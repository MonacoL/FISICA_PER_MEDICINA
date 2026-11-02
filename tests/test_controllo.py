"""Test del controllo automatico, invocato come lo invoca un utente: `uv run controllo`.

Ogni test costruisce un piccolo progetto LaTeX con la stessa struttura di `libro/`
(un `udN.tex` per UD e `libro.tex`) e controlla solo codice di uscita e rapporto.
"""

import subprocess
from pathlib import Path

import pytest

RADICE = Path(__file__).resolve().parent.parent

UD_VALIDA = r"""\documentclass{article}
\begin{document}
\input{ud1/ud1}
\end{document}
"""

LIBRO_VALIDO = r"""\documentclass{article}
\begin{document}
\input{ud1/ud1}
\end{document}
"""


def progetto(cartella: Path, file: dict[str, str]) -> Path:
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


@pytest.fixture
def progetto_valido(tmp_path: Path) -> Path:
    return progetto(
        tmp_path,
        {
            "ud1.tex": UD_VALIDA,
            "libro.tex": LIBRO_VALIDO,
            "ud1/ud1.tex": "Testo della prima Unità didattica.\n",
        },
    )


def test_progetto_valido_compila_ud_e_libro(progetto_valido: Path) -> None:
    esito = controllo("ud1", "--libro", str(progetto_valido))

    assert esito.returncode == 0, esito.stdout + esito.stderr
    assert "UD1: compila" in esito.stdout
    assert "Libro: compila" in esito.stdout


def test_errore_di_compilazione_fallisce_e_indica_il_file(tmp_path: Path) -> None:
    rotto = progetto(
        tmp_path,
        {
            "ud1.tex": UD_VALIDA,
            "libro.tex": LIBRO_VALIDO,
            "ud1/ud1.tex": "Testo.\n\n\\comandoinesistente\n",
        },
    )

    esito = controllo("ud1", "--libro", str(rotto))

    assert esito.returncode != 0
    assert "UD1: non compila" in esito.stdout
    assert "Libro: non compila" in esito.stdout
    assert "ud1/ud1.tex:3" in esito.stdout
