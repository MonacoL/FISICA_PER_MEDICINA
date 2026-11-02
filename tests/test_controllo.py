"""Test del controllo automatico, invocato come lo invoca un utente: `uv run controllo`.

Ogni test costruisce un piccolo progetto LaTeX con la stessa struttura di `libro/`
(un `udN.tex` per UD e `libro.tex`) e controlla solo codice di uscita e rapporto.
"""

import subprocess
from pathlib import Path

import pytest

RADICE = Path(__file__).resolve().parent.parent


def documento(*ud: str, preambolo: str = "") -> str:
    """Un `udN.tex` o un `libro.tex` minimo che include le UD indicate."""
    corpo = "".join(f"\\input{{{u}/{u}}}\n" for u in ud)
    return f"\\documentclass{{article}}\n{preambolo}\\begin{{document}}\n{corpo}\\end{{document}}\n"


def progetto(cartella: Path, preambolo: str = "", **testi: str) -> Path:
    """Scrive in `cartella` un progetto con una UD per ogni argomento (ud1="testo", ...)."""
    file = {f"{ud}.tex": documento(ud, preambolo=preambolo) for ud in testi}
    file["libro.tex"] = documento(*testi, preambolo=preambolo)
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
    valido = progetto(
        tmp_path,
        ud1="\\section{Prima}\\label{sec:prima}\nCome in sezione~\\ref{sec:prima}.\n",
    )

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


def test_riferimento_non_definito_fallisce_e_indica_file_e_etichetta(tmp_path: Path) -> None:
    rotto = progetto(tmp_path, ud1="Testo.\n\nVedi la sezione~\\ref{sec:assente}.\n")

    esito = controllo("ud1", "--cartella", str(rotto))

    assert esito.returncode != 0
    assert "UD1: compila" in esito.stdout
    assert "ud1/ud1.tex:3: riferimento non definito: sec:assente" in esito.stdout


def test_etichetta_definita_due_volte_fallisce_e_indica_i_file(tmp_path: Path) -> None:
    rotto = progetto(
        tmp_path,
        ud1="\\section{A}\\label{sec:doppia}\n",
        ud2="\\section{B}\n\\label{sec:doppia}\n",
    )

    esito = controllo("ud1", "ud2", "--cartella", str(rotto))

    assert esito.returncode != 0
    assert "ud1/ud1.tex:1: etichetta definita più volte: sec:doppia" in esito.stdout
    assert "ud2/ud2.tex:2: etichetta definita più volte: sec:doppia" in esito.stdout


@pytest.mark.parametrize(
    ("riga", "marcatore"),
    [
        ("\\todo{rivedere il conto}", "\\todo{"),
        ("% TODO: figura", "TODO"),
        ("% FIXME numero sbagliato", "FIXME"),
        ("% XXX", "XXX"),
        ("La dose vale [[valore]] Gy.", "[[valore]]"),
        ("La dose vale [DA VERIFICARE] Gy.", "[DA VERIFICARE]"),
    ],
)
def test_segnaposto_rimasto_fallisce_e_indica_file_e_marcatore(
    tmp_path: Path, riga: str, marcatore: str
) -> None:
    testo = "\\providecommand{\\todo}[1]{}\nTesto.\n" + riga + "\n"
    rotto = progetto(tmp_path, ud1=testo)

    esito = controllo("ud1", "--cartella", str(rotto))

    assert esito.returncode != 0
    assert f"ud1/ud1.tex:3: segnaposto rimasto: {marcatore}" in esito.stdout


def test_pacchetto_assente_dalla_lista_fallisce_e_indica_file_e_pacchetto(tmp_path: Path) -> None:
    rotto = progetto(tmp_path / "libro", preambolo="\\usepackage{booktabs}\n", ud1="Testo.\n")
    lista = tmp_path / "tex-packages.txt"
    lista.write_text("latexmk\n", encoding="utf-8")

    esito = controllo("ud1", "--cartella", str(rotto), "--pacchetti", str(lista))

    assert esito.returncode != 0
    assert "ud1.tex:2: pacchetto assente da tex-packages.txt: booktabs" in esito.stdout


def test_pacchetto_in_lista_col_nome_di_tex_live_passa(tmp_path: Path) -> None:
    # tabularx sta nel pacchetto TeX Live «tools», ed è quello che si scrive nella lista.
    valido = progetto(tmp_path / "libro", preambolo="\\usepackage{tabularx}\n", ud1="Testo.\n")
    lista = tmp_path / "tex-packages.txt"
    lista.write_text("latexmk\ntools\n", encoding="utf-8")

    esito = controllo("ud1", "--cartella", str(valido), "--pacchetti", str(lista))

    assert esito.returncode == 0, esito.stdout + esito.stderr


def test_overfull_oltre_soglia_e_un_avviso_che_non_fa_fallire(tmp_path: Path) -> None:
    largo = progetto(tmp_path, ud1="Testo.\n\n\\noindent\\rule{\\dimexpr\\textwidth+20pt}{1pt}\n")

    esito = controllo("ud1", "--cartella", str(largo))

    assert esito.returncode == 0, esito.stdout + esito.stderr
    assert "avviso: ud1/ud1.tex:3: overfull hbox di 20.0pt" in esito.stdout


def test_overfull_sotto_soglia_non_compare_nel_rapporto(tmp_path: Path) -> None:
    quasi = progetto(tmp_path, ud1="Testo.\n\n\\noindent\\rule{\\dimexpr\\textwidth+2pt}{1pt}\n")

    esito = controllo("ud1", "--cartella", str(quasi))

    assert esito.returncode == 0, esito.stdout + esito.stderr
    assert "overfull" not in esito.stdout


def test_overfull_dopo_un_input_indica_il_file_che_lo_contiene(tmp_path: Path) -> None:
    largo = progetto(
        tmp_path,
        ud1="Intro.\n\n\\input{ud1/parte}\n\nDopo.\n\n\\noindent\\rule{\\dimexpr\\textwidth+30pt}{1pt}\n\nFine.\n",
    )
    (largo / "ud1" / "parte.tex").write_text("Una parte breve.\n", encoding="utf-8")

    esito = controllo("ud1", "--cartella", str(largo))

    assert "avviso: ud1/ud1.tex:7: overfull hbox di 30.0pt" in esito.stdout


def test_overfull_di_una_scatola_esplicita_e_un_avviso(tmp_path: Path) -> None:
    largo = progetto(tmp_path, ud1="Testo.\n\n\\noindent\\hbox to 2cm{\\rule{3cm}{1pt}}\n\nFine.\n")

    esito = controllo("ud1", "--cartella", str(largo))

    assert esito.returncode == 0, esito.stdout + esito.stderr
    assert "avviso: ud1/ud1.tex:3: overfull hbox di" in esito.stdout


def test_pacchetti_sulla_stessa_riga_o_su_piu_righe_sono_controllati_tutti(tmp_path: Path) -> None:
    preambolo = "\\usepackage{amsmath}\\usepackage{booktabs}\n\\usepackage{amsmath,\n  multirow}\n"
    rotto = progetto(tmp_path / "libro", preambolo=preambolo, ud1="Testo.\n")
    lista = tmp_path / "tex-packages.txt"
    lista.write_text("latexmk\namsmath\n", encoding="utf-8")

    esito = controllo("ud1", "--cartella", str(rotto), "--pacchetti", str(lista))

    assert esito.returncode != 0
    assert "ud1.tex:2: pacchetto assente da tex-packages.txt: booktabs" in esito.stdout
    assert "ud1.tex:4: pacchetto assente da tex-packages.txt: multirow" in esito.stdout
