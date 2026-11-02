"""Controllo automatico delle Unità didattiche: compila ogni UD da sola e il Libro, controlla
riferimenti, etichette, pacchetti, segnaposto e overfull hbox."""

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent

# Con -file-line-error, LaTeX scrive gli errori come «./ud1/ud1.tex:3: messaggio».
ERRORE = re.compile(r"^(?:\./)?(\S+?\.(?:tex|cls|sty)):(\d+): (.*)$", re.MULTILINE)


def errori(log: Path) -> list[str]:
    if not log.exists():
        return [f"{log.name} non trovato: latexmk non ha avviato LaTeX"]
    testo = log.read_text(encoding="utf-8", errors="replace")
    return [
        f"{file}:{riga}: {messaggio}"
        for file, riga, messaggio in ERRORE.findall(testo)
        # La riga «==> Fatal error occurred» ripete solo la posizione dell'errore.
        if not messaggio.lstrip().startswith("==>")
    ]


# Avvisi di LaTeX sulle etichette: per ciascuno, che cosa cercare nei sorgenti
# per dire dove sta il problema, e come chiamarlo nel rapporto.
ETICHETTE = [
    (
        re.compile(r"LaTeX Warning: Reference `([^']+)' on page \d+ undefined"),
        r"\\\w*ref\*?\{{(?:[^}}]*,)?\s*{}\s*[,}}]",  # \ref{x}, \cref{a,x}
        "riferimento non definito",
    ),
    (
        re.compile(r"LaTeX Warning: Label `([^']+)' multiply defined"),
        r"\\label\{{{}\}}",
        "etichetta definita più volte",
    ),
]


# Note lasciate da chi scrive e che non devono arrivare allo Studente.
SEGNAPOSTO = re.compile(
    r"\\todo\s*[\[{]"  # \todo{...} o \todo[...]{...}
    r"|\b(?:TODO|FIXME|XXX)\b"
    r"|\[\[[^\]]*\]\]"  # [[valore]]
    r"|\[DA [A-ZÀ-Ü ]+\]"  # [DA COMPLETARE], [DA VERIFICARE]
)


# I pacchetti caricati direttamente: \usepackage[opzioni]{a,b} o \RequirePackage{c}.
CARICA = re.compile(r"^[^%]*?\\(?:usepackage|RequirePackage)\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}")

# Pacchetti TeX Live che TinyTeX installa sempre: non serve elencarli in tex-packages.txt.
NUCLEO = {"base", "graphics", "l3kernel", "latexconfig", "babel", "amsfonts"}


def righe(cartella: Path, *estensioni: str):
    """Ogni riga dei sorgenti di `cartella`, come («file:riga», testo); salta build/."""
    file = [f for estensione in estensioni for f in cartella.rglob(f"*{estensione}")]
    for sorgente in sorted(file):
        relativo = sorgente.relative_to(cartella)
        if "build" in relativo.parts:
            continue
        testo = sorgente.read_text(encoding="utf-8", errors="replace").splitlines()
        for numero, riga in enumerate(testo, start=1):
            yield f"{relativo.as_posix()}:{numero}", riga


def dove(cartella: Path, schema: re.Pattern[str]) -> list[str]:
    """Le posizioni «file:riga» dei sorgenti .tex di `cartella` in cui compare `schema`."""
    return [posizione for posizione, riga in righe(cartella, ".tex") if schema.search(riga)]


def pacchetto_tex_live(nome: str) -> str:
    """Il pacchetto TeX Live che contiene `nome`.sty, dalla cartella in cui sta (tabularx → tools)."""
    percorso = subprocess.run(
        ["kpsewhich", f"{nome}.sty"], capture_output=True, text=True
    ).stdout.strip()
    trovato = re.search(r"/tex/[^/]+/([^/]+)/", percorso)
    return trovato.group(1) if trovato else nome


def pacchetti_assenti(cartella: Path, lista: Path) -> list[str]:
    elencati = set(lista.read_text(encoding="utf-8").split()) | NUCLEO
    problemi = []
    for posizione, riga in righe(cartella, ".tex", ".cls", ".sty"):
        carica = CARICA.search(riga)
        if not carica:
            continue
        for nome in filter(None, (n.strip() for n in carica.group(1).split(","))):
            if pacchetto_tex_live(nome) not in elencati:
                problemi.append(f"{posizione}: pacchetto assente da {lista.name}: {nome}")
    return problemi


def etichette(cartella: Path, log: Path) -> list[str]:
    testo = log.read_text(encoding="utf-8", errors="replace")
    problemi = []
    for avviso, uso, motivo in ETICHETTE:
        for etichetta in sorted(set(avviso.findall(testo))):
            schema = re.compile(uso.format(re.escape(etichetta)))
            for posizione in dove(cartella, schema) or [log.name]:
                problemi.append(f"{posizione}: {motivo}: {etichetta}")
    return problemi


def segnaposti(cartella: Path) -> list[str]:
    return [f"{posizione}: segnaposto rimasto" for posizione in dove(cartella, SEGNAPOSTO)]


