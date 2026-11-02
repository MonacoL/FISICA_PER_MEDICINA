"""Test del controllo automatico, invocato come lo invoca un utente: `uv run controllo`.

Ogni test costruisce un piccolo progetto LaTeX con la stessa struttura di `libro/`
(un `udN.tex` per UD e `libro.tex`) e controlla solo codice di uscita e rapporto.
"""

import subprocess
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent


def documento(*ud: str) -> str:
    """Un `udN.tex` o un `libro.tex` minimo che include le UD indicate."""
    corpo = "".join(f"\\input{{{u}/{u}}}\n" for u in ud)
    return f"\\documentclass{{article}}\n\\begin{{document}}\n{corpo}\\end{{document}}\n"


def progetto(cartella: Path, **testi: str) -> Path:
    """Scrive in `cartella` un progetto con una UD per ogni argomento (ud1="testo", ...)."""
    file = {f"{ud}.tex": documento(ud) for ud in testi}
    file["libro.tex"] = documento(*testi)
    file |= {f"{ud}/{ud}.tex": testo for ud, testo in testi.items()}
    for percorso, testo in file.items():
        destinazione = cartella / percorso
        destinazione.parent.mkdir(parents=True, exist_ok=True)
        destinazione.write_text(testo, encoding="utf-8")
    return cartella


def controllo(*argomenti: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", "--quiet", "controllo", *argomenti],
        cwd=RADICE,
        capture_output=True,
        text=True,
    )


def test_progetto_valido_compila_ud_e_libro(tmp_path: Path) -> None:
    valido = progetto(tmp_path, ud1="Testo della prima Unità didattica.\n")

    esito = controllo("ud1", "--cartella", str(valido))

    assert esito.returncode == 0, esito.stdout + esito.stderr
    assert "UD1: compila" in esito.stdout
    assert "Libro: compila" in esito.stdout


def test_errore_di_compilazione_fallisce_e_indica_il_file(tmp_path: Path) -> None:
    rotto = progetto(tmp_path, ud1="Testo.\n\n\\comandoinesistente\n")

    esito = controllo("ud1", "--cartella", str(rotto))

    assert esito.returncode != 0
    assert "UD1: non compila" in esito.stdout
    assert "Libro: non compila" in esito.stdout
    assert "ud1/ud1.tex:3" in esito.stdout


def test_piu_ud_compilano_tutte_e_il_libro_una_volta(tmp_path: Path) -> None:
    misto = progetto(tmp_path, ud1="\\comandoinesistente\n", ud2="Testo valido.\n")

    esito = controllo("ud1", "ud2", "--cartella", str(misto))

    assert esito.returncode != 0
    assert "UD1: non compila" in esito.stdout
    assert "UD2: compila" in esito.stdout
    assert esito.stdout.count("Libro:") == 1
