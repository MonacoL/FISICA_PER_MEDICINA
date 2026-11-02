# Ogni dispensa ed eserciziario passa per tre revisori indipendenti

Prima del merge, ogni PR di una dispensa o di un eserciziario viene letta da revisori separati: il revisore di fisica, il revisore studente e, per l'eserciziario, il revisore di formato. Nessuno di loro vede la conversazione in cui il testo è stato scritto: ricevono solo il PDF, i sorgenti e i riferimenti (Syllabus, `CONTEXT.md`, ADR 0004). Un solo revisore tende a guardare soltanto se i risultati sono giusti. Così sfuggono i passaggi saltati per chi studia da solo e i distrattori che non ingannano nessuno. La PR si unisce solo quando non restano rilievi bloccanti.

I rilievi stanno nei commenti della PR, non in file del repo. Servono a decidere quel merge. Dopo il merge, quello che conta è il testo corretto, e la storia della discussione resta comunque nella PR.

Nella prima stesura del libro l'autore non rilegge ogni PR: la unisce chi scrive, quando la revisione è chiusa senza bloccanti, e l'autore rilegge a mano il libro completo alla fine. Nella checklist della PR le caselle della rilettura dell'autore restano vuote, e la descrizione elenca le scelte di chi scrive e i dubbi dei revisori, da guardare per primi nella lettura finale.
