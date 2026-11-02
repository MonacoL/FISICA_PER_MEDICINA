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

Compila con `latexmk` ogni Unità didattica indicata e, una volta, il Libro. Stampa un rapporto ed esce con un codice diverso da zero se qualcosa non compila:

```sh
uv run controllo ud7          # oppure più UD: uv run controllo ud1 ud7
uv run pytest
```

La stessa cosa gira in CI su ogni PR (`.github/workflows/controllo.yml`), che pubblica i PDF come artifact `pdf`.

## Licenza

- **Contenuti** (testo delle Dispense, esercizi, soluzioni, figure, cioè i file in `libro/udN/` e i PDF che ne derivano): [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.it), testo completo in [`LICENSE`](LICENSE). Si possono copiare e adattare citando l'autore, senza scopi commerciali e con la stessa licenza.
- **Codice** (la classe `libro/fisica.cls`, la configurazione di compilazione, gli script Python): [MIT](LICENSE-CODE).

© 2026 Luca Monaco
