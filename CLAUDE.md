## Agent skills

### Issue tracker

Issues are tracked as GitHub issues via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` + `docs/adr/` at the root. See `docs/agents/domain.md`.

## Convenzioni

- I grafici si fanno in LaTeX (TikZ/pgfplots). Solo se è molto più semplice si genera un PDF da Python (matplotlib, via `uv run`) e lo si include.
- Ogni pacchetto LaTeX nuovo va aggiunto a `tex-packages.txt`.
- La maiuscola va solo a inizio frase e sui nomi propri, ovunque: nel testo del libro, nei documenti del repo (`CONTEXT.md`, ADR, ricerche, agenti e skill), in issue, PR e commit. I termini del glossario sono nomi comuni: «esempio svolto», «quesito d'esame», «soluzione svolta», «unità didattica», «revisore», «rilievo». In `CONTEXT.md` il termine è in grassetto solo all'inizio della sua voce.
