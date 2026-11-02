# Rilievi: gravità e formato del rapporto

Vale per tutti i Revisori. Il rapporto è il messaggio finale del Revisore: la skill `revisione-ud` lo pubblica così com'è come commento nella PR.

## Gravità

- **Bloccante**: errore di fisica o di concetto; risultato numerico sbagliato; formula o unità di misura sbagliata; Quesito con zero o due risposte corrette; voce del Syllabus della UD non coperta. La PR non si unisce finché resta un Bloccante.
- **Da correggere**: passaggio poco chiaro o saltato; Distrattore debole; numeri di un Quesito non calcolabili a mente; voce del Syllabus coperta solo in parte; violazione delle regole di formato del Completamento. Maiuscola in mezzo alla frase su un nome comune, compresi i termini del glossario ("gli Esempi svolti" invece di "gli esempi svolti"). Chi scrive può respingerlo solo con il motivo.
- **Suggerimento**: stile, ordine dell'esposizione, figure migliorabili.

Nel dubbio fra due gravità, scegli la più alta e spiega il dubbio nel Rilievo.

## Formato

```markdown
## <Nome del Revisore> · <UD> <Parte>

<Una riga: che cosa hai letto e quanti Rilievi per gravità, es. "3 Rilievi: 1 Bloccante, 1 Da correggere, 1 Suggerimento".>

### <PREFISSO>-1 · <Gravità>
**Dove:** `libro/ud7/dispensa.tex:42` (PDF p. 3)
**Problema:** <che cosa non va, citando il testo o la formula>
**Correzione proposta:** <testo, formula o conto corretto, pronto da applicare>

### <PREFISSO>-2 · <Gravità>
...

<Sezioni aggiuntive richieste dal singolo Revisore, es. la copertura del Syllabus.>
```

- I Rilievi sono numerati dal più grave al meno grave. Il prefisso identifica il Revisore: `FIS` (fisica), `STU` (Studente), `FOR` (formato). Chi scrive risponde citando l'identificativo, es. `FIS-2`.
- Ogni Rilievo ha un solo problema e la sua posizione `file:riga` nel sorgente. Se si vede solo nel PDF (figura, impaginazione), indica la pagina del PDF e la riga del sorgente più vicina.
- Se non ci sono Rilievi, il rapporto lo dice nella riga iniziale: "Nessun Rilievo."
