import sys, os, zipfile, io, datetime as dt, statistics, glob, json, random, collections
files=sorted(glob.glob("amostra1k/*.jez"))
def read_log(p):
    with zipfile.ZipFile(p) as z:
        return io.TextIOWrapper(z.open(z.namelist()[0]),encoding="latin-1").read()

R1="04/10/2026"; R2="25/10/2026"
# per section per round: list of (is_manual, vote_secs)
per={}  # key -> {R1:[...], R2:[...]}
dur={R1:{'m':[],'b':[]}, R2:{'m':[],'b':[]}}
runs_obs={R1:[],R2:[]}; runs_data={R1:[],R2:[]}  # for clustering: store seq per section
for p in files:
    base=os.path.basename(p); key=base[6:6+15]
    try: txt=read_log(p)
    except Exception: continue
    cur={R1:[],R2:[]}
    manual=False; hab_dt=None; hab_round=None
    for line in txt.split("\n"):
        pr=line.split("\t")
        if len(pr)<5: continue
        ts=pr[0].strip(); msg=pr[4].strip()
        try: t=dt.datetime.strptime(ts,"%d/%m/%Y %H:%M:%S")
        except ValueError: continue
        day=t.strftime("%d/%m/%Y")
        if day not in (R1,R2):
            continue
        if "habilitação manual" in msg: manual=True
        elif msg=="Eleitor foi habilitado":
            hab_dt=t; hab_round=day
        elif msg=="O voto do eleitor foi computado":
            if hab_dt is not None and hab_round==day:
                secs=(t-hab_dt).total_seconds()
                cur[day].append((manual,secs))
            manual=False; hab_dt=None; hab_round=None
    if cur[R1] or cur[R2]:
        per[key]=cur
        for rnd in (R1,R2):
            for m,s in cur[rnd]:
                if 0<=s<3600: dur[rnd]['m' if m else 'b'].append(s)
            seq=[1 if m else 0 for m,s in cur[rnd]]
            runs_data[rnd].append(seq)

def rate(seq): 
    n=len(seq); m=sum(1 for x in seq if x[0]); return n,m
def longest(seq):
    r=mx=0
    for x in seq:
        r=r+1 if x else 0; mx=max(mx,r)
    return mx

print(f"Seções com dados: {len(per)}")
for rnd,lbl in [(R1,"1º TURNO 04/10"),(R2,"2º TURNO 25/10")]:
    tot=sum(len(per[k][rnd]) for k in per); man=sum(sum(1 for m,s in per[k][rnd] if m) for k in per)
    secs_m=dur[rnd]['m']; secs_b=dur[rnd]['b']
    med=lambda xs: statistics.median(xs) if xs else 0
    print(f"\n===== {lbl} =====")
    print(f"votantes: {tot:,} | manuais: {man:,} ({100*man/tot:.2f}%)")
    print(f"duração voto: biom mediana {med(secs_b):.0f}s | manual mediana {med(secs_m):.0f}s")

# paired per-urna rate
print("\n===== PAREADO por urna (mesma seção, 2 turnos) =====")
pairs=[]
for k,c in per.items():
    n1,m1=rate(c[R1]); n2,m2=rate(c[R2])
    if n1>=50 and n2>=50:
        pairs.append((k,n1,m1,n2,m2,m1/n1,m2/n2))
print(f"urnas com >=50 votantes nos 2 turnos: {len(pairs)}")
r1=[p[5] for p in pairs]; r2=[p[6] for p in pairs]
def pear(xs,ys):
    n=len(xs);mx=sum(xs)/n;my=sum(ys)/n
    cov=sum((x-mx)*(y-my) for x,y in zip(xs,ys));sx=sum((x-mx)**2 for x in xs)**.5;sy=sum((y-my)**2 for y in ys)**.5
    return cov/(sx*sy) if sx and sy else 0
print(f"taxa manual média: 1T {100*statistics.mean(r1):.2f}%  2T {100*statistics.mean(r2):.2f}%")
print(f"corr(taxa_1T, taxa_2T) por urna = {pear(r1,r2):+.3f}  (alto = propriedade estável da seção)")
dr=[ (p[6]-p[5]) for p in pairs]
dd=sorted(x*100 for x in dr); q=lambda pp: dd[min(len(dd)-1,int(pp*len(dd)))]
print(f"Δtaxa (2T-1T) por urna, pp: p5 {q(.05):+.1f}  p25 {q(.25):+.1f}  mediana {q(.5):+.1f}  p75 {q(.75):+.1f}  p95 {q(.95):+.1f}")
# outliers: urnas com maior SALTO de manual no 2T
pairs_sorted=sorted(pairs,key=lambda p:p[6]-p[5],reverse=True)
print("\nTop-8 SALTOS de taxa manual 1T->2T (possível sinal):")
for k,n1,m1,n2,m2,x1,x2 in pairs_sorted[:8]:
    print(f"   {k}: 1T {100*x1:4.1f}% ({m1}/{n1})  ->  2T {100*x2:4.1f}% ({m2}/{n2})   Δ{100*(x2-x1):+.1f}pp")

# clustering 2T
random.seed(5)
for rnd,lbl in [(R2,"2º TURNO")]:
    obs=exp=nc=0
    for seq in runs_data[rnd]:
        nm=sum(seq)
        if nm<5: continue
        nc+=1; obs+=longest(seq)
        sims=[]
        for _ in range(120):
            s=seq[:]; random.shuffle(s); sims.append(longest(s))
        exp+=statistics.mean(sims)
    if nc: print(f"\n[{lbl}] agrupamento manuais: corrida máx obs {obs/nc:.2f} vs aleatório {exp/nc:.2f}  (n={nc} seções)")
json.dump([list(p) for p in pairs], open("rounds_pairs.json","w"))
