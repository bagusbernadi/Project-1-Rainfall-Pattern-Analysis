"""Membangun results/3-presentation/analysis.ipynb (grafik dari results/*/*.csv; angka insight dihitung di sel kode)."""
import nbformat as nbf
import sys as _sys, pathlib as _pl; _sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[2]))  # project/code (common.py)
from common import RES_PRESENT, RES_PREP, RES_ANALYSIS

nb = nbf.v4.new_notebook()
C = lambda s: nb.cells.append(nbf.v4.new_code_cell(s.strip()))
M = lambda s: nb.cells.append(nbf.v4.new_markdown_cell(s.strip()))

M("# Rainfall Pattern Analysis (weatherAUS)\nGrafik dan insight dibaca dari `results/*/*.csv` hasil pipeline SQL. Hari hujan = RainToday = Yes (Rainfall > 1,0 mm). Semua angka ketepatan aturan bersifat **estimated** (in-sample).")
C("""
import pandas as pd, matplotlib.pyplot as plt
plt.rcParams.update({'figure.dpi':100,'axes.spines.top':False,'axes.spines.right':False,'font.size':10})
O='../2-analysis/'; P='../1-data-preparation/'; BLUE,ORANGE='#2a78d6','#eb6834'
kpi=pd.read_csv(O+'kpi_overall.csv').set_index('kpi_id')
print(kpi[['kpi','value','n']].to_string())
""")
M("## 1. Pola waktu (Q1-Q3)")
C("""
m=pd.read_csv(O+'rain_by_month.csv')
h=m.pivot(index='Location',columns='month',values='pct_rain')
z=m.drop_duplicates('Location').set_index('Location')['climate_zone']
h=h.loc[z.sort_values(kind='stable').index]
fig,ax=plt.subplots(figsize=(8,10)); im=ax.imshow(h.values,cmap='Blues',aspect='auto')
ax.set_xticks(range(12)); ax.set_xticklabels(h.columns); ax.set_yticks(range(len(h))); ax.set_yticklabels([f'{l} ({z[l]})' for l in h.index],fontsize=7)
fig.colorbar(im,label='% hari hujan'); ax.set_title('Persentase hari hujan per lokasi x bulan'); plt.show()
""")
C("""
zs=pd.read_csv(O+'rain_by_zone_season.csv').pivot(index='climate_zone',columns='season',values='pct_rain')[['Summer','Autumn','Winter','Spring']]
zs.plot.bar(figsize=(8,4),color=['#2a78d6','#7fb2ec','#1c4f94','#bcd6f5']); plt.ylabel('% hari hujan'); plt.title('Per zona iklim x musim'); plt.xticks(rotation=20); plt.show()
sw=(zs.max(axis=1)-zs.min(axis=1)).sort_values(ascending=False)
print('Selisih musim terbasah - terkering (poin) per zona:'); print(sw.round(1).to_string())
""")
C("""
t=pd.read_csv(O+'rain_trend_year.csv')
plt.figure(figsize=(7,3.5)); plt.plot(t.year,t.pct_rain,marker='o',color=BLUE); plt.ylim(0,40); plt.ylabel('% hari hujan')
plt.title(f"Tren 2009-2016 ({int(t.n_locations.iloc[0])} lokasi panel seimbang)"); plt.show()
print('Rentang tahunan:',t.pct_rain.min(),'-',t.pct_rain.max(),'(tidak ada uji signifikansi; 8 titik)')
""")
M("## 2. Lokasi (Q4-Q5): frekuensi vs jumlah hujan")
C("""
l=pd.read_csv(O+'location_ranking.csv')
fig,ax=plt.subplots(figsize=(6,5)); ax.scatter(l.pct_rain,l.est_annual_mm,color=BLUE)
for _,r in l[(l.rank_pct_rain<=3)|(l.rank_annual_mm<=3)|(l.est_annual_mm<300)].iterrows(): ax.annotate(r.Location,(r.pct_rain,r.est_annual_mm),fontsize=8,xytext=(4,2),textcoords='offset points')
ax.set_xlabel('% hari hujan'); ax.set_ylabel('Perkiraan curah tahunan (mm, estimated)'); plt.show()
top=l.nsmallest(3,'rank_pct_rain'); print('Terbanyak hari hujan:',', '.join(f'{r.Location} ({r.pct_rain}%)' for r in top.itertuples()))
top=l.nsmallest(3,'rank_annual_mm'); print('Curah terbesar:',', '.join(f'{r.Location} ({int(r.est_annual_mm)} mm)' for r in top.itertuples()))
print('Korelasi peringkat (Spearman):',round(l.rank_pct_rain.corr(l.rank_annual_mm),2))
""")
M("## 3. Kondisi cuaca sebelum hujan (Q6-Q9)")
C("""
d=pd.read_csv(O+'conditions_diff.csv'); print(d.to_string(index=False))
w=pd.read_csv(O+'wind_gust_dir.csv').sort_values('pct_rain_tomorrow')
plt.figure(figsize=(6,4)); plt.barh(w.WindGustDir,w.pct_rain_tomorrow,color=BLUE); plt.xlabel('% hujan besok'); plt.title('Arah hembusan angin vs hujan besok'); plt.show()
""")
M("## 4. Aturan peringatan (Q10-Q11)")
C("""
p=pd.read_csv(O+'persistence.csv'); a=p[p.Location=='ALL'].iloc[0]
print(f'P(hujan besok | hari ini hujan)={a.p_rain_tomorrow_if_rain_today}%, | tidak hujan={a.p_rain_tomorrow_if_dry_today}%, rasio={a.ratio}')
r=pd.read_csv(O+'rule_thresholds.csv')
fig,ax=plt.subplots(1,2,figsize=(10,3.6))
ax[0].plot(r.threshold,r.accuracy,marker='o',color=BLUE,label='Akurasi aturan'); ax[0].plot(r.threshold,r.baseline_accuracy,color=ORANGE,label='Baseline selalu tidak hujan'); ax[0].legend(); ax[0].set_xlabel('Ambang Humidity3pm'); ax[0].set_ylabel('%')
ax[1].plot(r.threshold,r.recall,marker='o',color=BLUE,label='Recall'); ax[1].plot(r.threshold,r.warn_pct,color=ORANGE,label='Hari bertanda peringatan'); ax[1].legend(); ax[1].set_xlabel('Ambang Humidity3pm')
plt.tight_layout(); plt.show()
x=r[r.threshold==70].iloc[0]
print(f'Ambang 70 (ditetapkan di awal): akurasi {x.accuracy}% vs baseline {x.baseline_accuracy}% (+{100*(x.tp+x.tn)/x.n_eval-100*(x.fp+x.tn)/x.n_eval:.1f} poin), recall {x.recall}%, peringatan {x.warn_pct}% hari (estimated, in-sample)')
print('Ambang yang melampaui baseline:',list(r[r.accuracy>r.baseline_accuracy].threshold))
""")
M("## 5. Kualitas data dan sensitivitas (Q13-Q15)")
C("""
mc=pd.read_csv(P+'missing_concentration.csv').head(8); print(mc[['column_name','null_pct','locations_never_recording','share_of_nulls_in_top5_locations_pct']].to_string(index=False))
s=pd.read_csv(O+'sensitivity.csv'); print(s[['metric','dropna_A','impute_B','rel_diff_pct','flag_review']].to_string(index=False))
c=pd.read_csv(O+'crosscheck.csv'); print('\\nCrosscheck SQL vs pandas:',(c.status=='PASS').sum(),'/',len(c),'PASS')
""")
nbf.write(nb, RES_PRESENT / "analysis.ipynb")
