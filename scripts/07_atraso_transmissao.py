import urllib.request, zipfile, csv, io, os, time, collections, statistics, datetime as dt
UFS=['AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA','PB','PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO']
BWEB="https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb"; TS="261020260742"; TMP="dl_tmp"; os.makedirs(TMP,exist_ok=True)
def pdt(s):
    s=s.strip()
    for f in ("%Y-%m-%d %H:%M:%S","%d/%m/%Y %H:%M:%S","%Y-%m-%d %H:%M","%d/%m/%Y %H:%M"):
        try: return dt.datetime.strptime(s,f)
        except ValueError: pass
    return None
S=[]  # (uf,mun,zona,local,secao,delay_min,L,F,enc,rec)
for uf in UFS:
    zp=os.path.join(TMP,f"{uf}.zip"); ok=False
    for _ in range(4):
        try: urllib.request.urlretrieve(f"{BWEB}/bweb_2t_{uf}_{TS}.zip",zp); ok=True; break
        except Exception: time.sleep(3)
    if not ok: print("FALHA",uf,flush=True); continue
    z=zipfile.ZipFile(zp); name=[n for n in z.namelist() if n.endswith(".csv")][0]
    sec={}
    with z.open(name) as raw:
        r=csv.reader(io.TextIOWrapper(raw,encoding="latin-1",newline=""),delimiter=";")
        h=next(r); ix={c:i for i,c in enumerate(h)}
        iC=ix["DS_CARGO_PERGUNTA"];iM=ix["CD_MUNICIPIO"];iZ=ix["NR_ZONA"];iS=ix["NR_SECAO"];iL=ix["NR_LOCAL_VOTACAO"]
        iNm=ix["NM_VOTAVEL"];iV=ix["QT_VOTOS"];iEnc=ix["DT_ENCERRAMENTO"];iRec=ix["DT_BU_RECEBIDO"]
        for row in r:
            if row[iC].strip().upper()!="PRESIDENTE": continue
            k=(row[iM].strip(),row[iZ].strip(),row[iS].strip())
            d=sec.setdefault(k,{'loc':row[iL].strip(),'L':0,'F':0,'enc':row[iEnc],'rec':row[iRec]})
            nm=row[iNm].strip().upper()
            if nm=="LULA": d['L']=int(row[iV])
            elif nm=="FLAVIO BOLSONARO": d['F']=int(row[iV])
    for (m,zn,sc),d in sec.items():
        e=pdt(d['enc']); rc=pdt(d['rec'])
        if not e or not rc or d['L']+d['F']<20: continue
        delay=(rc-e).total_seconds()/60
        if delay<0 or delay>24*60: continue
        S.append((uf,m,zn,d['loc'],sc,delay,d['L'],d['F'],d['enc'].strip(),d['rec'].strip()))
    z.close(); os.remove(zp); print(uf,"ok",len(S),flush=True)

def pear(xs,ys):
    n=len(xs);mx=sum(xs)/n;my=sum(ys)/n
    cov=sum((a-mx)*(b-my) for a,b in zip(xs,ys));sx=sum((a-mx)**2 for a in xs)**.5;sy=sum((b-my)**2 for b in ys)**.5
    return cov/(sx*sy) if sx and sy else 0
print(f"\nSeções com horários válidos: {len(S)}")
# ---- 1) os dois locais do post: SP zona 259 locais 1686 e 1465 ----
print("\n===== OS DOIS LOCAIS DO POST (SP, zona 259) =====")
for loc in ["1686","1465"]:
    ss=[x for x in S if x[0]=="SP" and x[2].lstrip("0")=="259" and x[3].lstrip("0")==loc]
    if not ss: print(f"local {loc}: não encontrado"); continue
    L=sum(x[6] for x in ss); F=sum(x[7] for x in ss); dls=[x[5] for x in ss]
    print(f"local {loc}: {len(ss)} seções | Lula {L} ({100*L/(L+F):.1f}%)  Flávio {F} | atraso médio {statistics.mean(dls):.0f} min (mín {min(dls):.0f}, máx {max(dls):.0f})")
    for x in sorted(ss,key=lambda x:x[5]): print(f"    seção {x[4]:>5}: encerrou {x[8][-8:]}  recebido {x[9][-8:]}  atraso {x[5]:5.0f} min  Lula {x[6]:4} Flávio {x[7]:4}")
# ---- 2) tese em escala: atraso x %Lula ----
dl=[x[5] for x in S]; ls=[x[6]/(x[6]+x[7]) for x in S]
print(f"\n===== NACIONAL: atraso de transmissão x %Lula =====")
print(f"corr(atraso, %Lula) = {pear(dl,ls):+.3f}")
Ss=sorted(S,key=lambda x:x[5]); t=len(Ss)//3
for nome,ch in [("terço MENOR atraso",Ss[:t]),("terço médio",Ss[t:2*t]),("terço MAIOR atraso",Ss[2*t:])]:
    L=sum(x[6] for x in ch); F=sum(x[7] for x in ch)
    print(f"  {nome:20}: atraso médio {statistics.mean(x[5] for x in ch):5.0f} min  ->  Lula {100*L/(L+F):.1f}%")
# dentro do município (demeaned): tira geografia
bym=collections.defaultdict(list)
for x in S: bym[(x[0],x[1])].append((x[5],x[6]/(x[6]+x[7])))
dd=[];dl2=[]
for vs in bym.values():
    if len(vs)<10: continue
    md=sum(v[0] for v in vs)/len(vs); ml=sum(v[1] for v in vs)/len(vs)
    for a,b in vs: dd.append(a-md); dl2.append(b-ml)
print(f"\nDENTRO DO MESMO MUNICÍPIO (demeaned, n={len(dd)}): corr(atraso, %Lula) = {pear(dd,dl2):+.3f}")
# dentro da zona 259 de SP
z259=[x for x in S if x[0]=="SP" and x[2].lstrip("0")=="259"]
if len(z259)>10: print(f"DENTRO DA ZONA 259/SP ({len(z259)} seções): corr(atraso, %Lula) = {pear([x[5] for x in z259],[x[6]/(x[6]+x[7]) for x in z259]):+.3f}")
# ---- 3) explicação mecânica: atraso x nº de seções do local ----
byloc=collections.defaultdict(list)
for x in S: byloc[(x[0],x[1],x[2],x[3])].append(x[5])
nsec=[];mdel=[]
for v in byloc.values(): nsec.append(len(v)); mdel.append(statistics.mean(v))
print(f"\ncorr(nº de seções do local, atraso médio do local) = {pear(nsec,mdel):+.3f}  (locais: {len(nsec)})")
for lo,hi,nome in [(1,2,"1-2 seções"),(3,6,"3-6"),(7,12,"7-12"),(13,999,"13+")]:
    ch=[m for n,m in zip(nsec,mdel) if lo<=n<=hi]
    if ch: print(f"  locais com {nome:10}: atraso médio {statistics.mean(ch):5.0f} min  (n={len(ch)})")
