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
