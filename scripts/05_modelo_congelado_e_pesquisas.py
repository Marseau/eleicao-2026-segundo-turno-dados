"""
05 — As probabilidades, com as premissas explícitas.

(a) Modelo "eleitorado congelado": bases do 1T 100% fiéis; outros de direita -> Flávio;
    Cury e Renan 50/50; mínimos de esquerda -> Lula; válidos novos pela proporção do 1T.
    Qual a probabilidade do resultado observado só com ruído binomial?
(b) Pesquisas da reta final (dados/pesquisas_2t_reta_final.csv): média, dispersão entre
    institutos, erro amostral. P(Lula >= observado) sob incerteza calculável só com 2026.
(c) Sensibilidade ao ERRO SISTEMÁTICO das pesquisas (todas errarem juntas), que 2026 sozinho
    não calibra: o único parâmetro que muda a resposta.
(d) Prior "nunca houve virada" (0 em 7) pela regra de Laplace.
(e) Rejeição como TETO: voto de cada um entre os presentes <= 100 - rejeição.
Só biblioteca padrão. ~10 s.
"""
import csv, math, random, statistics, os
from statistics import NormalDist
N=NormalDist(); sf=lambda z: 1-N.cdf(z)
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows=list(csv.DictReader(open(os.path.join(BASE,"dados","secoes_2026_1t_2t.csv"))))
I=lambda r,k:int(r[k])
T=collections=__import__('collections').Counter()
for r in rows:
    if I(r,'cp1')<=0 or I(r,'cp2')<=0: continue
    for c in ['cp1','L1','F1','B1','N1','cp2','L2','F2','B2','N2']: T[c]+=I(r,c)
L1,F1,L2,F2=T['L1'],T['F1'],T['L2'],T['F2']
O1=(T['cp1']-T['B1']-T['N1'])-L1-F1
newv=((T['B1']+T['N1'])-(T['B2']+T['N2']))+(T['cp2']-T['cp1'])
obs=100*L2/(L2+F2)
M=lambda x:x/1e6
print(f"Pools 1T: Lula {M(L1):.2f}M Flávio {M(F1):.2f}M outros {M(O1):.2f}M | válidos novos no 2T {M(newv):.2f}M | observado Lula {obs:.2f}%")

# ---------- (a) modelo congelado ----------
cand={r['candidato']:r for r in csv.DictReader(open(os.path.join(BASE,"dados","candidatos_1t_2026.csv")))}
v=lambda nm:int(cand[nm]['votos'])
cury=v('AUGUSTO CURY'); renan=v('RENAN SANTOS')
right=v('RONALDO CAIADO')+v('ZEMA')+v('LEONARDO AVALANCHE')+v('CLARIANA BARAO')+v('WILSON GRASSI')
left=v('SAMARA')+v('HERTZ DIAS')+v('EDMILSON COSTA')+v('RUI COSTA PIMENTA')
othL=0.5*(cury+renan)+left; othF=0.5*(cury+renan)+right
p1=L1/(L1+F1)
EL=L1+othL+p1*newv; EF=F1+othF+(1-p1)*newv
print(f"\n(a) MODELO CONGELADO: esperado Lula {M(EL):.2f}M ({100*EL/(EL+EF):.1f}%)  Flávio {M(EF):.2f}M ({100*EF/(EL+EF):.1f}%)")
sd=math.sqrt(newv*p1*(1-p1)+(cury+renan)*0.25); z=(L2-EL)/sd
print(f"    Lula observado {M(L2-EL):+.2f}M acima; ruído binomial {sd/1e3:.1f} mil votos; z = {z:.0f}; P = 0 (analítico ~10^-{int(z*z/4.6):,})")
print(f"    para EMPATAR sob estas premissas: {M((EF-EL)/2):.2f}M votos teriam de migrar de Flávio para Lula")

# ---------- (b) pesquisas ----------
polls=[]
for r in csv.DictReader(open(os.path.join(BASE,"dados","pesquisas_2t_reta_final.csv"))):
    nsz=int(r['amostra']) if r['amostra'].strip() else 2000
    polls.append((r['instituto'],float(r['lula_validos']),nsz,r['rej_lula'],r['rej_flavio']))
vals=[p[1] for p in polls]; m=statistics.mean(vals); sd_inst=statistics.stdev(vals)
sd_samp=statistics.mean(100*math.sqrt(0.25/p[2]) for p in polls)/math.sqrt(len(polls))
sd_tot=math.sqrt(sd_inst**2+sd_samp**2); zp=(obs-m)/sd_tot
print(f"\n(b) PESQUISAS ({len(polls)} institutos): média Lula {m:.2f}% | dispersão entre institutos {sd_inst:.2f} pp | erro amostral da média {sd_samp:.2f} pp")
print(f"    observado {obs:.2f}% = {obs-m:+.2f} pp acima da média -> z = {zp:.2f} -> P = {100*sf(zp):.3f}%")
random.seed(11); S=500_000; hit=sum(1 for _ in range(S) if random.gauss(m,sd_tot)>=obs)
print(f"    Monte Carlo {S:,}: P = {hit/S:.5f}  | pesquisas com Lula >= 50%: {sum(1 for x in vals if x>=50)} de {len(polls)}")
print("\n(c) SENSIBILIDADE ao erro sistemático s (todas as pesquisas errarem juntas):")
for s in [0,1,2,3,4]:
    print(f"    s = {s} pp : P(resultado) = {100*sf((obs-m)/math.sqrt(sd_tot**2+s**2)):6.2f}%")
print(f"\n(d) Prior de virada, 0 em 7 eleições (Laplace): {100/9:.1f}%")
comp2=T['cp2']
print(f"\n(e) REJEIÇÃO como teto (Lula teve {100*L2/comp2:.1f}% dos presentes; Flávio {100*F2/comp2:.1f}%):")
for inst,_,_,rL,rF in polls:
    if rL.strip() and rF.strip():
        rL=float(rL); rF=float(rF)
        print(f"    {inst:22}: teto Lula {100-rL:.1f}% (folga {100-rL-100*L2/comp2:+.1f}) | teto Flávio {100-rF:.1f}% (folga {100-rF-100*F2/comp2:+.1f})")
print(f"\nResumo: congelado 47,9% -> pesquisas {m:.1f}% -> observado {obs:.2f}%. Movimento já medido pelas pesquisas: {m-100*EL/(EL+EF):+.1f} pp; além delas: {obs-m:+.1f} pp.")
