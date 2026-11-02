# Ogni Dispensa ed Eserciziario passa per tre Revisori indipendenti

Prima del merge, ogni PR di una Dispensa o di un Eserciziario viene letta da Revisori separati: il Revisore di fisica, il Revisore Studente e, per l'Eserciziario, il Revisore di formato. Nessuno di loro vede la conversazione in cui il testo è stato scritto: ricevono solo il PDF, i sorgenti e i riferimenti (Syllabus, `CONTEXT.md`, ADR 0004). Un solo revisore tende a guardare soltanto se i risultati sono giusti. Così sfuggono i passaggi saltati per chi studia da solo e i Distrattori che non ingannano nessuno. La PR si unisce solo quando non restano Rilievi Bloccanti.

I Rilievi stanno nei commenti della PR, non in file del repo. Servono a decidere quel merge. Dopo il merge, quello che conta è il testo corretto, e la storia della discussione resta comunque nella PR.
