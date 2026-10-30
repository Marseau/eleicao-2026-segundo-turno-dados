import json, urllib.request, sys, asn1tools, pathlib

BASE = 'https://resultados.tse.jus.br/oficial'
ASN1 = sys.argv[1]           # caminho do bu.asn1
OUT  = pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
ZONA = sys.argv[3]; SECAO = sys.argv[4]
UF = 'pe'; MUN = '25216'     # Petrolina/PE, 1o turno 2026

def get(u):
    with urllib.request.urlopen(u, timeout=60) as r: return r.read()
def js(u): return json.loads(get(u))

config = js(BASE + '/comum/config/ele-c.json')
pleito = next(x for x in config['pl'] if x['dt'] == '25/10/2026' and x['c'] == 'ele2026')
cd = pleito['cd']; prefix = f'p{int(cd):06d}'
urnabase = f'{BASE}/{pleito["c"]}/arquivo-urna/{cd}'
local = f'{urnabase}/dados/{UF}/{MUN}/{ZONA}/{SECAO}'

aux = js(f'{local}/{prefix}-{UF}-m{MUN}-z{ZONA}-s{SECAO}-aux.json')
sel = [h for h in aux['hashes'] if h['st'].lower() == 'totalizado'][-1]
arqs = {a['tp']: a['nm'] for a in sel['arq']}
print('ARQUIVOS DA SECAO:', arqs)

# baixa todos os arquivos da seção (bu, assinatura, etc.)
for tp, nm in arqs.items():
    data = get(f'{local}/{sel["hash"]}/{nm}')
    (OUT / nm).write_bytes(data)
    print(f'  baixado {tp:10} {nm}  ({len(data)} bytes)')

# decodifica o BU
dec = asn1tools.compile_files(ASN1, codec='ber')
raw = (OUT / arqs['bu']).read_bytes()
env = dec.decode('EntidadeEnvelopeGenerico', raw)
bu  = dec.decode('EntidadeBoletimUrna', env['conteudo'])
i = bu['identificacaoSecao']
print('\nFASE:', bu['fase'], '| municipio/zona/secao:',
      i['municipioZona'], i['secao'])

# soma votos de PRESIDENTE (cargo codigo 1)
print('\nVOTOS NO BU (presidente):')
for e in bu['resultadosVotacaoPorEleicao']:
    for rv in e['resultadosVotacao']:
        cargo = rv['identificacaoVotacao']
        for tot in rv['totaisVotosCargo']:
            pass
# estrutura pode variar; imprime o bloco de presidente cru
import pprint
pres = None
for e in bu['resultadosVotacaoPorEleicao']:
    for rv in e['resultadosVotacao']:
        c = rv.get('identificacaoVotacao', {})
        if c.get('cargoConstitucional') == 'presidente' or c.get('codigoCargo', [None])[-1] == 1 or c == 1:
            pres = rv
# fallback: imprime chaves para a gente achar
print('CHAVES resultadosVotacao[0]:', list(bu['resultadosVotacaoPorEleicao'][0]['resultadosVotacao'][0].keys()))
