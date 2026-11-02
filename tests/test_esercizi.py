"""Test della fonte unica degli esercizi, attraverso `uv run controllo` come gli altri.

Ogni test costruisce una UD con la classe del libro, un `esercizi.toml` e una dispensa
che include il quesito lampo generato; controlla codice di uscita e rapporto.
"""

import shutil
from pathlib import Path

from test_controllo import RADICE, controllo

ESERCIZI = """\
[costanti]
ln2 = 0.69

[[problema]]
id = "ud1-mezzo"
livello = 1
testo = '''Uno strato ha coefficiente di attenuazione {{mu}}. Calcola lo spessore emivalente.'''
dati.mu = { valore = 0.35, unita = "cm^-1" }
  [[problema.parte]]
  calcolo = "ln2 / mu"
  risultato = { valore = 2.0, unita = "cm", cifre = 2 }
  soluzione = '''$x_{1/2} = 0{,}69/0{,}35 \\approx \\SI{2,0}{\\centi\\metre}$.'''

[[quesito]]
id = "ud1-somma"
tipo = "completamento"
testo = '''Due più due fa \\completa.'''
calcolo = "2 + 2"
risposta = "4"
soluzione = '''Si contano.'''

[[quesito]]
id = "ud1-lampo"
tipo = "multipla"
lampo = true
testo = '''Quanto fa $2 \\cdot 3$?'''
corretta = "C"
calcolo = "2 * 3"
soluzione = '''Si moltiplica.'''
  [[quesito.opzione]]
  testo = "4"
  commento = "Somma due volte 2."
  [[quesito.opzione]]
  testo = "5"
  commento = "Somma invece di moltiplicare."
  [[quesito.opzione]]
  testo = "6"
  valore = 6
  [[quesito.opzione]]
  testo = "8"
  commento = "Eleva al cubo il 2."
  [[quesito.opzione]]
  testo = "9"
  commento = "Eleva al quadrato il 3."
"""


def unita(cartella: Path, esercizi: str) -> Path:
    """Un progetto con la classe del libro e una UD1 fatta di dispensa ed eserciziario generati."""
    shutil.copy(RADICE / "libro" / "fisica.cls", cartella)
    testo = (
        "\\unita{1}{Prova}{Prova}\n\\dispensa\n\\input{ud1/generati/lampo-ud1-lampo}\n"
        "\\eserciziario{Prova}\n\\input{ud1/generati/eserciziario}\n"
    )
    documento = "\\documentclass{fisica}\n\\begin{document}\n\\input{ud1/ud1}\n\\end{document}\n"
    for percorso, contenuto in {
        "ud1.tex": documento,
        "libro.tex": documento,
        "ud1/ud1.tex": testo,
        "ud1/esercizi.toml": esercizi,
    }.items():
        (cartella / percorso).parent.mkdir(parents=True, exist_ok=True)
        (cartella / percorso).write_text(contenuto, encoding="utf-8")
    return cartella


def test_esercizi_validi_generano_latex_e_pagina_e_compilano(tmp_path: Path) -> None:
    esito = controllo("ud1", "--cartella", str(unita(tmp_path, ESERCIZI)))

    assert esito.returncode == 0, esito.stdout + esito.stderr
    assert "Esercizi UD1: tornano" in esito.stdout
    assert "UD1: compila" in esito.stdout
    assert (tmp_path / "build" / "web" / "ud1.html").is_file()


def test_risultato_che_non_torna_fallisce_e_indica_l_esercizio(tmp_path: Path) -> None:
    sbagliato = ESERCIZI.replace("valore = 2.0, unita", "valore = 2.5, unita")

    esito = controllo("ud1", "--cartella", str(unita(tmp_path, sbagliato)))

    assert esito.returncode != 0
    assert "ud1/esercizi.toml: pb:ud1-mezzo parte 1: il conto dà 1.971" in esito.stdout


def test_completamento_con_il_punto_decimale_fallisce(tmp_path: Path) -> None:
    sbagliato = ESERCIZI.replace('calcolo = "2 + 2"\nrisposta = "4"', 'calcolo = "2 + 2"\nrisposta = "4.0"')

    esito = controllo("ud1", "--cartella", str(unita(tmp_path, sbagliato)))

    assert esito.returncode != 0
    assert "qe:ud1-somma: risposta «4.0» fuori dalle regole del completamento" in esito.stdout


def test_distrattore_senza_commento_fallisce(tmp_path: Path) -> None:
    sbagliato = ESERCIZI.replace('  commento = "Eleva al cubo il 2."\n', "")

    esito = controllo("ud1", "--cartella", str(unita(tmp_path, sbagliato)))

    assert esito.returncode != 0
    assert "ql:ud1-lampo: il distrattore D non ha commento" in esito.stdout


def test_opzione_corretta_diversa_dal_conto_fallisce(tmp_path: Path) -> None:
    sbagliato = ESERCIZI.replace('corretta = "C"', 'corretta = "D"').replace(
        '  testo = "8"\n  commento = "Eleva al cubo il 2."', '  testo = "8"\n  valore = 8'
    ).replace('  testo = "6"\n  valore = 6', '  testo = "6"\n  commento = "Giusto, ma non è la corretta."')

    esito = controllo("ud1", "--cartella", str(unita(tmp_path, sbagliato)))

    assert esito.returncode != 0
    assert "ql:ud1-lampo: il conto dà 6, che non è l'opzione D" in esito.stdout


def test_figura_nel_testo_diventa_un_rimando_nella_pagina_web() -> None:
    from controllo.esercizi import latex_a_html

    html = latex_a_html("Prima.\n\\begin{center}\n\\input{ud2/figure/trazione}\n\\end{center}\nDopo.")
    assert "\\input" not in html and "\\begin{center}" not in html
    assert "La figura è nel libro in PDF." in html
