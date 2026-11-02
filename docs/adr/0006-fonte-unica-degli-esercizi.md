# Gli esercizi si scrivono una volta sola, in un file TOML per unità didattica

Problemi, quesiti d'esame e quesiti lampo di una UD stanno in `libro/udN/esercizi.toml`. Da lì `uv run controllo` genera il LaTeX dell'eserciziario e dei quesiti lampo, che la dispensa include, e la pagina web dell'eserciziario. Nello stesso passaggio ricalcola ogni risultato e controlla le regole di formato: un'opzione corretta e cinque opzioni, un commento per ogni distrattore, la risposta a completamento con la virgola e al massimo 16 caratteri. Senza una fonte unica, lo stesso esercizio vivrebbe in tre posti (testo, risultati rapidi, soluzione svolta), più la pagina web, e i numeri finirebbero per divergere.

Le scelte, provate sul prototipo del ticket #3 (branch `prototipo-3-fonte-esercizi`):

- **TOML** invece di YAML: la libreria standard di Python lo legge, e le stringhe letterali `'''…'''` lasciano intatto il LaTeX. Il prezzo è una sintassi un po' verbosa per le parti dei problemi (`[[problema.parte]]`).
- **I dati come segnaposto** (`{{mu}}`) nel testo, con il valore una volta sola in `dati`: testo e calcolo non possono divergere.
- **Il testo dei quesiti lampo** sta nella fonte degli esercizi, non nella dispensa, che lo include con `\input`.
- **Costanti arrotondate** come le usa lo studente (ln 2 = 0,69): il ricalcolo controlla il conto del libro, non quello della calcolatrice.

I file generati non sono versionati: li ricrea `uv run controllo` prima di compilare.
