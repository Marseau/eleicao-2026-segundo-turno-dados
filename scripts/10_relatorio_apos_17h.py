import csv, sys, collections, math
S = sys.argv[1]
rows = [r for r in csv.DictReader(open(f"{S}/after17_BR.csv")) if not r["erro"]]
err = sum(1 for r in csv.DictReader(open(f"{S}/after17_BR.csv")) if r["erro"])
I = lambda r, k: int(r[k])
cp = collections.Counter()
for r in csv.DictReader(open(f"{S}/cold_sections.csv")):
    cp[r["uf"].lower()] += int(r["cp2"])

T = collections.Counter(); L = collections.Counter()   # L = só urnas com voto após 17h
U = collections.defaultdict(collections.Counter)
off = collections.Counter()
for r in rows:
    k = ["total", "after", "a_bio", "a_man", "a_sem", "b_bio", "b_man", "b_sem"]
    for x in k: T[x] += I(r, x); U[r["uf"]][x] += I(r, x)
    U[r["uf"]]["secoes"] += 1
    off[(r["anchor"], r["offset"])] += 1
    if I(r, "after") > 0:
        L["urnas"] += 1
        for x in k: L[x] += I(r, x)
        U[r["uf"]]["urnas_tarde"] += 1

def pct(a, b): return 100 * a / b if b else 0
print(f"Seções processadas: {len(rows):,} (com erro de leitura: {err})")
print(f"Votos contados nos logs: {T['total']:,} | comparecimento oficial: {sum(cp.values()):,} | diferença: {T['total']-sum(cp.values()):+,}")
print(f"Âncora de fuso: {dict(off)}\n")
a = T["after"]; b = T["b_bio"] + T["b_man"] + T["b_sem"]
print("===== NACIONAL =====")
print(f"Votos após as 17h (Brasília): {a:,}")
print(f"  biometria:        {T['a_bio']:,} ({pct(T['a_bio'],a):.2f}%)")
print(f"  liberação manual: {T['a_man']:,} ({pct(T['a_man'],a):.2f}%)")
print(f"  sem biometria cadastrada/outro: {T['a_sem']:,} ({pct(T['a_sem'],a):.2f}%)")
print(f"  => SEM biometria (manual + sem): {T['a_man']+T['a_sem']:,} ({pct(T['a_man']+T['a_sem'],a):.2f}%)")
print(f"Votos até as 17h: {b:,} | sem biometria: {pct(T['b_man']+T['b_sem'],b):.2f}%")
print(f"Urnas com algum voto após as 17h: {L['urnas']:,} de {len(rows):,}")

# comparação justa: dentro das MESMAS urnas que tiveram voto tardio
la = L["after"]; lb = L["b_bio"] + L["b_man"] + L["b_sem"]
p1 = (L["a_man"] + L["a_sem"]) / la if la else 0
p0 = (L["b_man"] + L["b_sem"]) / lb if lb else 0
print("\n===== MESMAS URNAS (só as que tiveram voto após 17h) =====")
print(f"Sem biometria após as 17h: {pct(p1,1):.2f}%  ({L['a_man']+L['a_sem']:,} de {la:,})")
print(f"Sem biometria no resto do dia nessas urnas: {pct(p0,1):.2f}%  ({L['b_man']+L['b_sem']:,} de {lb:,})")
print(f"  manual: {pct(L['a_man'],la):.2f}% (tarde) x {pct(L['b_man'],lb):.2f}% (resto)")
print(f"  sem cadastro/outro: {pct(L['a_sem'],la):.2f}% (tarde) x {pct(L['b_sem'],lb):.2f}% (resto)")
if la:
    se = math.sqrt(p0 * (1 - p0) / la); z = (p1 - p0) / se if se else 0
    print(f"Diferença: {100*(p1-p0):+.2f} pp | z = {z:+.1f} (|z|>3 = diferença estatisticamente real)")

print("\n===== POR ESTADO =====")
print(f"{'UF':3}{'após 17h':>10}{'urnas':>8}{'s/ biom. tarde':>16}{'s/ biom. resto':>16}{'log x oficial':>15}")
for u in sorted(U, key=lambda u: -U[u]["after"]):
    c = U[u]; ca = c["after"]; cb = c["b_bio"] + c["b_man"] + c["b_sem"]
    print(f"{u.upper():3}{ca:>10,}{c['urnas_tarde']:>8,}{pct(c['a_man']+c['a_sem'],ca):>15.1f}%{pct(c['b_man']+c['b_sem'],cb):>15.1f}%{c['total']-cp[u]:>+15,}")
