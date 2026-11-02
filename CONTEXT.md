# Corso di Fisica per il semestre filtro di Medicina

Corso di fisica in italiano per chi prepara l'esame di Fisica del semestre filtro di Medicina e Chirurgia. Copre tutto il syllabus e prepara al formato reale della prova.

## Language

### Fonti e riferimenti

**Syllabus**:
Il documento ufficiale «Syllabus semestre filtro – Insegnamento di Fisica», che elenca le unità didattiche e i loro contenuti. Stabilisce che cosa il corso deve coprire.
_Avoid_: programma, indice

**Prova d'esame**:
Una prova reale del semestre filtro, con risposta corretta e commento (es. la prova Alpha del 2° appello 2025/26). Stabilisce il livello di difficoltà e il registro delle spiegazioni.
_Avoid_: simulazione, test

**Fuori syllabus**:
Un argomento chiesto in una prova d'esame ma assente dal syllabus (es. numero di Reynolds, gas reali). Si tratta solo in un approfondimento.

### Struttura del corso

**Studente**:
L'unico lettore del corso: studia da solo, senza docente. Il corso non contiene materiale per chi insegna.
_Avoid_: allievo, utente, docente

**Unità didattica (UD)**:
Una delle sette parti del syllabus (UD1 Metodi … UD7 Radiazioni). È l'unità di organizzazione del corso.
_Avoid_: modulo, capitolo, lezione

**Libro**:
L'opera completa, con tutte le unità didattiche in ordine.
_Avoid_: volume, manuale

**Dispensa**:
La parte di teoria di una unità didattica: spiegazioni, figure, box ed esempi svolti.
_Avoid_: lezione, appunti, teoria

**Eserciziario**:
La parte di esercizi di una unità didattica: problemi su tre livelli, quesiti d'esame, risultati rapidi e soluzioni svolte.
_Avoid_: esercitazione, raccolta esercizi

### Esercizi

**Problema**:
Esercizio a risposta aperta dell'eserciziario, risolto con un calcolo.
_Avoid_: esercizio (come termine generico va bene, ma non per distinguere i tipi)

**Livello**:
Il grado di difficoltà di un problema: 1 = applicazione diretta di una formula; 2 = due passaggi, il primo risultato serve nel secondo; 3 = problema vero di media difficoltà, che combina più concetti, spesso in un contesto medico.
_Avoid_: difficoltà, grado

**Quesito d'esame**:
Esercizio nel formato della prova d'esame: a risposta multipla oppure a completamento.
_Avoid_: quiz, domanda

**Simulazione**:
Una prova completa nel formato ufficiale (31 quesiti d'esame su tutte le unità didattiche, da svolgere in 50 minuti), con le soluzioni. Sta in fondo al libro.
_Avoid_: compito, mock

**Risposta multipla**:
Quesito d'esame con cinque opzioni (A–E), di cui una sola corretta.

**Completamento**:
Quesito d'esame in cui lo studente completa una frase con un numero o una parola, scritti secondo le regole ufficiali.
_Avoid_: risposta aperta, fill-in

**Distrattore**:
Un'opzione sbagliata di un quesito a risposta multipla, costruita su un errore plausibile. La soluzione spiega perché è sbagliata.

**Risultati rapidi**:
Tabella dell'eserciziario con il solo risultato finale di ogni esercizio, per controllare subito la propria risposta.

**Fonte degli esercizi**:
Il file `esercizi.toml` di una unità didattica, dove problemi, quesiti d'esame e quesiti lampo si scrivono una volta sola, con i dati, il calcolo del risultato e la soluzione svolta. Da lì si generano l'eserciziario, i quesiti lampo della dispensa e la pagina web (ADR 0006).
_Avoid_: database, sorgente degli esercizi

**Soluzione svolta**:
La risoluzione completa di un esercizio: principio fisico, formula, conto con le unità e, per la risposta multipla, il commento a ogni distrattore.
_Avoid_: correzione

### Box della dispensa

**Formula**:
Box che riquadra una legge o una definizione da ricordare.
_Avoid_: formulario, riquadro

**Applicazione medica**:
Box che collega un argomento del syllabus a un fenomeno fisiologico o a una tecnica clinica. Un'applicazione medica di un argomento fuori syllabus va in approfondimento.

**Approfondimento**:
Box facoltativo: dimostrazioni, storia, curiosità e argomenti fuori syllabus.

**Esempio svolto**:
Esercizio risolto per intero dentro la dispensa, subito dopo il concetto che illustra.
_Avoid_: esercizio guidato

**Attenzione**:
Box che segnala un errore tipico o una trappola ricorrente nelle prove d'esame.
_Avoid_: errore tipico, warning

**Quesito lampo**:
Un quesito d'esame inserito nella dispensa subito dopo il concetto su cui verte. La sua soluzione svolta si trova nell'eserciziario della stessa unità didattica, non accanto alla domanda.

**Richiamo di matematica**:
Box che ripassa lo strumento matematico che serve in quel punto (potenze di 10, logaritmi, Pitagora, proporzionalità, pendenza e area di un grafico).
_Avoid_: prerequisito, ripasso

### Revisione

**Revisore**:
Un lettore indipendente che controlla una dispensa o un eserciziario prima del merge, senza aver visto come è stato scritto. Ce ne sono tre: il revisore di fisica (correttezza e copertura del syllabus), il revisore studente (chiarezza per chi studia da solo) e il revisore di formato (aderenza al formato della prova d'esame).
_Avoid_: correttore, referee

**Rilievo**:
Un singolo problema segnalato da un revisore, con posizione nel testo, gravità e correzione proposta.
_Avoid_: commento, osservazione, issue
