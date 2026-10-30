import urllib.request, zipfile, csv, io, os, time, collections, math, statistics, json
UFS=['AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA','PB',
     'PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO']
BASE="https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb"
TS="261020260742"; TMP="ol_tmp"; os.makedirs(TMP,exist_ok=True)
# local key -> list of (section_id, L, F)
locals_=collections.defaultdict(list)
for uf in UFS:
    zp=os.path.join(TMP,f"{uf}.zip"); ok=False
    for _ in range(4):
        try: urllib.request.urlretrieve(f"{BASE}/bweb_2t_{uf}_{TS}.zip",zp); ok=True; break
        except Exception: time.sleep(3)
    if not ok: print("FALHA",uf,flush=True); continue
    z=zipfile.ZipFile(zp); name=[n for n in z.namelist() if n.endswith(".csv")][0]
    sec={}
    with z.open(name) as raw:
        r=csv.reader(io.TextIOWrapper(raw,encoding="latin-1",newline=""),delimiter=";")
        h=next(r); ix={c:i for i,c in enumerate(h)}
        iC=ix["DS_CARGO_PERGUNTA"];iM=ix["CD_MUNICIPIO"];iZ=ix["NR_ZONA"];iS=ix["NR_SECAO"]
        iL=ix["NR_LOCAL_VOTACAO"];iNm=ix["NM_VOTAVEL"];iTv=ix["DS_TIPO_VOTAVEL"];iV=ix["QT_VOTOS"]
        for row in r:
            if row[iC].strip().upper()!="PRESIDENTE": continue
            k=(uf,row[iM].strip(),row[iZ].strip(),row[iS].strip())
            d=sec.setdefault(k,{'loc':row[iL].strip(),'L':0,'F':0})
            nm=row[iNm].strip().upper()
            if nm=="LULA": d['L']=int(row[iV])
            elif nm=="FLAVIO BOLSONARO": d['F']=int(row[iV])
    for k,d in sec.items():
        lk=(uf,k[1],k[2],d['loc'])
        locals_[lk].append((k,d['L'],d['F']))
    z.close(); os.remove(zp); print(f"{uf} ok (locais {len(locals_)})",flush=True)

# z-score binomial de cada seção vs o pool do seu local
zs=[]  # (z, section, n, p_local, share_sec, lk, nsec_in_local)
big=[a for a in [3,4,5,6]]
cnt={b:{'+':0,'-':0} for b in big}
nsec=0
for lk,secs in locals_.items():
    if len(secs)<3: continue
    Lsum=sum(s[1] for s in secs); Fsum=sum(s[2] for s in secs)
    if Lsum+Fsum<100: continue
    p=Lsum/(Lsum+Fsum)
    if p<=0 or p>=1: continue
    for (sid,L,F) in secs:
        n=L+F
        if n<50: continue
        exp=n*p; sd=math.sqrt(n*p*(1-p))
        if sd==0: continue
        z=(L-exp)/sd
        zs.append(z); nsec+=1
        for b in big:
            if z>=b: cnt[b]['+']+=1
            elif z<=-b: cnt[b]['-']+=1

from statistics import NormalDist
N=NormalDist()
print(f"\n===== OUTLIER vs VIZINHAS (2º turno) =====")
print(f"Seções testadas (em locais com >=3 seções): {nsec:,}")
print(f"z médio {statistics.mean(zs):+.3f}  desvio {statistics.pstdev(zs):.3f}  (esperado: 0 e ~1 se for só ruído)")
print(f"\n{'|z|>=':>6}{'obs +':>8}{'obs -':>8}{'esperado(cada lado)':>22}")
for b in big:
    exp_each=nsec*(1-N.cdf(b))
    print(f"{b:>6}{cnt[b]['+']:>8}{cnt[b]['-']:>8}{exp_each:>22.1f}")
# simetria: excesso pró-Lula vs pró-Flávio em |z|>=4
tot_excess_pos=cnt[4]['+']; tot_excess_neg=cnt[4]['-']
print(f"\nEm |z|>=4: {tot_excess_pos} seções acima do bairro (pró-Lula), {tot_excess_neg} abaixo (pró-Flávio)")
print("(excesso simétrico = heterogeneidade local/ruído; excesso só de um lado = sinal)")
json.dump({'nsec':nsec,'cnt':{str(k):v for k,v in cnt.items()},'zmean':statistics.mean(zs),'zstd':statistics.pstdev(zs)},open("outlier_result.json","w"))
