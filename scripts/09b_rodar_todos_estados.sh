#!/bin/zsh
# Baixa o pacote de arquivos de urna de cada UF (2º turno 2026), processa os logs e apaga o pacote.
# Retomável: UFs já concluídas ficam marcadas em done.txt.
S="/private/tmp/claude-501/-Users-marseaufranco-Elei--es-2026/49250f6b-5ef4-4695-b3b9-0c59edc3d254/scratchpad"
D="$S/arqurna_dl"; OUT="$S/after17_BR.csv"; DONE="$D/done.txt"
mkdir -p "$D"; touch "$DONE"
BASE="https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/arqurnatot/bu_imgbu_logjez_rdv_vscmr_2026_2t"
for UF in AC RR AP RO TO MS SE DF AL MT AM RN PI ES PB MA GO SC PA PE CE PR RS BA RJ MG SP; do
  if grep -qx "$UF" "$DONE"; then echo "$UF já feito"; continue; fi
  echo "$(date +%H:%M:%S) $UF baixando"
  ok=0
  for i in 1 2 3 4 5 6; do
    if curl -sf -C - -o "$D/$UF.zip" "${BASE}_${UF}.zip"; then ok=1; break; fi
    echo "  tentativa $i falhou, aguardando"; sleep 20
  done
  if [ $ok -ne 1 ]; then echo "FALHA download $UF"; continue; fi
  echo "$(date +%H:%M:%S) $UF processando ($(du -h "$D/$UF.zip" | cut -f1))"
  if "$S/tools/venv/bin/python" -I "$S/tools/after17.py" "$D/$UF.zip" "$OUT"; then
    echo "$UF" >> "$DONE"; rm -f "$D/$UF.zip"; echo "$(date +%H:%M:%S) $UF concluído"
  else
    echo "FALHA processamento $UF"
  fi
done
echo "FIM_GERAL"
