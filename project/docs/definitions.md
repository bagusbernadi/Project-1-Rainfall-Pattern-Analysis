# Definisi

## Hari hujan
`RainToday = Yes`, yaitu Rainfall > 1,0 mm (diverifikasi cocok pada seluruh 142.199 baris terisi; 1.759 hari dengan Rainfall tepat 1,0 mm semuanya "No").
Penyebut persentase = hari dengan RainToday terisi. Baris kosong tidak dihitung dan tidak diisi.
Persentase memakai poin persen (2 desimal di tabel, dibulatkan di tampilan).

## Musim (belahan bumi selatan)
Summer = Des-Feb, Autumn = Mar-Mei, Winter = Jun-Agu, Spring = Sep-Nov.
Zona Tropis utara dibaca juga sebagai musim basah (Nov-Apr) dan kering (Mei-Okt).

## Zona iklim (`data/reference/dim_location.csv`)
5 zona, ditentukan manual berdasarkan pengetahuan umum letak/iklim, bukan klasifikasi resmi:
Tropis utara (4), Pesisir timur (13), Tenggara sedang (18), Barat daya (6), Pedalaman kering (8).
NorfolkIsland ditaruh di Pesisir timur sebagai pendekatan. Batasan: pembagian zona subjektif dan bisa diubah; hasil per zona ikut berubah.

## KPI (`sql/06_kpi.sql`, dihitung ulang di dashboard sesuai filter)
| ID | Rumus |
|---|---|
| K1 | Frekuensi hari hujan (%) = hari RainToday=Yes / hari RainToday terisi x 100 |
| K2 | Curah rata-rata per hari hujan (mm) = rata-rata Rainfall pada hari hujan |
| K3 | Selisih Humidity3pm = rata-rata (RainTomorrow=Yes) - rata-rata (RainTomorrow=No), poin % |
| K4 | Rasio peluang = P(hujan besok / hari ini hujan) / P(hujan besok / hari ini tidak hujan) |
| K5 | Recall aturan Humidity3pm >= 70 = hari hujan besok yang diberi peringatan / seluruh hari hujan besok |

## Tren tahunan (Q3), panel seimbang
Tahun 2009-2016. Lokasi-tahun dianggap lengkap jika RainToday terisi >= 90% hari. Hanya lokasi yang lengkap di kedelapan tahun dipakai (30 lokasi), supaya perubahan tidak berasal dari lokasi yang masuk/keluar. Tidak ada uji signifikansi.

## Aturan peringatan (Q11)
Peringatan jika Humidity3pm >= ambang (40-90, langkah 5). Pembanding (baseline) = selalu menebak "besok tidak hujan". Evaluasi pada baris yang sama dengan yang dipakai membaca pola (in-sample, tanpa data uji), jadi semua angka ketepatan berlabel **estimated**.
Ambang KPI 5 ditetapkan di awal = 70, tidak dipilih dari hasil terbaik.

## Guard sampel kecil
Rasio/recall tidak ditampilkan jika n < 30 (`MIN_N` di dashboard).
