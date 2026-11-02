---
name: revisione-ud
description: Revisione di una Unità didattica prima del merge (ADR 0005). Controllo automatico, poi i Revisori indipendenti, poi i rapporti pubblicati nella PR. Da usare alla fine di un ticket di scrittura di una Dispensa o di un Eserciziario, o quando si chiede di rivedere una UD. Argomenti: UD e parte, es. "ud7 dispensa".
---

# Revisione di una Unità didattica

Argomenti: la UD (`ud7`) e la parte (`dispensa` | `eserciziario`). Se mancano, chiedili.

## Revisori per parte

| Parte | Revisori (agente) |
|---|---|
| Dispensa | Revisore di fisica (`revisore-fisica`) |
| Eserciziario | non ancora disponibile: fermati e dillo |

## Procedura

1. **PR.** Trova la PR del branch corrente con `gh pr view --json number,url`. Se non c'è, fermati: la revisione si pubblica in una PR, quindi va aperta prima.
2. **Controllo automatico.** Lancia `uv run controllo <ud>`. Se esce con codice diverso da zero, fermati e riporta il rapporto del comando: i Revisori leggono solo una UD che compila pulita. Se passa, il PDF è in `libro/build/<ud>.pdf`.
3. **Revisori.** Lancia in parallelo, con il tool Agent, un agente per ogni Revisore della tabella. Il prompt contiene solo UD, parte e questi percorsi, nient'altro:
   - `libro/build/<ud>.pdf`;
   - i sorgenti della parte: `libro/<ud>/dispensa.tex` o `libro/<ud>/eserciziario.tex`;
   - `docs/research/syllabus-fisica.md`, con l'indicazione della sezione della UD;
   - `CONTEXT.md` e `docs/adr/0004-calibrazione-sul-formato-esame.md`;
   - `.claude/skills/revisione-ud/rilievi.md`.

   Il Revisore è indipendente: il prompt non riassume la conversazione, non spiega le scelte di scrittura e non anticipa i problemi noti.
4. **Pubblicazione.** Per ogni rapporto: salvalo in un file temporaneo e pubblicalo così com'è con `gh pr comment <numero> --body-file <file>`, un commento per Revisore. Se un rapporto non segue il formato di `rilievi.md` (manca la gravità o la posizione di un Rilievo), rilancia quel Revisore una volta indicando che cosa manca.
5. **Esito.** Riporta il link di ogni commento e il conteggio dei Rilievi per gravità. Se c'è un Bloccante, la PR non si unisce: dillo.

Fatto quando ogni Revisore della tabella ha il suo commento nella PR.
