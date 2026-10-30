# Pacote de reprodutibilidade — 2º turno presidencial de 2026

Tudo aqui usa **só dados públicos do TSE** e **só a biblioteca padrão do Python 3** (nada para instalar).
Qualquer pessoa pode rodar e conferir cada número do post. Se achar erro, aponte a linha.

## O que está aqui

```
pacote_post_2026/
  post.md                          o post (versão publicada)
  README.md                        este arquivo
  dados/
    secoes_2026_1t_2t.csv          497.897 seções: votos, comparecimento, branco/nulo nos 2 turnos (42 MB)
    pesquisas_2t_reta_final.csv    12 pesquisas de 2º turno da reta final, com fonte, amostra e rejeição
    agregador_rali_vespera.csv     agregador O Globo/Locomotiva da véspera
    candidatos_1t_2026.csv         votos nominais do 1º turno por candidato (base das regras de transferência)
  scripts/
    01_baixar_secoes_tse.py        (re)gera dados/secoes_2026_1t_2t.csv a partir do TSE  [download, ~1 h]
    02_excesso_por_municipio.py    excesso sobre o ambiente local; 97%; teste de sinal; Nula B  [30 s]
    03_monte_carlo_uniformidade.py "a moeda é honesta?" MC1/MC2/MC3  [minutos]
    04_estrutura_do_excesso.py     onde o excesso é maior; os 156 negativos  [20 s]
    05_modelo_congelado_e_pesquisas.py  as probabilidades com as premissas explícitas  [10 s]
    06_outliers_vs_vizinhas.py     seções que destoam do próprio local de votação  [download 2T, ~20 min]
    07_atraso_transmissao.py       atraso de transmissão x resultado, 497 mil seções  [download 2T, ~20 min]
    08_liberacao_manual_logs.py    liberações manuais nos logs de urna, 1T vs 2T  [precisa dos .logjez]
    util_baixar_uma_secao.py       baixa e decodifica os arquivos de uma seção (BU, log, etc.)
    util_candidatos_1t.py          soma os votos do 1T por candidato (gera candidatos_1t_2026.csv)
  resultados/                      saídas dos scripts (CSV por município etc.)
```

## Como rodar (ordem)

```bash
cd pacote_post_2026
python3 scripts/02_excesso_por_municipio.py
python3 scripts/03_monte_carlo_uniformidade.py 1000     # argumento = nº de simulações
python3 scripts/04_estrutura_do_excesso.py
python3 scripts/05_modelo_congelado_e_pesquisas.py
```
Os quatro acima rodam sobre o CSV incluído e reproduzem todos os números do post em poucos minutos.
Os scripts 01, 06, 07 e 08 baixam dados do TSE (grandes) e só são necessários para refazer o CSV
ou os testes complementares.

## Fontes dos dados

- Boletins de urna por seção (bweb): `https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/buweb/bweb_{1t|2t}_{UF}_{TS}.zip`
  com TS = `051020261403` (1º turno) e `261020260742` (2º turno). Cargo = PRESIDENTE.
- Arquivos de urna por seção (BU, RDV, log): `https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/{3220|3221}/...`
  (3220 = 1º turno, 04/10; 3221 = 2º turno, 25/10). O log de cada urna é cumulativo e contém os dois turnos; separar por data.
- Pesquisas: ver coluna `fonte` em `dados/pesquisas_2t_reta_final.csv`. Não houve boca de urna no 2º turno de 2026.

## Avisos importantes

1. **Coluna `O1` do CSV está zerada** (bug de uma versão anterior do script 01). Todos os scripts recalculam
   `outros = (cp1 - B1 - N1) - L1 - F1` e **não usam a coluna**. O script 01 incluído já está corrigido.
2. **Toda probabilidade é condicional às premissas.** O script 05 imprime as premissas e a sensibilidade.
   O único parâmetro que 2026 sozinho não calibra é o erro sistemático das pesquisas (todas errarem juntas);
   por isso o post mostra a resposta para vários valores dele em vez de escolher um.
3. **Classificação ideológica dos candidatos** (`campo_assumido` em `candidatos_1t_2026.csv`) é uma escolha, não um dado.
   Mude e rode o 05 de novo para ver o efeito.
4. **O que esta análise mede**: o comportamento dos resultados agregados. **O que não mede**: a origem do voto dentro da urna.
   Isso é objeto do Teste de Integridade do TSE (voto em papel sob câmera) e de auditoria técnica, não de estatística de resultado.

## Números-chave que os scripts devem reproduzir

| Script | Número |
|---|---|
| 02 | Excesso do Lula sobre o ambiente local: **+3,66 mi**; 97,1% dos municípios pró-Lula; z (sinal) = 69 |
| 02 | Nula B z>3: 2 municípios (~350 votos) contra ~7 esperados por acaso |
| 03 | MC1: 0 simulações chegam a 97%; deslocamento uniforme perfeito dá 100% (exclui o observado) |
| 04 | corr(excesso, força do Flávio 1T) = +0,59; 156 negativos, 120 no NE |
| 05 | Congelado: Lula 47,9% → P = 0; pesquisas: média 49,3%, P = 0,08% (s=0), 12,5% (s=2 pp); Laplace 11% |
