# SDG7 – Step 5: EPİAŞ-source-based historical renewable mix analysis

Input: `elektrik-uretim-saatlik.csv.gz` from EnerjiVeri EPİAŞ archive (third-party mirror).

Data: 103,622 raw records, 2014-11-13 to 2026-10-30; latest date may be incomplete.

Selected: 30 complete recorded days, 2026-09-30 through 2026-10-29, 720 hour observations.

Formula: renewable_pct = (dam hydro + river hydro + wind + solar + geothermal + biomass) / sum(all listed source categories) * 100.

During the selected 30 days, `total_mw` and the sum of source columns differ: mean signed discrepancy 1.39%, largest absolute discrepancy 4.96%. Therefore the denominator for source mix is explicitly the sum of the listed sources, rather than `total_mw`.

Highest historical mean share: 00:00, 51.38% of listed sources; next best hours are close. Lowest: 21:00, 48.64%. These are NOT tomorrow's verified or forecast values.

Illustrative two-hour cycle: 1.2 kWh shifted from 18:00–20:00 to NEXT DAY 00:00–02:00. Historical source mix 49.17% -> 51.29% (+2.12 percentage points). This does not establish a carbon reduction.

The cost difference in `illustrative_shift_18_to_00.csv` uses the provided dated 2026-04-04 EPDK retail TOU tariff and excludes taxes/other full-bill effects. It is illustrative, not a verified household bill or appliance-level behavior.

Critical limitations:
- Source data are an EPİAŞ-derived third-party mirror, NOT an official EPİAŞ download.
- Observed hourly generation source share is not marginal-grid CO2 intensity or an emissions estimate.
- No future generation forecasts; past 30-day profile cannot guarantee tomorrow's best hour.
- Historical month/day/season matter, so ranking changes across samples.
- `gunes` in this source may not include all rooftop/unlicensed installations.
- No device-level measurements; appliance example is a scenario only.
- London 2013 demand, France 2010 demand, 2026 Turkish costs and Turkish supply are from different places/times; don't claim one integrated measured validation.
- EPİAŞ hourly PTF prices are NOT the same as household retail electricity prices.

Sources:
- https://enerjiveri.com/elektrik/uretim-tarihce/
- https://seffaflik.epias.com.tr/
- https://www.epdk.gov.tr/Detay/Icerik/3-1327/elektrik-faturalarina-esas-tarife-tablolari
