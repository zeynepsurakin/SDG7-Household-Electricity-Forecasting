"""SDG7 / Step 5 – EPİAŞ-derived hourly source mix, via EnerjiVeri archive.

No web calls. Inputs:
  elektrik-uretim-saatlik.csv.gz
  epdk_tariff_2026_04_04.csv
Outputs are placed in EPIAS_Sonuclar/.

This is a HISTORICAL 30-full-day renewable-share profile, NOT a real-time
forecast or a model of marginal CO2 emissions.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = Path.cwd()
GEN = BASE / 'elektrik-uretim-saatlik.csv.gz'
TARIFF = BASE / 'epdk_tariff_2026_04_04.csv'
OUT = BASE / 'EPIAS_Sonuclar'
OUT.mkdir(exist_ok=True)
RENEWABLE = ['barajli_hes', 'akarsu', 'ruzgar', 'gunes', 'jeotermal', 'biyokutle']
FOSSIL = ['dogalgaz','ithal_komur','linyit','tas_komur','fuel_oil','asfaltit','lng','nafta']
NON_RENEWABLE_OTHER = ['atik_isi']
SOURCE_COLS = RENEWABLE + FOSSIL + NON_RENEWABLE_OTHER

if not GEN.exists():
    raise FileNotFoundError(f'CSV bulunamadı: {GEN}. Colab Dosyalar panelinden yükleyin.')
raw = pd.read_csv(GEN, compression='gzip')
needed = ['tarih','saat','toplam_mw'] + SOURCE_COLS
missing = [c for c in needed if c not in raw.columns]
if missing: raise ValueError(f'Eksik sütunlar: {missing}')
raw['tarih'] = pd.to_datetime(raw['tarih'], format='%Y-%m-%d', errors='coerce')
raw['saat'] = pd.to_numeric(raw['saat'], errors='coerce')
for c in ['toplam_mw']+SOURCE_COLS:
    raw[c] = pd.to_numeric(raw[c],errors='coerce')
valid_rows = raw.dropna(subset=needed).copy()
valid_rows = valid_rows[valid_rows.saat.between(0,23)]
valid_rows = valid_rows[valid_rows.toplam_mw>0]
valid_rows = valid_rows[~valid_rows.duplicated(['tarih','saat'])]
# Use 30 most recent COMPLETE calendar days (not necessarily consecutive).
day_counts = valid_rows.groupby('tarih')['saat'].nunique()
full_dates = day_counts[day_counts==24].index.sort_values()
window = full_dates[-30:]
if len(window) < 30: raise ValueError('Yeterli tam gün yok.')
df = valid_rows[valid_rows.tarih.isin(window)].copy()
# Latest selected days in this archive have no negative source entries; if future
# input contains negatives, surface a validation error rather than silently fix.
neg = int((df[SOURCE_COLS] < 0).sum().sum())
if neg:
    raise ValueError(f'Son 30 günde {neg} negatif kaynak üretimi var, incelenmeli.')
df['source_sum_mw'] = df[SOURCE_COLS].sum(axis=1)
df = df[df.source_sum_mw>0].copy()
df['renewables_mw'] = df[RENEWABLE].sum(axis=1)
df['nonrenewable_mw'] = df[FOSSIL+NON_RENEWABLE_OTHER].sum(axis=1)
df['renewable_pct'] = 100*df.renewables_mw/df.source_sum_mw
df['residual_pct'] = 100*(df.source_sum_mw - df.toplam_mw)/df.toplam_mw

def period(h):
    if 6 <= h < 17: return 'Gunduz'
    if 17 <= h < 22: return 'Puant'
    return 'Gece'

profile = (
    df.groupby('saat',as_index=False)
    .agg(n_hours=('renewable_pct','size'),
         renewable_average_pct=('renewable_pct','mean'),
         renewable_median_pct=('renewable_pct','median'),
         renewable_q10_pct=('renewable_pct',lambda x:x.quantile(0.10)),
         renewable_q90_pct=('renewable_pct',lambda x:x.quantile(0.90)),
         renewable_sum_mw=('renewables_mw','sum'),
         sources_sum_mw=('source_sum_mw','sum'))
)
profile['renewable_weighted_pct'] = 100*profile.renewable_sum_mw/profile.sources_sum_mw
profile['tariff_period'] = profile.saat.map(period)
if TARIFF.exists():
    tariff = pd.read_csv(TARIFF)
    required = ['period','energy_tl_per_kwh','distribution_tl_per_kwh']
    if not set(required).issubset(tariff.columns):
        raise ValueError(f'Tarife CSV sütunları eksik: {set(required)-set(tariff.columns)}')
    profile = profile.merge(tariff[required],left_on='tariff_period',right_on='period',how='left',validate='many_to_one').drop(columns='period')
    if profile.energy_tl_per_kwh.isna().any(): raise ValueError('Tarife eşleştirme hatası')
else:
    profile['energy_tl_per_kwh']=np.nan
    profile['distribution_tl_per_kwh']=np.nan

# CSV of 720 individual hour observations, allowing independent rechecks.
ex = df[['tarih','saat','source_sum_mw','toplam_mw','renewables_mw','renewable_pct','residual_pct']+RENEWABLE].copy()
ex['tarih']=ex.tarih.dt.strftime('%Y-%m-%d')
ex.round(6).to_csv(OUT/'selected_30_days_source_mix.csv',index=False)
profile.round(6).to_csv(OUT/'hourly_clean_hours_profile.csv',index=False)

# Ranked by average per-hour historical share; small differences are NOT predictions.
ranking = profile.sort_values('renewable_average_pct',ascending=False).copy()
ranking[['saat','renewable_average_pct','renewable_q10_pct','renewable_q90_pct','tariff_period','energy_tl_per_kwh']].round(4).to_csv(OUT/'historical_ranked_hours.csv',index=False)

# Illustrative adjustable two-hour 1.2 kWh cycle: 18-20 -> next day 00-02.
# Appliance consumption is a chosen hypothetical example, not disaggregated metering.
orig_hours=[18,19]; dest_hours=[0,1]; cycle_energy_kwh=1.2
lookup = profile.set_index('saat')
old_share=float(lookup.loc[orig_hours,'renewable_average_pct'].mean())
new_share=float(lookup.loc[dest_hours,'renewable_average_pct'].mean())
example = {
    'scenario':'Illustrative two-hour appliance load; NOT verified appliance-level data',
    'load_kwh':cycle_energy_kwh,
    'original_start':'18:00', 'original_end':'20:00',
    'proposed_start':'next day 00:00','proposed_end':'next day 02:00',
    'historical_source_share_original_pct':old_share,
    'historical_source_share_proposed_pct':new_share,
    'historical_source_share_difference_pp':new_share-old_share,
}
if profile.energy_tl_per_kwh.notna().all():
    old_cost=cycle_energy_kwh/2*lookup.loc[orig_hours,'energy_tl_per_kwh'].sum()
    new_cost=cycle_energy_kwh/2*lookup.loc[dest_hours,'energy_tl_per_kwh'].sum()
    example.update({'tariff_snapshot':'2026-04-04 EPDK (from CSV)',
                    'energy_only_original_tl':float(old_cost),
                    'energy_only_proposed_tl':float(new_cost),
                    'energy_only_difference_tl':float(old_cost-new_cost),
                    'full_bill_difference_verified':False})
pd.DataFrame([example]).to_csv(OUT/'illustrative_shift_18_to_00.csv',index=False)

# Decision-support prototype: all potential TWO-HOUR start times.
# User must provide actual flexible activity and valid permitted windows.
windows=[]
for h in range(24):
    hours=[h,(h+1)%24]
    line={
        'start_hour':h,'end_hour_exclusive':(h+2)%24,
        'historical_average_renewable_pct':float(lookup.loc[hours,'renewable_average_pct'].mean()),
        'time_windows':' / '.join(lookup.loc[hours,'tariff_period'].astype(str).tolist()),
        'available_if_daytime_only': bool(h>=6 and h+2<=22),
        'load_kwh':cycle_energy_kwh,
    }
    if profile.energy_tl_per_kwh.notna().all():
        line['energy_only_cost_tl']=float(cycle_energy_kwh/2*lookup.loc[hours,'energy_tl_per_kwh'].sum())
    windows.append(line)
windows_df=pd.DataFrame(windows)
windows_df.sort_values('start_hour').round(5).to_csv(OUT/'candidate_2h_schedules.csv',index=False)

# Monthly story: how historical renewable mix changes by day, not a time forecast.
daily = df.groupby('tarih',as_index=False).agg(ren=('renewables_mw','sum'),all_sources=('source_sum_mw','sum'),n=('saat','size'))
daily['renewable_pct']=100*daily.ren/daily.all_sources
daily['tarih']=daily.tarih.dt.strftime('%Y-%m-%d')
daily.round(5).to_csv(OUT/'daily_renewable_share.csv',index=False)

# plots
plt.figure(figsize=(11.3,5))
plt.plot(profile.saat,profile.renewable_average_pct,marker='o',label='Historical mean renewable source share')
plt.fill_between(profile.saat,profile.renewable_q10_pct,profile.renewable_q90_pct,alpha=0.16,label='10–90 percentile across 30 days')
plt.xticks(range(24));plt.xlim(0,23);plt.xlabel('Hour (Türkiye local hour labels in source)')
plt.ylabel('Renewables / sum of listed generation sources (%)')
plt.title('Türkiye: hourly renewable-share pattern, 30 complete days ending 2026-10-29')
plt.grid(alpha=0.18);plt.legend(loc='best');plt.tight_layout()
plt.savefig(OUT/'renewable_profile_last30d.png',dpi=180);plt.close()

plt.figure(figsize=(11.3,5))
plt.plot(profile.saat,profile.renewable_average_pct,marker='o',label='Historical mean renewable share (%)')
plt.axhline(float(profile.renewable_average_pct.mean()),linestyle='--',alpha=0.6,label='24-hour mean')
for h in [0,8,14,18,21]:
    p=profile.set_index('saat').loc[h,'renewable_average_pct']
    plt.annotate(f'{h:02d}:00  {p:.1f}%',(h,p),xytext=(0,9 if h%2 else -19),textcoords='offset points',ha='center',fontsize=8)
plt.xticks(range(24));plt.xlabel('Hour of day');plt.ylabel('Historical renewable share (%)')
plt.title('Clean-hour screening: small mean differences, substantial daily variation')
plt.grid(alpha=.2);plt.tight_layout();plt.savefig(OUT/'historical_clean_hour_candidates.png',dpi=180);plt.close()

# Methodology card for uploading to GitHub and explaining limitations.
notes=f'''# SDG7 – Step 5: EPİAŞ-source-based historical renewable mix analysis\n\n'''+f'''Input: `elektrik-uretim-saatlik.csv.gz` from EnerjiVeri EPİAŞ archive (third-party mirror).\n\n'''+f'''Data: {len(raw):,} raw records, {raw.tarih.min():%Y-%m-%d} to {raw.tarih.max():%Y-%m-%d}; latest date may be incomplete.\n\n'''+f'''Selected: {len(window)} complete recorded days, {window.min():%Y-%m-%d} through {window.max():%Y-%m-%d}, {len(df)} hour observations.\n\n'''+'''Formula: renewable_pct = (dam hydro + river hydro + wind + solar + geothermal + biomass) / sum(all listed source categories) * 100.\n\n'''+f'''During the selected 30 days, `total_mw` and the sum of source columns differ: mean signed discrepancy {df.residual_pct.mean():.2f}%, largest absolute discrepancy {df.residual_pct.abs().max():.2f}%. Therefore the denominator for source mix is explicitly the sum of the listed sources, rather than `total_mw`.\n\n'''+f'''Highest historical mean share: {int(ranking.iloc[0].saat):02d}:00, {ranking.iloc[0].renewable_average_pct:.2f}% of listed sources; next best hours are close. Lowest: {int(ranking.iloc[-1].saat):02d}:00, {ranking.iloc[-1].renewable_average_pct:.2f}%. These are NOT tomorrow's verified or forecast values.\n\n'''+f'''Illustrative two-hour cycle: 1.2 kWh shifted from 18:00–20:00 to NEXT DAY 00:00–02:00. Historical source mix {old_share:.2f}% -> {new_share:.2f}% (+{new_share-old_share:.2f} percentage points). This does not establish a carbon reduction.\n\n'''+('The cost difference in `illustrative_shift_18_to_00.csv` uses the provided dated 2026-04-04 EPDK retail TOU tariff and excludes taxes/other full-bill effects. It is illustrative, not a verified household bill or appliance-level behavior.\n\n' if TARIFF.exists() else 'No tariff file supplied; only renewable generation shares were analyzed.\n\n')+'''Critical limitations:\n- Source data are an EPİAŞ-derived third-party mirror, NOT an official EPİAŞ download.\n- Observed hourly generation source share is not marginal-grid CO2 intensity or an emissions estimate.\n- No future generation forecasts; past 30-day profile cannot guarantee tomorrow's best hour.\n- Historical month/day/season matter, so ranking changes across samples.\n- `gunes` in this source may not include all rooftop/unlicensed installations.\n- No device-level measurements; appliance example is a scenario only.\n- London 2013 demand, France 2010 demand, 2026 Turkish costs and Turkish supply are from different places/times; don't claim one integrated measured validation.\n- EPİAŞ hourly PTF prices are NOT the same as household retail electricity prices.\n\nSources:\n- https://enerjiveri.com/elektrik/uretim-tarihce/\n- https://seffaflik.epias.com.tr/\n- https://www.epdk.gov.tr/Detay/Icerik/3-1327/elektrik-faturalarina-esas-tarife-tablolari\n'''
(OUT/'methodology_notes.md').write_text(notes,encoding='utf-8')

quality={
    'raw_rows':int(len(raw)), 'raw_min_date':str(raw.tarih.min().date()),'raw_max_date':str(raw.tarih.max().date()),
    'selected_first_date':str(window.min().date()),'selected_last_date':str(window.max().date()),
    'selected_complete_days':len(window),'selected_hour_rows':len(df),
    'selected_raw_total_source_sum_mean_residual_pct':round(float(df.residual_pct.mean()),4),
    'selected_raw_total_source_sum_max_abs_residual_pct':round(float(df.residual_pct.abs().max()),4),
    'selected_renewable_weighted_pct':round(float(100*df.renewables_mw.sum()/df.source_sum_mw.sum()),4),
    'selected_renewable_average_hourly_pct':round(float(df.renewable_pct.mean()),4),
    'max_hour':int(ranking.iloc[0].saat), 'max_hour_share_pct':round(float(ranking.iloc[0].renewable_average_pct),4),
    'min_hour':int(ranking.iloc[-1].saat), 'min_hour_share_pct':round(float(ranking.iloc[-1].renewable_average_pct),4),
}
(OUT/'validation_summary.json').write_text(json.dumps(quality,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(quality,indent=2,ensure_ascii=False))
print('Suggested load shift:',json.dumps(example,indent=2,ensure_ascii=False))
print('Output folder:',OUT)
