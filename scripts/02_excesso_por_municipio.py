"""
02 — O movimento entre turnos medido contra o ambiente de cada urna.

Para cada seção (e depois por município): se os "votos em disputa" do 2º turno
   pool = outros do 1T + redução de branco/nulo + aumento de comparecimento
se dividissem na MESMA proporção Lula/Flávio que a própria seção teve no 1º turno,
quanto cada candidato ganharia? A diferença entre o observado e isso é o "excesso".

Saídas:
  - números nacionais (nível de seção): esperado pelo nulo local vs observado, excesso
  - por município: % com excesso positivo, teste de sinal, teste da média
  - Nula B (desvio do deslocamento comum, calibrado): quantos municípios ficam fora, lista z>3
  - resultados/municipios_excesso.csv  (todos os municípios)
  - resultados/municipios_z3.csv       (os que desviam do comum em z>3)
Só biblioteca padrão. ~30 s.
"""
import csv, math, statistics, collections, os
from statistics import NormalDist
N=NormalDist()
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows=list(csv.DictReader(open(os.path.join(BASE,"dados","secoes_2026_1t_2t.csv"))))
I=lambda r,k:int(r[k])
def outros(r): return (I(r,'cp1')-I(r,'B1')-I(r,'N1'))-I(r,'L1')-I(r,'F1')   # recalculado; não usar coluna O1

# ---------- nível de SEÇÃO (números de manchete) ----------
A=collections.Counter(); nsec=0
for r in rows:
    cp1=I(r,'cp1');cp2=I(r,'cp2');L1=I(r,'L1');F1=I(r,'F1');L2=I(r,'L2');F2=I(r,'F2')
    if cp1<=0 or cp2<=0 or L1+F1<20: continue
    O1=outros(r)
    if O1<0: continue
    p=L1/(L1+F1); dcomp=cp2-cp1; dbn=(I(r,'B1')+I(r,'N1'))-(I(r,'B2')+I(r,'N2')); pool=O1+dbn+dcomp
    A['nL']+=p*pool; A['nF']+=(1-p)*pool; A['oL']+=L2-L1; A['oF']+=F2-F1
    A['L1']+=L1;A['F1']+=F1;A['O1']+=O1;A['dbn']+=dbn;A['dcomp']+=dcomp;A['L2']+=L2;A['F2']+=F2; nsec+=1
M=lambda x:x/1e6
print(f"Seções usadas: {nsec}")
print(f"Pools: Lula1T {M(A['L1']):.2f}M  Flávio1T {M(A['F1']):.2f}M  outros {M(A['O1']):.2f}M  Δbranco/nulo {M(A['dbn']):.2f}M  Δcomparecimento {M(A['dcomp']):.2f}M")
print(f"Resultado 2T: Lula {M(A['L2']):.2f}M ({100*A['L2']/(A['L2']+A['F2']):.2f}%)  Flávio {M(A['F2']):.2f}M")
print(f"\nSE cada urna dividisse os votos novos como ela própria votou no 1T:")
print(f"  esperado: Lula {M(A['nL']):+.2f}M   Flávio {M(A['nF']):+.2f}M")
print(f"  observado: Lula {M(A['oL']):+.2f}M   Flávio {M(A['oF']):+.2f}M")
print(f"  EXCESSO do Lula sobre o ambiente local: {M(A['oL']-A['nL']):+.2f}M")

# ---------- nível de MUNICÍPIO ----------
Mun=collections.defaultdict(collections.Counter)
for r in rows:
    if I(r,'cp1')<=0 or I(r,'cp2')<=0: continue
    d=Mun[(r['uf'],r['mun'])]
    for c in ['cp1','L1','F1','B1','N1','cp2','L2','F2','B2','N2']: d[c]+=I(r,c)
recs=[]
for (uf,mun),d in Mun.items():
    if d['L1']+d['F1']<100: continue
    O1=(d['cp1']-d['B1']-d['N1'])-d['L1']-d['F1']
    if O1<0: continue
    dbn=(d['B1']+d['N1'])-(d['B2']+d['N2']); dcomp=d['cp2']-d['cp1']; pool=O1+dbn+dcomp
    if pool<=0: continue
    p=d['L1']/(d['L1']+d['F1']); v2=d['L2']+d['F2']; nullL=p*pool
    exv=(d['L2']-d['L1'])-nullL
    recs.append(dict(uf=uf,cd_municipio=mun,prop_lula_1t=round(100*p,2),pool=pool,outros_1t=O1,d_branco_nulo=dbn,
                     d_comparecimento=dcomp,ganho_lula=d['L2']-d['L1'],ganho_flavio=d['F2']-d['F1'],
                     nulo_local_lula=round(nullL),excesso_votos=round(exv),excesso_pp=round(100*exv/v2,3),validos_2t=v2))
n=len(recs); pps=[x['excesso_pp'] for x in recs]; pos=sum(1 for x in pps if x>0)
print(f"\nMunicípios: {n} | com excesso pró-Lula: {pos} ({100*pos/n:.1f}%)")
z_sign=(pos-n/2)/math.sqrt(n*0.25); m=statistics.mean(pps); sd=statistics.pstdev(pps)
print(f"Teste de sinal (nula: 50/50): z = {z_sign:.0f}")
print(f"Excesso médio {m:+.2f} pp (desvio {sd:.2f}); teste da média: t = {m/(sd/math.sqrt(n)):.0f}")

# ---------- Nula B: desvio do deslocamento comum ----------
center=statistics.median(pps); mad=statistics.median(abs(x-center) for x in pps); tau=1.4826*mad
delta=sum(x['excesso_votos'] for x in recs)/sum(x['pool'] for x in recs)
for x in recs:
    p=x['prop_lula_1t']/100; q=min(.99,max(.01,p+delta))
    sdb=100*math.sqrt(x['pool']*q*(1-q))/x['validos_2t']
    x['z_desvio_do_comum']=round((x['excesso_pp']-center)/math.sqrt(sdb**2+tau**2),2)
    x['votos_acima_do_comum']=round((x['excesso_pp']-center)/100*x['validos_2t'])
print(f"\nNula B — deslocamento comum (mediana) {center:+.2f} pp, dispersão real tau {tau:.2f} pp")
for zc in [2,3,4]:
    sel=[x for x in recs if x['z_desvio_do_comum']>zc]
    print(f"  z>{zc}: {len(sel):4} municípios | esperados por acaso: {n*(1-N.cdf(zc)):6.1f} | votos acima do comum: {sum(x['votos_acima_do_comum'] for x in sel):+,}")
os.makedirs(os.path.join(BASE,"resultados"),exist_ok=True)
with open(os.path.join(BASE,"resultados","municipios_excesso.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(recs[0].keys())); w.writeheader(); w.writerows(sorted(recs,key=lambda x:-x['excesso_votos']))
with open(os.path.join(BASE,"resultados","municipios_z3.csv"),"w",newline="",encoding="utf-8") as f:
    sel=sorted([x for x in recs if x['z_desvio_do_comum']>3],key=lambda x:-x['z_desvio_do_comum'])
    w=csv.DictWriter(f,fieldnames=list(recs[0].keys())); w.writeheader(); w.writerows(sel)
print("\nsalvos: resultados/municipios_excesso.csv, resultados/municipios_z3.csv")
