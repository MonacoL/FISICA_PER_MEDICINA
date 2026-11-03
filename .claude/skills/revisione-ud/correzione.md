# Ciclo di correzione

Dopo il primo giro di revisione, tocca a chi ha scritto la UD. Si fanno al massimo due giri di revisione; il secondo legge solo le correzioni.

## 1. Risposte

Per ogni rapporto del primo giro pubblica un commento di risposta nella PR, con `gh pr comment <numero> --body-file <file>`:

```markdown
## Risposte al <nome del revisore>, <UD> <parte>, giro 1
Rapporto: <link al commento del revisore>

| Rilievo | Gravità | Decisione | Che cosa cambia / motivo |
|---|---|---|---|
| FIS-1 | bloccante | accolto | `dispensa.tex:64`: 1/256 ≈ 0,4 % |
| FIS-7 | da correggere | respinto | <motivo: perché il testo va bene così> |
```

- Ogni rilievo del rapporto ha la sua riga: la tabella è completa quando le righe sono tante quanti i rilievi.
- Un bloccante si accoglie sempre.
- Un rilievo da correggere si respinge solo con un motivo che risponde al problema sollevato, non con «va bene così».
- Un suggerimento si può respingere con un motivo breve.

## 2. Correzioni

Applica tutte le correzioni accolte, poi rilancia `uv run controllo <ud>` finché passa. Fai un commit per giro, con il messaggio `Correzioni dal giro 1 della revisione (<ud> <parte>)`, e fai push. Il diff del secondo giro è `git diff <commit prima delle correzioni>..HEAD -- libro/<ud>/`.

## 3. Secondo giro

Rilancia **solo** i revisori che nel primo giro avevano almeno un bloccante; per gli altri il primo giro basta. Il prompt contiene UD, parte, la dicitura «secondo giro», i percorsi del primo giro (vedi `SKILL.md`, passo 3) e in più:

- il rapporto del revisore al primo giro e la tabella delle risposte, salvati in file;
- il diff delle correzioni, salvato in un file.

Pubblica il rapporto come al primo giro. Se nessun revisore aveva bloccanti, il secondo giro non si fa.

## 4. Stop

Dopo il secondo giro, se resta un bloccante (non risolto, o respinto con motivo non accettato), fermati: non correggere ancora e non lanciare un terzo giro. Scrivi nella PR un commento che elenca i bloccanti aperti con il link al rilievo, e avvisa l'autore, che decide come procedere.

## 5. Checklist della PR

Compila la descrizione della PR dal modello `.github/pull_request_template.md`, con `gh api -X PATCH repos/{owner}/{repo}/pulls/<numero> -F body=@<file>` (`gh pr edit` può fallire per un errore dei Projects classic):

- controllo automatico: spuntato se `uv run controllo <ud>` passa e la CI della PR è verde;
- una riga per revisore, con il numero di rilievi accolti e respinti e il link al commento del rapporto;
- l'elenco dei rilievi respinti, con gravità, motivo e link;
- il link al PDF prodotto dalla CI: l'artifact `pdf` dell'ultima esecuzione del workflow `Controllo` sul branch (`gh run list --branch <branch> --workflow Controllo --limit 1 --json databaseId`, poi `gh api repos/{owner}/{repo}/actions/runs/<id>/artifacts --jq '.artifacts[0].id'`; il link è `https://github.com/<owner>/<repo>/actions/runs/<id>/artifacts/<artifact>`).

Le caselle della rilettura restano vuote: le spunta l'autore.

Fatto quando ogni rilievo ha una risposta, il secondo giro è chiuso (o non serve, o si è fermato al passo 4) e la checklist è compilata.
