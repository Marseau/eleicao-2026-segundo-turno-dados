import urllib.request, zipfile, csv, io, os, time, collections
UFS=['AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA','PB',
     'PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO']
BWEB="https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb"
TS="051020261403"; TMP="c1_tmp"; os.makedirs(TMP,exist_ok=True)
cand=collections.Counter(); part=collections.Counter()
for uf in UFS:
    zp=os.path.join(TMP,f"{uf}.zip"); ok=False
    for _ in range(4):
        try: urllib.request.urlretrieve(f"{BWEB}/bweb_1t_{uf}_{TS}.zip",zp); ok=True; break
        except Exception: time.sleep(3)
    if not ok: print("FALHA",uf,flush=True); continue
    z=zipfile.ZipFile(zp); name=[n for n in z.namelist() if n.endswith(".csv")][0]
    with z.open(name) as raw:
        r=csv.reader(io.TextIOWrapper(raw,encoding="latin-1",newline=""),delimiter=";")
        h=next(r); ix={c:i for i,c in enumerate(h)}
        iC=ix["DS_CARGO_PERGUNTA"];iTv=ix["DS_TIPO_VOTAVEL"];iNm=ix["NM_VOTAVEL"];iV=ix["QT_VOTOS"];iP=ix.get("SG_PARTIDO")
        for row in r:
            if row[iC].strip().upper()!="PRESIDENTE": continue
            if row[iTv].strip().upper()!="NOMINAL": continue
            nm=row[iNm].strip(); cand[nm]+=int(row[iV])
            if iP is not None: part[(nm,row[iP].strip())]+=int(row[iV])
    z.close(); os.remove(zp); print(uf,"ok",flush=True)
tot=sum(cand.values())
print(f"\n=== PRESIDENTE 1º TURNO — votos nominais nacionais ({tot:,}) ===")
for nm,v in cand.most_common():
    sg=next((p for (n,p),c in part.items() if n==nm), "?")
    print(f"  {v:>14,}  {100*v/tot:5.2f}%  {sg:6}  {nm}")
