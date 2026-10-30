# Jogue uma moeda 5.395 vezes

Em 5.239 deu o mesmo lado.

Foi isso que aconteceu entre o 1º e o 2º turno de 2026: em **97% dos municípios do Brasil**, os votos novos pesaram para o mesmo candidato mais do que a própria cidade pesava. Acaso? A chance é de 1 em 10¹⁰⁰⁰. Moeda viciada.

A pergunta é: **o que viciou a moeda?**

Os dados estão aqui. Confira.

*Tudo abaixo vem de dados públicos do TSE e das pesquisas publicadas. Os dados, os scripts e o passo a passo estão em https://github.com/Marseau/eleicao-2026-segundo-turno-dados. Se encontrar um erro, aponte a linha.*

---

## 1. De onde vêm os números

Boletins de urna de **497.897 seções**, 1º e 2º turno, baixados do portal de dados abertos do TSE. As **12 pesquisas de 2º turno da reta final** (Datafolha, Quaest, PoderData, BTG/Nexus, Futura, Veritá, AtlasIntel, CNT/MDA, Real Time Big Data, Vox, Ipespe, Meio/Ideia), com instituto, data, amostra e link. Não houve boca de urna. Nenhum número aqui depende de confiar em alguém: todos se recalculam com os scripts do pacote.

## 2. Os fatos, sem adjetivo

| | |
|---|---|
| 1º turno (04/10) | Flávio 47,0% · Lula 45,2% · outros 7,8% |
| Histórico | Em 7 de 7 segundos turnos (1989–2022), quem liderou o 1º venceu |
| Pesquisas da véspera | 10 de 12 davam Flávio à frente; média: Flávio 50,7% · Lula 49,3% |
| Resultado (25/10) | **Lula 51,8% · Flávio 48,2%** |

A diferença entre a média das pesquisas e o resultado foi de **2,5 pontos**, todos os institutos errando para o mesmo lado. Esta foi a **primeira virada** de 2º turno presidencial no Brasil, a partir da **menor vantagem** de 1º turno da série (1,9 ponto; as anteriores iam de 5 a 23).

## 3. O que se moveu entre os turnos

Entre os dois turnos entraram em disputa 14 milhões de votos: os 9,3 mi de quem votou em outros candidatos, 1,8 mi de brancos e nulos que viraram voto e 2,9 mi de comparecimento a mais.

Fizemos a pergunta mais simples possível, urna por urna: **se esses votos novos se dividissem em cada urna exatamente como a própria urna já se dividia no 1º turno, quanto cada um ganharia?**

| | Esperado pelo ambiente de cada urna | Observado |
|---|---|---|
| Lula | +6,7 mi | **+10,3 mi** |
| Flávio | +7,4 mi | **+3,7 mi** |

Lula ficou **3,7 milhões de votos acima** do que o ambiente das urnas daria, e Flávio 3,7 milhões abaixo. Isso é da ordem da margem final (4,4 mi).

E isso aconteceu **em 97% dos 5.395 municípios**, com desvio médio de +2,4 pontos e dispersão de só 1,3 ponto. Se fosse moeda honesta, 97% de um lado em 5.395 lançamentos tem probabilidade da ordem de 10⁻¹⁰⁰⁰. **Não é acaso.** Existe uma causa nacional única, agindo em praticamente todo município.

## 4. As probabilidades, com as premissas na frente

Toda probabilidade depende do que se assume. Em vez de escolher por você, mostramos as opções:

| Premissa | Probabilidade do resultado |
|---|---|
| Ninguém muda de voto entre os turnos; eleitor de candidato de direita vai para Flávio (Cury e Renan 50/50) | **0** (o resultado exigiria 2,6 mi de votos migrando) |
| As 12 pesquisas estão certas e só diferem entre si por amostra | **0,08%** (1 em 1.200) |
| As pesquisas podem errar todas juntas em 1 ponto | 2,6% |
| … em 2 pontos | 12,5% (1 em 8) |
| … em 3 pontos | 21% |
| "Nunca houve virada" como taxa-base (0 em 7, regra de Laplace) | 11% de chance de virada |

Leitura honesta da tabela: **se pesquisas brasileiras não erram em bloco, o resultado tinha 1 chance em 1.200. Se podem errar 2 pontos em bloco, 1 em 8.** Qual das duas vale é a pergunta "quanto as pesquisas erram sistematicamente", e ela não se responde só com 2026.

A rejeição não muda isso: o resultado cabe dentro do teto de rejeição de todos os institutos (o mais apertado, PoderData, deixa 1,9 ponto de folga para Lula).

## 5. O que esses números excluem

- **Acaso.** Ver bloco 3.
- **Manipulação localizada.** Não há concentração por urna, por lote de carga, por modelo de urna nem por município. Os 2 municípios que destoam estatisticamente do movimento geral somam 350 votos. O atraso de transmissão dos boletins não tem relação com o resultado (correlação −0,02 em 497 mil seções). A taxa de liberação manual de eleitores é igual nos dois turnos e sobe com a idade da seção, não com o candidato.
- **Um ajuste mecânico uniforme.** Um acréscimo igual em todo lugar produziria 100% dos municípios na mesma direção. O observado tem **156 municípios indo para o outro lado**, **120 deles em redutos do Lula no Nordeste**. O excesso do Lula é maior justamente onde Flávio era mais forte e menor, até negativo, onde Lula já dominava. Essa é a forma de um bloco de eleitores com preferência própria se comportando como bloco, e não a forma de um número somado ao resultado.

## 6. O que esses números não decidem

**A causa.** Um eleitorado inteiro inclinando para o mesmo lado na última semana e uma interferência nacional uniforme produzem o mesmo 97%. A estatística dos resultados diz que a moeda não é honesta; não diz o que a viciou. Quem afirmar uma causa a partir destes números, em qualquer direção, está afirmando mais do que eles sustentam.

## 7. O que decidiria

1. **O tamanho histórico do erro em bloco das pesquisas brasileiras em 2º turno.** É o parâmetro que separa "1 em 1.200" de "1 em 8". Exige comparar com outras eleições, por isso está fora deste texto.
2. **A cobertura do Teste de Integridade de 2026** (urnas sorteadas votando em papel sob câmera) sobre o tipo de movimento aqui descrito.
3. **Evidência sobre o mecanismo dentro da urna**, que o resultado agregado não contém e nenhuma estatística de boletim substitui.

## 8. Qual a chance disso?

10 de 12 pesquisas davam Flávio. Em 7 de 7 eleições, quem liderou o 1º turno venceu. Lula virou.

Qual a chance? **Depende de uma única premissa**, e as duas respostas estão no bloco 4: se pesquisas não erram em bloco, **1 em 1.200**; se podem errar 2 pontos em bloco, **1 em 8**. Veja qual você aceita, e por quê.

Moeda viciada, isso os números provam. O que a viciou, eles não dizem. Quem disser que dizem está afirmando mais do que os dados sustentam.

## Reproduza

Pacote com os 497.897 boletins, as 12 pesquisas com link, os scripts e o passo a passo: https://github.com/Marseau/eleicao-2026-segundo-turno-dados. Quatro scripts rodam em minutos sobre o CSV incluído e imprimem cada número deste texto.

---

*Fontes das pesquisas e do histórico estão no pacote (`dados/pesquisas_2t_reta_final.csv`, `README.md`).*
