"""
01 — Baixa os boletins de urna (bweb) do 1º e 2º turno de 2026 (presidente) de todos os
estados, diretamente do TSE, e monta dados/secoes_2026_1t_2t.csv (uma linha por seção).

Fonte: https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_{1t|2t}_{UF}_{TS}.zip
TS (carimbo da publicação): 1T = 051020261403 ; 2T = 261020260742

Colunas de saída:
  uf, mun (CD_MUNICIPIO do TSE), zona, secao,
  ap1 cp1 L1 F1 O1 B1 N1   -> 1º turno: aptos, comparecimento, Lula, Flávio, outros nominais, brancos, nulos
  ap2 cp2 L2 F2 B2 N2      -> 2º turno
  tu2 (CD_TIPO_URNA), cg2 (CD_CARGA_1_URNA_EFETIVADA)

Observação: O1 é a soma dos votos nominais que NÃO são Lula nem Flávio.
(O CSV distribuído no pacote foi gerado por uma versão anterior deste script com O1 zerado por
 um bug de subtração dupla; todos os scripts 02-05 recalculam O1 = (cp1-B1-N1)-L1-F1 e não usam a coluna.)
Demora: ~30-60 min (SP tem 1,4 GB por turno). Só biblioteca padrão.
"""
import urllib.request, zipfile, csv, io, os, time
UFS=['AC','AL','AM','AP','BA','CE','DF','ES','GO','MA','MG','MS','MT','PA','PB',
     'PE','PI','PR','RJ','RN','RO','RR','RS','SC','SE','SP','TO']
BWEB="https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb"
TS={'1t':'051020261403','2t':'261020260742'}
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(BASE,"dados","secoes_2026_1t_2t.csv")
TMP=os.path.join(BASE,"tmp_bweb"); os.makedirs(TMP,exist_ok=True)
S={}
def load(tag):
    for uf in UFS:
        zp=os.path.join(TMP,f"{uf}_{tag}.zip"); ok=False
        for _ in range(4):
            try: urllib.request.urlretrieve(f"{BWEB}/bweb_{tag}_{uf}_{TS[tag]}.zip",zp); ok=True; break
            except Exception: time.sleep(3)
        if not ok: print("FALHA",tag,uf,flush=True); continue
        z=zipfile.ZipFile(zp); name=[n for n in z.namelist() if n.endswith(".csv")][0]
        with z.open(name) as raw:
            r=csv.reader(io.TextIOWrapper(raw,encoding="latin-1",newline=""),delimiter=";")
            h=next(r); ix={c:i for i,c in enumerate(h)}
            iC=ix["DS_CARGO_PERGUNTA"];iM=ix["CD_MUNICIPIO"];iZ=ix["NR_ZONA"];iS=ix["NR_SECAO"]
            iAp=ix["QT_APTOS"];iCp=ix["QT_COMPARECIMENTO"];iTv=ix["DS_TIPO_VOTAVEL"];iNm=ix["NM_VOTAVEL"];iV=ix["QT_VOTOS"]
            iTu=ix.get("CD_TIPO_URNA"); iCg=ix.get("CD_CARGA_1_URNA_EFETIVADA")
            for row in r:
                if row[iC].strip().upper()!="PRESIDENTE": continue
                k=(uf,row[iM].strip(),row[iZ].strip(),row[iS].strip())
                d=S.setdefault(k,{})
                p=d.setdefault(tag,{'ap':0,'cp':0,'L':0,'F':0,'B':0,'N':0,'nom':0,'tu':'','cg':''})
                p['ap']=int(row[iAp]); p['cp']=int(row[iCp])
                if iTu is not None: p['tu']=row[iTu].strip()
                if iCg is not None: p['cg']=row[iCg].strip()
                tv=row[iTv].strip().upper(); nm=row[iNm].strip().upper(); v=int(row[iV])
                if tv=="BRANCO": p['B']=v
                elif tv=="NULO": p['N']=v
                elif nm=="LULA": p['L']=v
                elif nm=="FLAVIO BOLSONARO": p['F']=v
                elif tv=="NOMINAL": p['nom']+=v          # outros candidatos (já exclui Lula e Flávio)
        z.close(); os.remove(zp); print(f"{tag} {uf} ok ({len(S)} seções)",flush=True)
load('1t'); load('2t')
with open(OUT,"w",newline="") as f:
    w=csv.writer(f); w.writerow(['uf','mun','zona','secao','ap1','cp1','L1','F1','O1','B1','N1','ap2','cp2','L2','F2','B2','N2','tu2','cg2'])
    n=0
    for (uf,mun,z,s),d in S.items():
        if '1t' not in d or '2t' not in d: continue
        a=d['1t']; b=d['2t']
        if a['cp']<=0 or b['cp']<=0: continue
        w.writerow([uf,mun,z,s,a['ap'],a['cp'],a['L'],a['F'],a['nom'],a['B'],a['N'],
                    b['ap'],b['cp'],b['L'],b['F'],b['B'],b['N'],b['tu'],b['cg']]); n+=1
print("salvo",OUT,"seções:",n)