# Un overfull hbox più largo di così si vede nel margine: va nel rapporto come avviso.
SOGLIA_OVERFULL_PT = 5.0

# Nel log, «(./ud1/ud1.tex» apre un file e «)» lo chiude; gli overfull stanno in mezzo.
EVENTO = re.compile(
    # «in paragraph at lines 3--4», o «detected at line 3» per una \hbox esplicita.
    r"^Overfull \\hbox \((?P<pt>[\d.]+)pt too wide\).*?lines? (?P<riga>\d+)"
    r"|\((?P<apre>[^\s()]*)"
    r"|(?P<chiude>\))",
    re.MULTILINE,
)


def overfull(log: Path) -> list[str]:
    """Gli overfull hbox oltre soglia, con il file in cui stanno.

    Il file è quello aperto in cima alla pila. Ma se il paragrafo finisce dopo la fine
    del file, LaTeX chiude il file prima di scrivere l'avviso: allora è il file appena
    chiuso, purché abbia la riga indicata (altrimenti il paragrafo sta nel file sopra).
    """
    testo = log.read_text(encoding="utf-8", errors="replace")
    pila: list[str] = []
    appena_chiuso = None
    avvisi = []
    cartella = log.parent.parent

    def contiene(file: str | None, riga: int) -> bool:
        sorgente = cartella / file if file else None
        if not sorgente or not sorgente.is_file():
            return False
        return riga <= len(sorgente.read_text(encoding="utf-8", errors="replace").splitlines())

    for evento in EVENTO.finditer(testo):
        if evento["chiude"]:
            chiuso = pila.pop() if pila else ""
            appena_chiuso = chiuso if chiuso.endswith(".tex") else None
            continue
        if evento["apre"] is not None:
            pila.append(evento["apre"].removeprefix("./"))
            appena_chiuso = None
            continue
        riga = int(evento["riga"])
        aperto = next((f for f in reversed(pila) if f.endswith(".tex")), log.name)
        file = appena_chiuso if contiene(appena_chiuso, riga) else aperto
        appena_chiuso = None
        if float(evento["pt"]) > SOGLIA_OVERFULL_PT:
            avvisi.append(f"{file}:{evento['riga']}: overfull hbox di {evento['pt']}pt")
    return avvisi


@dataclass
class Esito:
    """Che cosa è venuto fuori da un documento: se compila, gli errori e gli avvisi."""

    compila: bool
    errori: list[str] = field(default_factory=list)
    avvisi: list[str] = field(default_factory=list)


def compila(cartella: Path, sorgente: str) -> Esito:
    """Compila `sorgente` dentro `cartella` e controlla il log."""
    if not (cartella / sorgente).exists():
        return Esito(False, [f"{sorgente} non esiste in {cartella}"])
    esito = subprocess.run(
        [
            "latexmk",
            "-pdf",
            "-outdir=build",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            sorgente,
        ],
        cwd=cartella,
        capture_output=True,
        text=True,
        # Righe del log non spezzate a 79 caratteri, così i percorsi restano interi.
        env={**os.environ, "max_print_line": "10000"},
    )
    log = cartella / "build" / Path(sorgente).with_suffix(".log")
    if esito.returncode != 0:
        return Esito(False, errori(log) or [f"latexmk è uscito con codice {esito.returncode}"])
    return Esito(True, etichette(cartella, log), overfull(log))


def rapporto(nome: str, esito: Esito) -> None:
    print(f"{nome}: {'compila' if esito.compila else 'non compila'}")
    for errore in esito.errori:
        print(f"  errore: {errore}")
    for avviso in esito.avvisi:
        print(f"  avviso: {avviso}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="controllo",
        description="Compila con latexmk ogni Unità didattica indicata e, una volta, il Libro.",
    )
    parser.add_argument("ud", nargs="+", help="le Unità didattiche, per esempio ud7")
    parser.add_argument(
        "--cartella",
        type=Path,
        default=RADICE / "libro",
        help="cartella del progetto LaTeX (predefinita: libro/)",
    )
    parser.add_argument(
        "--pacchetti",
        type=Path,
        default=RADICE / "tex-packages.txt",
        help="elenco dei pacchetti TeX Live installati in CI (predefinito: tex-packages.txt)",
    )
    argomenti = parser.parse_args()

    documenti = [(ud.upper(), f"{ud.lower()}.tex") for ud in argomenti.ud]
    documenti.append(("Libro", "libro.tex"))

    sorgenti = Esito(
        True,
        segnaposti(argomenti.cartella)
        + pacchetti_assenti(argomenti.cartella, argomenti.pacchetti),
    )
    print(f"Sorgenti: {'puliti' if not sorgenti.errori else 'da sistemare'}")
    for errore in sorgenti.errori:
        print(f"  errore: {errore}")
    riuscito = not sorgenti.errori
    for nome, sorgente in documenti:
        esito = compila(argomenti.cartella, sorgente)
        rapporto(nome, esito)
        riuscito = riuscito and not esito.errori
    sys.exit(0 if riuscito else 1)
