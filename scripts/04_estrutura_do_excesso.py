"""
04 — A forma do movimento: onde o excesso do Lula é maior e onde é negativo.

Mostra que o excesso sobre o ambiente local cresce com a força do Flávio no 1T e que os
municípios onde o Lula ficou ABAIXO da própria proporção local se concentram em redutos dele
no Nordeste. Um ajuste mecânico pró-Lula não produz municípios negativos; um bloco nacional de
eleitores com preferência própria produz exatamente isso. ~20 s.
"""
import csv, collections, statistics, os
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows=list(csv.DictReader(open(os.path.join(BASE,"dados","secoes_2026_1t_2t.csv"))))
I=lambda r,k:int(r[k])
NE={'AL','BA','CE','MA','PB','PE','PI','RN','SE'}; NO={'AC','AM','AP','PA','RO','RR','TO'}
reg=lambda u:'NE' if u in NE else ('N' if u in NO else 'S/SE/CO')
Mun=collections.defaultdict(collections.Counter); UF={}
for r in rows:
    if I(r,'cp1')<=0 or I(r,'cp2')<=0: continue
    k=(r['uf'],r['mun']); UF[k]=r['uf']; d=Mun[k]
    for c in ['cp1','L1','F1','B1','N1','cp2','L2','F2','B2','N2']: d[c]+=I(r,c)
recs=[]
for k,d in Mun.items():
    if d['L1']+d['F1']<100: continue
    O1=(d['cp1']-d['B1']-d['N1'])-d['L1']-d['F1']
    if O1<0: continue
    pool=O1+((d['B1']+d['N1'])-(d['B2']+d['N2']))+(d['cp2']-d['cp1'])
    if pool<=0: continue
    p=d['L1']/(d['L1']+d['F1']); v2=d['L2']+d['F2']
    recs.append((100*((d['L2']-d['L1'])-p*pool)/v2, reg(UF[k]), 1-p, v2))
n=len(recs); neg=[r for r in recs if r[0]<=0]
print(f"Municípios {n} | com excesso NEGATIVO (foram para o Flávio além do local): {len(neg)} ({100*len(neg)/n:.1f}%)\n")
print("Onde estão os negativos:")
for rg in ['NE','N','S/SE/CO']:
    t=sum(1 for r in recs if r[1]==rg); g=sum(1 for r in neg if r[1]==rg)
    print(f"  {rg:9}: {g:4} de {t:4} municípios = {100*g/max(t,1):.1f}%")
print("\nExcesso médio do Lula por força do Flávio no 1T (terços):")
rs=sorted(recs,key=lambda r:r[2]); t=n//3
for nome,ch in [("terço MENOS Flávio",rs[:t]),("terço médio",rs[t:2*t]),("terço MAIS Flávio",rs[2*t:])]:
    print(f"  {nome:20}: Flávio1T {100*statistics.mean(r[2] for r in ch):.0f}%  ->  excesso médio {statistics.mean(r[0] for r in ch):+.2f} pp | negativos {100*sum(1 for r in ch if r[0]<=0)/len(ch):.1f}%")
def pear(xs,ys):
    m=len(xs);mx=sum(xs)/m;my=sum(ys)/m
    cov=sum((a-mx)*(b-my) for a,b in zip(xs,ys));sx=sum((a-mx)**2 for a in xs)**.5;sy=sum((b-my)**2 for b in ys)**.5
    return cov/(sx*sy) if sx and sy else 0
print(f"\ncorr(excesso do Lula, força do Flávio no 1T) = {pear([r[0] for r in recs],[r[2] for r in recs]):+.3f}")
print("\nLeitura: o excesso é MAIOR onde o Flávio era mais forte e menor/negativo nos redutos do Lula. É o que um bloco\n"
      "de eleitores com preferência própria (~65% Lula, onde quer que more) produz: parece 'mais Lula' que a vizinhança\n"
      "no Sul e 'menos Lula' que a vizinhança no Nordeste. Um ajuste mecânico pró-Lula não gera municípios negativos.")
