# Fisica per Medicina

Corso di Fisica in LaTeX per l'esame del semestre filtro di Medicina. Il vocabolario del progetto è in `CONTEXT.md`, le decisioni in `docs/adr/`.

## Ambiente

**Python** (grafici e controllo dei risultati numerici), con [uv](https://docs.astral.sh/uv/):

```sh
uv sync
```

**LaTeX** con [TinyTeX](https://yihui.org/tinytex/), che si installa nella home senza sudo:

```sh
wget -qO- "https://yihui.org/tinytex/install-bin-unix.sh" | sh
tlmgr update --self
tlmgr install $(cat tex-packages.txt)
```

TinyTeX mette i suoi comandi in `~/.local/bin`, che deve essere nel `PATH`. Se manca un pacchetto, `tlmgr search --global --file /nome.sty` dice in quale pacchetto si trova. Ogni nuovo pacchetto va aggiunto a `tex-packages.txt`.

## Controllo automatico

Compila con `latexmk` ogni unità didattica indicata e, una volta, il libro, e controlla i sorgenti. Stampa un rapporto con file e riga di ogni problema ed esce con un codice diverso da zero se:

- qualcosa non compila;
- c'è un `\ref` a un'etichetta che non esiste, o un'etichetta definita due volte;
- un `\usepackage` o `\RequirePackage` carica un pacchetto il cui pacchetto TeX Live non è in `tex-packages.txt` (per esempio `tabularx` sta in `tools`); i pacchetti del nucleo di TinyTeX non serve elencarli;
- restano `\todo{…}`, `TODO`, `FIXME`, `XXX`, `[[…]]` o `[DA …]` nei `.tex`, commenti compresi.

Gli overfull hbox oltre 5pt compaiono nel rapporto come avviso, senza far fallire il comando.

Prima di compilare, il comando legge la fonte degli esercizi di ogni UD (`libro/udN/esercizi.toml`, ADR 0006). Ne genera `libro/udN/generati/` (eserciziario e quesiti lampo, non versionati) e la pagina web `libro/build/web/udN.html`. Intanto ricalcola ogni risultato e controlla il formato dei quesiti. Un risultato che non torna, o un quesito fuori dalle regole, fa fallire il comando. Per compilare a mano con `latexmk` serve quindi aver lanciato prima `uv run controllo`. Il formato della fonte è descritto in testa a `libro/ud7/esercizi.toml`.

```sh
uv run controllo ud7          # oppure più UD: uv run controllo ud1 ud7
uv run pytest
```

La stessa cosa gira in CI su ogni PR (`.github/workflows/controllo.yml`), che pubblica i PDF come artifact `pdf` e le pagine web come artifact `web`.

## Licenza

- **Contenuti** (testo delle dispense, esercizi, soluzioni, figure, cioè i file in `libro/udN/` e i PDF che ne derivano): [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.it), testo completo in [`LICENSE`](LICENSE). Si possono copiare e adattare citando l'autore, senza scopi commerciali e con la stessa licenza.
- **Codice** (la classe `libro/fisica.cls`, la configurazione di compilazione, gli script Python): [MIT](LICENSE-CODE).

© 2026 Luca Monaco
