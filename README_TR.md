# SDG 7 – Household Electricity Forecasting and Cost-Aware Scheduling

**30 Ekim 2026 teslim için geliştirme paketidir.** Mevcut GitHub projesine ilave olarak eklenen **deney ve sonuçları** içerir; orijinal repo ve model eğitimi yerine geçmez. Her deney farklı veri/ülke/dönem üzerinde yürütülmüştür.

## Hocanın geri bildirimine verilen yanıt

| İstek | Yapılan çalışma | Durum |
|---|---|---|
| Tek haneden çıkıp çok hanede test | London Smart Meters alt kümesi: 30 farklı hane saptandı, 12'si uzunluk filtresinden geçti; 9 eğitim, **3 tamamen görülmemiş test hanesi** | Tamamlandı (alt küme) |
| Ertesi gün tahminine odaklan | Saatlik tüketim için önceki gün ve daha eski tüketim gecikmeleri, ileri test tarihleri | Tamamlandı (test edilen model) |
| Hava durumu etkisi | Önceki günün hava verisiyle adil model karşılaştırması | Tamamlandı |
| EPDK üç zamanlı fatura hesabı | 4 Nisan 2026 tarihli, dönemi açık belirtilmiş tarife CSV'si ile model tahminlerine senaryo uygulaması | Tamamlandı (senaryo) |
| Saat kaydırmayla tasarruf önerisi | %0/%10/%20/%30 esnek yük senaryoları, ayrı örnek cihaz simülasyonu | Tamamlandı (varsayımsal) |
| EPİAŞ'tan üretim kaynağı ve temiz saatler | Üçüncü taraf EPİAŞ kaynaklı arşiv ile 30 tam gün, 720 saatlik profil; hidro/rüzgâr/güneş/jeotermal/biyokütle | Tamamlandı (tarihsel analiz) |
| EPİAŞ saatlik PTF analizi | Henüz paket kapsamında indirilmedi | Geliştirme |
| SDG 13 ve gerçek CO₂ tasarrufu | Yenilenebilir üretim payı göstergesi eklendi, CO₂ emisyonu hesaplanmadı | Kavramsal bağlantı, nicel test yok |
| Grup 13'ten ayrışma | Sonraki saat yerine ertesi gün, tarife, esnek yük ve karar önerisi | Açıkça tanımlandı |

## 1. İlk model ve EPDK senaryosu — Fransa tek hane

Özgün Random Forest değerlendirmesi: **MAE 0,4205 kWh, RMSE 0,5827 kWh**. 216 seçili tam test gününün 5.315,83 kWh tahmini tüketimi kullanıldı. **%20 esnek yük** varsayımında kaydırma öncesi **27.412,53 TL**, sonrası **26.301,90 TL**; fark **1.110,63 TL (%4,05)**. Bunlar **gerçek fatura ve ölçülmüş tasarruf değildir**. Fiyatlar 2026 Türkiye EPDK tarihli, tüketim ise 2010 Fransa verisidir; 216 gün ardışık fatura dönemi değildir.

## 2. London Smart Meters – görülmemiş hane

9 eğitim hanesi, 3 eğitimde görülmeyen test hanesi, 135.956 eğitim / 11.495 test gözlemi, zaman kesimi 19.09.2013. Sonuç: **Random Forest MAE 0,202609 kWh, RMSE 0,340148 kWh**; önceki gün baseline **0,230553 kWh**, önceki hafta **0,240448 kWh**. Hata, eğitimde görülmemiş hanelerde ölçüldü. Fransa veri setiyle sonuçlar **doğrudan kıyaslanmamalıdır**.

## 3. Hava durumu özelliklerinin etkisi

Aynı London test hanelerinde: sadece gecikmeli tüketimle **MAE 0,202680**, önceki günün gerçek hava bilgisi eklendiğinde **0,205649**. Hava, bu veri ve kurulumda **hata azaltmadı**. Bu sonuç ertesi günün gerçekleşmiş hava verisini önceden biliyormuş gibi kullanmaz.

## 4. Türkiye kaynak bazlı üretim ve tarihsel çevresel tercih

EnerjiVeri EPİAŞ kaynağından türetilmiş arşivin 30.09–29.10.2026 arası **30 tam gün / 720 saat** alt kümesi. Yenilenebilir payı listelenen 15 üretim kaynağının toplamına göre hesaplandı. Saatlik ortalama en yüksek pay **00:00 %51,38**, en düşük **21:00 %48,64**. Saatler arasındaki farkın belirsizliği yüksektir. Tarihsel % yenilenebilir payını **gerçek marjinal karbon salımı** diye sunmayın.

Varsayımsal iki saatlik 1,2 kWh'lık faaliyeti 18:00–20:00'dan ertesi gün 00:00–02:00'a kaydırmak, 4 Nisan 2026 tarihli EPDK **aktif enerji fiyatları** altında **3,881 TL/çalıştırma** enerji bedeli farkı; iki tarihsel saat çiftinde **+2,12 yüzde puan** yenilenebilir kaynak payı farkı verir. Gerçek cihaz veya karbon tasarrufu ölçümü değildir.

## Repo ve teslimde ne yapılmalı?

1. **Mevcut GitHub projesini silmeyin.** Bu paketlerdeki alt klasörleri yeni `experiments/` klasörünün altında ekleyin.
2. Notebook'lar, CSV metrikler, PNG grafikler ve ilgili `methodology` notları birlikte kalmalı.
3. Rapor başlığı: **Day-Ahead Household Electricity Forecasting and Cost-Aware Load Scheduling under Turkish Time-of-Use Tariffs**.
4. Deneyleri ülke ve dönem olarak açıkça ayırın: **2010 Fransa tüketimi / 2013 Londra tüketimi / 2026 Türkiye tarifesi / 2026 Türkiye kaynak dağılımı**.
5. "Savings" sonucu yanında **simulated**; temiz saat grafiği yanında **historical renewable share** yazın.
6. Tam fiziksel karbon hesabı ve cihaz bazlı deney yapılmadığını "Limitations / Future Work" bölümüne ekleyin.
7. EPİAŞ **PTF fiyatları toptan fiyatlardır**; EPDK perakende mesken tarifesine doğrudan ikame edilemez.

## Çalıştırma

- Her aşamada ilgili `.ipynb` notebook'undan ilerleyin.
- `04_EPIAS_Renewable_and_Scheduling/` klasörü dahilindeki `.csv.gz`, `epdk_tariff_2026_04_04.csv` ve `epias_clean_hours_analysis.py` aynı klasördeyken `python epias_clean_hours_analysis.py` komutu tüm analizi yeniden oluşturur.
- Test edilen sonuç CSV'lerini PDF/rapor için tablolaştırın; tüm ağır ham verileri GitHub'a yüklemek zorunda değilsiniz.

## Kaynaklar

- GitHub çalışma başlangıcı: https://github.com/brkarsln4/SDG7-Household-Electricity-Forecasting
- London Smart Meters: https://data.london.gov.uk/dataset/smartmeter-energy-consumption-data-in-london-households-vqm0d
- EnerjiVeri EPİAŞ tarihçe arşivi: https://enerjiveri.com/elektrik/uretim-tarihce/
- EPİAŞ Şeffaflık: https://seffaflik.epias.com.tr/
- EPDK tarife tabloları: https://www.epdk.gov.tr/Detay/Icerik/3-1327/elektrik-faturalarina-esas-tarife-tablolari
