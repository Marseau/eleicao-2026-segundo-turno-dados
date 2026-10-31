"""
Votos registrados após as 17h (Brasília) no 2º turno de 2026, por tipo de habilitação,
a partir do log de TODAS as urnas de um pacote estadual do TSE (arqurnatot).

Uso: python -I after17.py <pacote_UF.zip> <saida.csv>
Acrescenta uma linha por seção ao CSV.

Fuso: o log usa hora local e não registra o fuso. Âncora: o evento
"Urna pronta para receber votos" ocorre na abertura (8h de Brasília). Logo
  limite local das 17h de Brasília = 17 - (8 - hora_local_da_urna_pronta).
Habilitação de cada eleitor (até o "voto computado"):
  man = houve "Solicitação ... habilitação manual" (digital falhou, mesário liberou)
  bio = "Tipo de habilitação do eleitor [biométrica]" sem liberação manual
  sem = nenhum dos dois (eleitor sem biometria cadastrada / outro tipo)
"""
import sys, os, io, zipfile, csv, datetime as dt, re

DAY = "25/10/2026"
UF_DEFAULT_OFFSET = {"ac": -2, "am": -1, "ms": -1, "mt": -1, "ro": -1, "rr": -1}
# fusos possíveis por estado (AM tem o oeste em UTC-5; PE tem Fernando de Noronha em UTC-2)
ALLOWED = {"ac": {-2}, "am": {-1, -2}, "ms": {-1}, "mt": {-1}, "ro": {-1}, "rr": {-1}, "pe": {0, 1}}

def parse_log(raw_bytes, uf):
    with zipfile.ZipFile(io.BytesIO(raw_bytes)) as z:
        names = [n for n in z.namelist() if n.endswith(".dat")] or z.namelist()
        txt = z.read(names[0]).decode("latin-1")
    pronta = None; enc = None; last_vote = None
    events = []
    for line in txt.split("\n"):
        if not line.startswith(DAY):
            continue
        pr = line.split("\t")
        if len(pr) < 5:
            continue
        try:
            t = dt.datetime.strptime(pr[0].strip(), "%d/%m/%Y %H:%M:%S")
        except ValueError:
            continue
        m = pr[4].strip()
        if m.startswith("Urna pronta para receber votos") and pronta is None:
            pronta = t
        if m.startswith("Procedimento de encerramento confirmado"):
            enc = t
        events.append((t, m))
    # fuso aceito só se compatível com o estado E se a urna abriu no início do dia
    # (urna de contingência abre tarde e não serve de âncora)
    allowed = ALLOWED.get(uf, {0})
    cand = (pronta.hour - 8) if pronta is not None else None
    if cand is not None and cand in allowed and pronta.minute < 30:
        offset = cand; anchor = "pronta"
    else:
        offset = UF_DEFAULT_OFFSET.get(uf, 0)
        anchor = "uf"
    limit_hour = 17 + offset
    r = dict(total=0, after=0, a_bio=0, a_man=0, a_sem=0, b_bio=0, b_man=0, b_sem=0)
    man = bio = False
    for t, m in events:
        if "habilitação manual" in m:
            man = True
        elif m.startswith("Tipo de habilitação do eleitor [biométrica]"):
            bio = True
        elif m.startswith("Habilitação cancelada"):
            man = bio = False
        elif m == "O voto do eleitor foi computado":
            kind = "man" if man else ("bio" if bio else "sem")
            r["total"] += 1
            last_vote = t
            if t.hour >= limit_hour:
                r["after"] += 1; r["a_" + kind] += 1
            else:
                r["b_" + kind] += 1
            man = bio = False
    r.update(offset=offset, anchor=anchor,
             pronta=pronta.strftime("%H:%M:%S") if pronta else "",
             encerramento=enc.strftime("%H:%M:%S") if enc else "",
             ultimo_voto=last_vote.strftime("%H:%M:%S") if last_vote else "")
    return r

def main(zpath, out):
    cols = ["uf", "secao_id", "total", "after", "a_bio", "a_man", "a_sem", "b_bio", "b_man", "b_sem",
            "offset", "anchor", "pronta", "encerramento", "ultimo_voto", "erro"]
    new = not os.path.exists(out)
    n = 0; err = 0
    with zipfile.ZipFile(zpath) as Z, open(out, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if new:
            w.writeheader()
        for name in Z.namelist():
            if not name.endswith("-log.jez"):
                continue
            sid = os.path.basename(name)[:-len("-log.jez")]   # ex.: o03221ac0100700090001
            uf = sid[6:8]
            try:
                r = parse_log(Z.read(name), uf); r["erro"] = ""
            except Exception as e:
                r = {"erro": type(e).__name__}; err += 1
            r["uf"] = uf; r["secao_id"] = sid
            w.writerow(r); n += 1
    print(f"{os.path.basename(zpath)}: {n} logs processados, {err} com erro", flush=True)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
