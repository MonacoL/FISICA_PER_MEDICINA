# Rilievi: gravità e formato del rapporto

Vale per tutti i revisori. Il rapporto è il messaggio finale del revisore: la skill `revisione-ud` lo pubblica così com'è come commento nella PR.

## Gravità

- **Bloccante**: errore di fisica o di concetto; risultato numerico sbagliato; formula o unità di misura sbagliata; quesito con zero o due risposte corrette; voce del syllabus della UD non coperta. La PR non si unisce finché resta un bloccante.
- **Da correggere**: passaggio poco chiaro o saltato; esercizio che non si risolve con quello che il testo ha già spiegato; termine o simbolo usato prima di essere definito; richiamo di matematica mancante; distrattore debole; numeri di un quesito non calcolabili a mente; voce del syllabus coperta solo in parte; violazione delle regole di formato del completamento; maiuscola in mezzo alla frase su un nome comune, compresi i termini del glossario ("gli Esempi svolti" invece di "gli esempi svolti"). Chi scrive può respingerlo solo con il motivo.
- **Suggerimento**: stile, ordine dell'esposizione, figure migliorabili.

Nel dubbio fra due gravità, scegli la più alta e spiega il dubbio nel rilievo.

## Formato

```markdown
## <Nome del revisore> · <UD> <parte> · giro <1 | 2>

<Una riga: che cosa hai letto e quanti rilievi per gravità, es. "3 rilievi: 1 bloccante, 1 da correggere, 1 suggerimento".>

### <PREFISSO>-1 · <Gravità>
**Dove:** `libro/ud7/dispensa.tex:42` (PDF p. 3)
**Problema:** <che cosa non va, citando il testo o la formula>
**Correzione proposta:** <testo, formula o conto corretto, pronto da applicare>

### <PREFISSO>-2 · <Gravità>
...

<Sezioni aggiuntive richieste dal singolo revisore, es. la copertura del syllabus.>
```

- I rilievi sono numerati dal più grave al meno grave. Il prefisso identifica il revisore: `FIS` (fisica), `STU` (studente), `FOR` (formato). Chi scrive risponde citando l'identificativo, es. `FIS-2`.
- Ogni rilievo ha un solo problema e la sua posizione `file:riga` nel sorgente. Se si vede solo nel PDF (figura, impaginazione), indica la pagina del PDF e la riga del sorgente più vicina.
- Se non ci sono rilievi, il rapporto lo dice nella riga iniziale: "Nessun rilievo."

## Secondo giro

Il prompt lo dice, e ti dà il tuo rapporto del primo giro, le risposte di chi scrive e il diff delle correzioni.

- Rileggi solo le parti toccate dal diff, nel sorgente e nel PDF.
- Per ogni rilievo accolto del primo giro: è risolto? Se no, riportalo con lo stesso identificativo e la stessa gravità.
- Per ogni rilievo respinto: il motivo regge? Se un bloccante è stato respinto, riportalo come bloccante.
- Una correzione che introduce un errore nuovo è un rilievo nuovo, numerato dopo l'ultimo del primo giro.
- Prima dei rilievi, una sezione `### Esito del primo giro`: una riga per rilievo, `<ID>: risolto | non risolto | respinto, motivo accettato | respinto, motivo non accettato`.
