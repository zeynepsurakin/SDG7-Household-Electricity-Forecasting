# Adım 5 – EPİAŞ Kaynak Bazlı Üretim ve Tarihsel Temiz Saat Analizi

## Neden yapıldı?
Yıldız Teknik Üniversitesi SDG7 elektrik tüketimi tahmin projesindeki "şebekenin yenilenebilir üretim payı yüksek saatler" önerisini somutlaştırmak. Bu adım, tüketim **tahmini değil**, Türkiye şebekesindeki **tarihsel üretim kaynağı karışımı** analizidir.

## Veri kaynağı ve kapsam
- `elektrik-uretim-saatlik.csv.gz` dosyası EnerjiVeri'nin EPİAŞ Şeffaflık Platformu'ndan derlediğini açıkladığı **üçüncü taraf arşivdir**.
- Dosyada **103.622 saatlik kayıt** vardır (13.11.2014–30.10.2026). 30.10.2026 gününün verileri tam olmadığından hariç bırakılmıştır.
- En son **30 tamamlanmış gün** (30.09.2026–29.10.2026) kullanılmıştır: **720 saat**.
- Kaynak kategorileri: barajlı HES, akarsu HES, rüzgâr, güneş, jeotermal ve biyokütle (yenilenebilir); doğalgaz, kömür ve diğer kaynaklar (diğer).
- Sütunlar **MW cinsinden saatlik ortalama üretim gücü** gösterir.

## Hesaplama

`renewable_pct = 100 × (barajlı HES + akarsu HES + rüzgâr + güneş + jeotermal + biyokütle) / (tüm listelenen kaynak kategorilerinin toplamı)`

**Veri kalitesi:** `toplam_mw` ile kaynak sütunlarının toplamı arasında son 30 günde ortalama **%1,39** fark ve en fazla **%4,96** fark bulundu. Payların tutarlı hesaplanması için payda olarak **listelenen kaynakların toplamı** kullanıldı; `toplam_mw` aynen korunarak karşılaştırma sütununda saklandı.

## Temel sonuç
- Seçilen dönem için toplam kaynak üretimindeki yenilenebilir payı (ağırlıklı): **%50,06**.
- Saatler içinde en yüksek 30-günlük ortalama yenilenebilir pay: **00.00 = %51,38**.
- Diğer uygun örnek saatler: **08.00 = %51,22**, **14.00 = %51,22**.
- En düşük ortalama: **21.00 = %48,64**.
- Saatlere göre küçük ortalama farklar, günler arasındaki değişkenliğin yanında kalabilir. Bunlar **ertesi günün kesin saatleri** değildir.

## Tasarruf ile birlikte gösterilen açıklayıcı senaryo
- **Varsayımsal** 1,2 kWh tüketen, **iki saatlik** bir faaliyetin **18.00–20.00** yerine **ertesi gün 00.00–02.00** aralığına kaydırıldığını düşünelim.
- Türkiye 4 Nisan 2026 tarihli EPDK üç zamanlı **aktif enerji bedeli** tarife CSV'si uygulandığında: **4,497 TL → 0,616 TL**; fark **3,881 TL** / çalıştırma (dağıtım ve vergi toplamı değil).
- Aynı iki tarihsel saat çiftinin ortalama yenilenebilir kaynak payı **%49,17 → %51,29**; **+2,12 yüzde puan**.
- Gece çalışması uygun değilse, **08.00–10.00** saat çiftinin yenilenebilir payı ortalaması **%51,18**, 1,2 kWh için örnek aktif enerji bedeli **2,341 TL**. Hangi saatlerin kullanılabilir olduğu kullanıcı kısıtlarıyla belirlenmelidir.

## Dosyalar
- `epias_clean_hours_analysis.py`: Baştan sona tekrarlanabilir veri doğrulama ve analiz kodu.
- `SDG7_Adim5_EPIAS_Colab.ipynb`: Colab notebook; iki input dosyasını sol panelden yüklemeniz yeterli.
- `EPIAS_Sonuclar/hourly_clean_hours_profile.csv`: 24 saatlik profil ve tarifeler.
- `EPIAS_Sonuclar/historical_ranked_hours.csv`: Tarihsel saatlerin yenilenebilir pay sıralaması.
- `EPIAS_Sonuclar/candidate_2h_schedules.csv`: 24 olası iki saatlik başlangıç ve örnek enerji maliyeti.
- `EPIAS_Sonuclar/illustrative_shift_18_to_00.csv`: Senaryo hesabı.
- `EPIAS_Sonuclar/daily_renewable_share.csv`: 30 günlük karşılaştırma.
- `EPIAS_Sonuclar/selected_30_days_source_mix.csv`: Ara hesap ve kaynak veri alt kümesi.
- `EPIAS_Sonuclar/*.png`: Sunuma konulabilir görseller.
- `EPIAS_Sonuclar/validation_summary.json`: Veri kalite özeti.

## Bilimsel sınırlılıklar
1. Yenilenebilir kaynak payı **karbon yoğunluğu / marjinal CO₂ emisyonu** değildir; "karbon tasarrufu" nicel olarak **hesaplanmadı**.
2. Veriler geçmiş günlere aittir. Ertesi günün gerçek üretim dağılımı için ayrıca üretim tahmini gerekir.
3. Hane cihaz verisi yoktur. Cihaz saatleri ve 1,2 kWh tüketimi yalnızca **örnek senaryodur**.
4. Türkiye EPDK tarife senaryosu, Londra/Fransa hanelerinden elde edilen tarihsel tüketim tahminleriyle eş zamanlı ölçüm değildir.
5. EPİAŞ'ın toptan **PTF değeri**, EPDK üç zamanlı **mesken tarife fiyatı değildir**. PTF dosyası bu paketin girdisi değildir.
6. Üç zamanlı tarifedeki saatler, sayaç ayarına ve abonelik türüne göre doğrulanmalıdır.

## Kaynaklar
- Türkiye üretim kaynağı arşivi (EPİAŞ verisinden türeten üçüncü taraf): https://enerjiveri.com/elektrik/uretim-tarihce/
- EPİAŞ Şeffaflık: https://seffaflik.epias.com.tr/
- EPDK tarife tabloları: https://www.epdk.gov.tr/Detay/Icerik/3-1327/elektrik-faturalarina-esas-tarife-tablolari
