---
name: revisione-ud
description: Revisione di una unità didattica prima del merge (ADR 0005). Controllo automatico, revisori indipendenti con i rapporti nella PR, poi risposte, correzioni, secondo giro e checklist. Da usare alla fine di un ticket di scrittura di una dispensa o di un eserciziario, o quando si chiede di rivedere una UD. Argomenti: UD e parte, es. "ud7 dispensa".
---

# Revisione di una unità didattica

Argomenti: la UD (`ud7`) e la parte (`dispensa` | `eserciziario`). Se mancano, chiedili.

## Revisori per parte

| Parte | Revisori (agente) |
|---|---|
| Dispensa | Revisore di fisica (`revisore-fisica`), revisore studente (`revisore-studente`) |
| Eserciziario | Revisore di fisica (`revisore-fisica`), revisore studente (`revisore-studente`), revisore di formato (`revisore-formato`) |

## Procedura

1. **PR.** Trova la PR del branch corrente con `gh pr view --json number,url`. Se non c'è, fermati: la revisione si pubblica in una PR, quindi va aperta prima.
2. **Controllo automatico.** Lancia `uv run controllo <ud>`. Se esce con codice diverso da zero, fermati e riporta il rapporto del comando: i revisori leggono solo una UD che compila pulita. Se passa, il PDF è in `libro/build/<ud>.pdf`.
3. **Revisori.** Lancia in parallelo, con il tool Agent, un agente per ogni revisore della tabella. Il prompt contiene solo UD, parte e questi percorsi, nient'altro:
   - `libro/build/<ud>.pdf`;
   - i sorgenti della parte: `libro/<ud>/dispensa.tex` o `libro/<ud>/eserciziario.tex`;
   - per un eserciziario, anche `libro/<ud>/dispensa.tex` come riferimento: è la dispensa già unita della stessa UD;
   - `docs/research/syllabus-fisica.md`, con l'indicazione della sezione della UD;
   - `CONTEXT.md` e `docs/adr/0004-calibrazione-sul-formato-esame.md`;
   - `.claude/skills/revisione-ud/rilievi.md`;
   - al revisore di formato, anche `docs/research/regole-esame-semestre-filtro.md`.

   Il revisore è indipendente: il prompt non riassume la conversazione, non spiega le scelte di scrittura e non anticipa i problemi noti.
4. **Pubblicazione.** Questo è il giro 1. Per ogni rapporto: salvalo in un file temporaneo e pubblicalo così com'è con `gh pr comment <numero> --body-file <file>`, un commento per revisore. Se un rapporto non segue il formato di `rilievi.md` (manca la gravità o la posizione di un rilievo), rilancia quel revisore una volta indicando che cosa manca.
5. **Esito.** Riporta il link di ogni commento e il conteggio dei rilievi per gravità. Se c'è un bloccante, la PR non si unisce: dillo.
6. **Correzione.** Rispondi ai rilievi, correggi, fai il secondo giro e compila la checklist seguendo `correzione.md`, nella stessa cartella di questa skill.

Fatto quando il passo 6 è chiuso secondo il criterio di `correzione.md`.
