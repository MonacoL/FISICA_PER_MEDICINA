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
- Nel testo del Libro (tutto ciò che finisce nel PDF) la maiuscola va solo a inizio frase e sui nomi propri. I termini del glossario sono nomi comuni: «esempio svolto», «quesito d'esame», «soluzione svolta», «unità didattica». Le maiuscole di `CONTEXT.md` servono a riconoscere i termini nei documenti del repo e nel testo per lo Studente non vanno usate.
