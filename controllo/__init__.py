"""Controllo automatico di una Unità didattica: compila la UD singola e il Libro."""

import argparse
import os
import re
import subprocess
import sys
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


def compila(libro: Path, sorgente: str) -> list[str]:
    """Compila `sorgente` dentro `libro` e restituisce gli errori trovati (vuota se compila)."""
    if not (libro / sorgente).exists():
        return [f"{sorgente} non esiste in {libro}"]
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
        cwd=libro,
        capture_output=True,
        text=True,
        # Righe del log non spezzate a 79 caratteri, così i percorsi restano interi.
        env={**os.environ, "max_print_line": "10000"},
    )
    if esito.returncode == 0:
        return []
    log = libro / "build" / Path(sorgente).with_suffix(".log")
    return errori(log) or [f"latexmk è uscito con codice {esito.returncode}"]


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="controllo",
        description="Compila con latexmk una Unità didattica e il Libro.",
    )
    parser.add_argument("ud", help="l'Unità didattica, per esempio ud7")
    parser.add_argument(
        "--libro",
        type=Path,
        default=RADICE / "libro",
        help="cartella del progetto LaTeX (predefinita: libro/)",
    )
    argomenti = parser.parse_args()
    ud = argomenti.ud.lower()

    riuscito = True
    for nome, sorgente in ((ud.upper(), f"{ud}.tex"), ("Libro", "libro.tex")):
        trovati = compila(argomenti.libro, sorgente)
        if not trovati:
            print(f"{nome}: compila")
            continue
        riuscito = False
        print(f"{nome}: non compila")
        for errore in trovati:
            print(f"  {errore}")
    sys.exit(0 if riuscito else 1)
