S=[("Definisi dan aturan","dokumen definisi",0),("Struktur tabel","kamus data",0),
("Unduh dan profiling","ringkasan profiling",0),("Audit nilai kosong","missing_audit",1),("Tabel bersih ke DuckDB","file database",0),
("Frekuensi hujan","Q1–Q5",1),("Kondisi cuaca","Q6–Q9",0),("Peluang dan ambang","Q10–Q11",0),("Cek silang SQL–pandas","Q15",0),("Uji sensitivitas","Q14",0),
("Dashboard","Q12 dan filter",1),("README dan finalisasi","repo siap ditinjau",0)]
P=[("A","Perencanaan","--navyH",[0,1]),("B","Menyiapkan data","--tealH",[2,3,4]),("C","Menghitung dan menganalisis","--plumH",[5,6,7,8,9]),("D","Menyajikan","--roseH",[10,11])]
lanes=[]
for L_,name,col,idx in P:
    bx=''.join(f'<div class="wb{" L" if S[i][2] else ""}"><span class="n">{i+1}</span><b>{S[i][0]}</b><span class="s">{S[i][1]}</span></div>' for i in idx)
    lanes.append(f'<div class="wl" style="--c:var({col})"><h4>Tahap {L_} · {name}</h4><div class="ws" style="--k:{len(idx)}">{bx}</div></div>')
block='<h3>Alur tahapan kerja</h3>\n<div class="card"><div class="wf">'+'<div class="wrow">'+lanes[0]+lanes[1]+'</div>'+lanes[2]+lanes[3]+'</div>\n<p style="text-align:center;margin:8px 0 0">Panah menunjukkan urutan pengerjaan. Angka di kotak sama dengan nomor langkah di bawah.</p></div>\n\n'
s=open('body.html',encoding='utf8').read()
ph=s.index('<div class="phases">')
if '<h3>Alur tahapan kerja</h3>' in s:
    s=s[:s.index('<h3>Alur tahapan kerja</h3>')]+s[ph:]
assert s.count('<div class="phases">')==1 and s.count('Alur tahapan kerja')==0
s=s.replace('<div class="phases">',block+'<div class="phases">')
open('body.html','w',encoding='utf8').write(s)
css='''.row .bl{position:absolute;top:0;bottom:0;width:2px;background:var(--roseH);z-index:1}
.row .n{width:100px}
.figw .arN{fill:none;stroke:var(--bar);stroke-width:2}
.tag.c1{background:#188038;color:#fff}.tag.c2{background:#9334E6;color:#fff}.tag.c3{background:#D93025;color:#fff}.tag.c4{background:#fff;color:#174EA6}
.wf{display:grid;gap:30px;margin:6px 0}.wl{--c:var(--navyH);position:relative;border-radius:14px;padding:14px 16px;background:color-mix(in srgb,var(--c) 8%,var(--card));border:1px solid color-mix(in srgb,var(--c) 30%,var(--card))}
.wl:not(:last-child)::after{content:"\\2193";position:absolute;left:50%;bottom:-27px;transform:translateX(-50%);font-size:24px;font-weight:800;color:var(--bar);line-height:1}
.wl h4{margin:0 0 12px;font-size:15px;color:var(--c);text-transform:uppercase;letter-spacing:.06em}.ws{display:grid;gap:30px;grid-template-columns:1fr}
.wb{position:relative;background:var(--card);border:2px solid var(--c);border-radius:12px;padding:10px 12px 10px 54px;min-height:66px}.wb .n{position:absolute;left:12px;top:12px;width:30px;height:30px;border-radius:50%;background:var(--c);color:#fff;display:grid;place-items:center;font-weight:800;font-size:15px}
.wb b{display:block;font-size:16.5px;line-height:1.3}.wb .s{display:block;font-size:14px;line-height:1.4;margin-top:2px;color:var(--mut)}.wb.L::before{content:"beban besar";position:absolute;right:8px;top:-11px;background:var(--amber);color:var(--amber-ink);font-size:11.5px;font-weight:700;padding:1px 8px;border-radius:999px}
.wb:not(:last-child)::after{content:"\\2193";position:absolute;left:50%;bottom:-28px;transform:translateX(-50%);color:var(--bar);font-size:22px;font-weight:800;line-height:1}
@media (min-width:1200px){.ws{grid-template-columns:repeat(5,minmax(0,1fr));gap:36px}.wb:not(:last-child)::after{content:"\\2192";left:auto;right:-30px;bottom:auto;top:50%;transform:translateY(-50%)}}
.card a{color:var(--navy);font-weight:600}
.wrow{position:relative;display:grid;gap:30px}
.wrow::after{content:"\\2193";position:absolute;left:50%;bottom:-27px;transform:translateX(-50%);font-size:24px;font-weight:800;color:var(--bar);line-height:1}
@media (min-width:1200px){.wrow{grid-template-columns:2fr 3fr;gap:44px}.wrow .ws{grid-template-columns:repeat(var(--k),minmax(0,1fr))}.wrow .wl:first-child::after{content:"\\2192";left:auto;right:-36px;bottom:auto;top:50%;transform:translateY(-50%)}}
</style>'''
L=open('template.html',encoding='utf8').read().split('\n')
head0='\n'.join(L[:150]).replace('<title>Project 3: Yield, Rework &amp; Defect Tracking</title>','<title>Project 1: Rainfall Pattern Analysis</title>').replace('Rancangan project portofolio Data Analyst: sistem pelacakan yield, rework, dan defect produksi PLC Splitter dengan SQL dan dashboard.','Rancangan project portofolio Data Analyst: analisis pola hujan dataset weatherAUS tanpa machine learning dengan SQL, pandas, dan dashboard HTML.')
i=head0.rindex('</style>');head=head0[:i]+css+head0[i+len('</style>'):]
open('project_1_rainfall.html','w',encoding='utf8').write(head+'\n\n'+s+'\n<script>\n'+open('script.js',encoding='utf8').read()+'</script>\n\n</body></html>\n')

# index.html (GitHub Pages) = halaman + link kembali ke hub
h=open('project_1_rainfall.html',encoding='utf8').read()
a='</head><body>'
assert h.count(a)==1
back='<a href="https://bagusbernadi.github.io/" style="display:inline-block;margin:12px 16px;font:600 14px/1.4 \'Source Sans 3\',Arial,sans-serif;color:#1A73E8;text-decoration:none">\u2190 All projects / Semua project</a>'
open('../index.html','w',encoding='utf8').write(h.replace(a,a+back))
