"""
03 — Monte Carlo da uniformidade ("a moeda é honesta?").

MC1  nula "não existe movimento nacional": cada município divide os votos novos pela
     própria proporção do 1T, só com ruído binomial. Qual a chance de 97% saírem pró-Lula?
MC2  alternativa "deslocamento nacional uniforme" (mesmo acréscimo em todo lugar) + ruído:
     reproduz o observado? (não: dá ~100% pró-Lula, e o observado tem 2,9% contra)
MC3  deslocamento nacional + variação LOCAL gaussiana (sigma): algum sigma reproduz ao mesmo
     tempo o % pró-Lula e a dispersão? (não -> a variação local é estruturada, ver script 04)

Aproximação normal da binomial para velocidade. SIMS ajustável. ~2-5 min.
"""
import csv, math, random, statistics, collections, os, sys
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows=list(csv.DictReader(open(os.path.join(BASE,"dados","secoes_2026_1t_2t.csv"))))
I=lambda r,k:int(r[k])
Mun=collections.defaultdict(collections.Counter)
for r in rows:
    if I(r,'cp1')<=0 or I(r,'cp2')<=0: continue
    d=Mun[(r['uf'],r['mun'])]
    for c in ['cp1','L1','F1','B1','N1','cp2','L2','F2','B2','N2']: d[c]+=I(r,c)
mun=[]; obs=[]
for d in Mun.values():
    if d['L1']+d['F1']<100: continue
    O1=(d['cp1']-d['B1']-d['N1'])-d['L1']-d['F1']
    if O1<0: continue
    pool=O1+((d['B1']+d['N1'])-(d['B2']+d['N2']))+(d['cp2']-d['cp1'])
    if pool<=0: continue
    p=d['L1']/(d['L1']+d['F1']); v2=d['L2']+d['F2']
    mun.append((pool,p,v2)); obs.append(100*((d['L2']-d['L1'])-p*pool)/v2)
n=len(mun); obs_pos=100*sum(1 for x in obs if x>0)/n; obs_mean=statistics.mean(obs); obs_sd=statistics.pstdev(obs)
delta=sum(((d['L2']-d['L1'])-(d['L1']/(d['L1']+d['F1']))*(((d['cp1']-d['B1']-d['N1'])-d['L1']-d['F1'])+((d['B1']+d['N1'])-(d['B2']+d['N2']))+(d['cp2']-d['cp1']))) for d in Mun.values() if d['L1']+d['F1']>=100)/sum((((d['cp1']-d['B1']-d['N1'])-d['L1']-d['F1'])+((d['B1']+d['N1'])-(d['B2']+d['N2']))+(d['cp2']-d['cp1'])) for d in Mun.values() if d['L1']+d['F1']>=100)
print(f"Municípios {n} | OBSERVADO: {obs_pos:.1f}% pró-Lula, excesso médio {obs_mean:+.2f} pp, dispersão {obs_sd:.2f} pp")
print(f"Deslocamento nacional médio (fração do pool): {delta:+.3f}\n")
SIMS=int(sys.argv[1]) if len(sys.argv)>1 else 1000
random.seed(2026)
def run(delta_,sigma):
    P=[];Mn=[];Sd=[]
    for _ in range(SIMS):
        ex=[]
        for pool,p,v2 in mun:
            sh=delta_+(random.gauss(0,sigma) if sigma>0 else 0.0); q=min(0.99,max(0.01,p+sh))
            lnew=random.gauss(pool*q,math.sqrt(pool*q*(1-q)))
            ex.append(100*(lnew-p*pool)/v2)
        P.append(100*sum(1 for e in ex if e>0)/n); Mn.append(statistics.mean(ex)); Sd.append(statistics.pstdev(ex))
    return P,Mn,Sd
P,Mn,Sd=run(0.0,0.0)
print(f"MC1 nula 'sem movimento nacional' ({SIMS} sims): % pró-Lula média {statistics.mean(P):.1f}% (máx {max(P):.1f}%) | sims >= {obs_pos:.1f}%: {sum(1 for x in P if x>=obs_pos)}")
print(f"     observado está a {(obs_pos-statistics.mean(P))/statistics.pstdev(P):.0f} desvios-padrão da nula\n")
print(f"MC2/MC3 deslocamento nacional {delta:+.3f} + variação local sigma (observado: {obs_pos:.1f}% / {obs_mean:+.2f} / {obs_sd:.2f}):")
print(f"{'sigma':>7}{'% pró-Lula':>12}{'exc médio':>11}{'dispersão':>11}")
for sigma in [0.0,0.04,0.08,0.12,0.14,0.16]:
    P,Mn,Sd=run(delta,sigma)
    tag="   <- uniforme perfeito: 100%, exclui o observado" if sigma==0 else ""
    print(f"{sigma:>7.2f}{statistics.mean(P):>11.1f}%{statistics.mean(Mn):>+11.2f}{statistics.mean(Sd):>11.2f}{tag}")
print("\nLeitura: nenhum sigma gaussiano dá ao mesmo tempo ~97% e dispersão ~1,25. A variação local não é ruído; é estruturada (script 04).")
