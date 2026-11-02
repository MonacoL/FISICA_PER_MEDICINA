"""Fonte unica degli esercizi (ADR 0006): da `udN/esercizi.toml` ai file LaTeX
dell'eserciziario e dei quesiti lampo, alla pagina web e al ricalcolo dei risultati.

Il formato è descritto in testa a `libro/ud7/esercizi.toml`.
"""

import html
import json
import math
import re
import tomllib
from pathlib import Path

LETTERE = "ABCDE"

# Unità scritte come testo semplice nella fonte: siunitx per il libro. Un'unità che
# non è qui passa a siunitx così com'è, come testo («giorni»).
UNITA = {
    "m": r"\metre",
    "cm": r"\centi\metre",
    "mm": r"\milli\metre",
    "nm": r"\nano\metre",
    "cm^-1": r"\centi\metre\tothe{-1}",
    "s": r"\second",
    "s^-1": r"\second\tothe{-1}",
    "h": r"\hour",
    "Hz": r"\hertz",
    "MHz": r"\mega\hertz",
    "GHz": r"\giga\hertz",
    "Bq": r"\becquerel",
    "kBq": r"\kilo\becquerel",
    "MBq": r"\mega\becquerel",
    "GBq": r"\giga\becquerel",
    "eV": r"\electronvolt",
    "keV": r"\kilo\electronvolt",
    "J": r"\joule",
    "W": r"\watt",
    "mW": r"\milli\watt",
    "W/m^2": r"\watt\per\metre\squared",
    "m/s": r"\metre\per\second",
    "D": "D",
}

NOMI_LIVELLO = {
    1: "Applicazione diretta delle formule",
    2: "Problemi a due passaggi",
    3: "Problemi di media difficoltà",
}

# Risposte a completamento: virgola decimale, al massimo 16 caratteri (ADR 0004).
REGOLA_COMPLETAMENTO = re.compile(r"^[0-9A-Za-zÀ-ú,/^x·+\-]{1,16}$")


# --------------------------------------------------------------------------
# Numeri e dati


def valore(d: dict) -> float:
    """Il valore di un dato: numero TOML, o stringa con la virgola per tenere le cifre ("0,50")."""
    v = d["valore"]
    return float(v.replace(",", ".")) if isinstance(v, str) else float(v)


def numero(v: float, cifre: int) -> str:
    """`v` con `cifre` cifre significative, virgola decimale, notazione siunitx (1,3e13) se serve."""
    if v == 0:
        return "0"
    e = math.floor(math.log10(abs(v)))
    if e >= 5 or e < -3:
        return f"{v / 10**e:.{cifre - 1}f}".replace(".", ",") + f"e{e}"
    return f"{v:.{max(cifre - 1 - e, 0)}f}".replace(".", ",")


def grandezza(n: str, unita: str | None) -> str:
    if unita is None:
        return rf"\num{{{n}}}"
    u = UNITA.get(unita, unita)
    opzioni = "[per-mode=power]" if "tothe" in u else ""
    return rf"\SI{opzioni}{{{n}}}{{{u}}}"


def dato_latex(d: dict) -> str:
    v = d["valore"]
    if isinstance(v, str):
        n = v
    else:
        n = numero(float(v), len(str(v).replace(".", "").replace("-", "").lstrip("0")) or 1)
    return grandezza(n, d.get("unita"))


def risultato_latex(r: dict) -> str:
    return grandezza(numero(float(r["valore"]), r["cifre"]), r.get("unita"))


def riempi(testo: str, dati: dict) -> str:
    return re.sub(r"\{\{(\w+)\}\}", lambda m: dato_latex(dati[m.group(1)]), testo)


def ambiente(fonte: dict, dati: dict) -> dict:
    env = {"math": math, **fonte.get("costanti", {})}
    env.update({nome: valore(d) for nome, d in dati.items()})
    return env


def uguale(calcolato: float, atteso: float, cifre: int) -> bool:
    return float(f"{calcolato:.{cifre}g}") == float(f"{atteso:.{cifre}g}")


# --------------------------------------------------------------------------
# Controlli


def controlla(fonte: dict, nome: str) -> tuple[list[str], list[str]]:
    """(errori, avvisi) sulla fonte: ricalcolo dei risultati e regole di formato."""
    errori, avvisi = [], []
    for p in fonte.get("problema", []):
        dove = f"{nome}: pb:{p['id']}"
        for i, parte in enumerate(p["parte"]):
            r = parte["risultato"]
            v = eval(parte["calcolo"], ambiente(fonte, p.get("dati", {})))
            if not uguale(v, r["valore"], r["cifre"]):
                errori.append(
                    f"{dove} parte {i + 1}: il conto dà {v:.4g}, il testo dichiara {float(r['valore']):g}"
                )
        if p["livello"] == 2 and len(p["parte"]) < 2:
            errori.append(f"{dove}: livello 2 con un solo passaggio")
    lettere = []
    for q in fonte.get("quesito", []):
        dove = f"{nome}: {'ql' if q.get('lampo') else 'qe'}:{q['id']}"
        env = ambiente(fonte, q.get("dati", {}))
        if q["tipo"] == "multipla":
            opzioni = q["opzione"]
            if len(opzioni) != 5:
                errori.append(f"{dove}: {len(opzioni)} opzioni invece di 5")
                continue
            k = LETTERE.index(q["corretta"])
            lettere.append(q["corretta"])
            for j, o in enumerate(opzioni):
                if j != k and "commento" not in o:
                    errori.append(f"{dove}: il distrattore {LETTERE[j]} non ha commento")
            if "calcolo" in q:
                v = eval(q["calcolo"], env)
                if "valore" not in opzioni[k] or not math.isclose(v, opzioni[k]["valore"], rel_tol=1e-9):
                    errori.append(f"{dove}: il conto dà {v:.4g}, che non è l'opzione {q['corretta']}")
        elif q["tipo"] == "completamento":
            risposta = q["risposta"]
            if not REGOLA_COMPLETAMENTO.match(risposta) or "." in risposta:
                errori.append(f"{dove}: risposta «{risposta}» fuori dalle regole del completamento")
            if "calcolo" in q:
                v = eval(q["calcolo"], env)
                if not math.isclose(v, float(risposta.replace(",", ".")), rel_tol=1e-9):
                    errori.append(f"{dove}: il conto dà {v:.4g}, la risposta è {risposta}")
        else:
            errori.append(f"{dove}: tipo «{q['tipo']}» sconosciuto (multipla | completamento)")
    conti = {lettera: lettere.count(lettera) for lettera in LETTERE}
    if lettere and max(conti.values()) > 2 * max(1, min(conti.values())):
        avvisi.append(f"{nome}: lettere corrette sbilanciate, {conti}")
    return errori, avvisi


# --------------------------------------------------------------------------
# LaTeX


def opzioni_latex(q: dict) -> str:
    opzioni = [o["testo"] for o in q["opzione"]]
    if max(len(o) for o in opzioni) < 25:
        return r"\opzioni" + "".join(f"{{{o}}}" for o in opzioni)
    righe = "\n".join(rf"  \item {o}" for o in opzioni)
    return f"\\begin{{opzionilunghe}}\n{righe}\n\\end{{opzionilunghe}}"


def testo_quesito(q: dict) -> str:
    testo = riempi(q["testo"], q.get("dati", {}))
    return testo + ("\n" + opzioni_latex(q) if q["tipo"] == "multipla" else "")


def risposta_breve(q: dict) -> str:
    return q["corretta"] if q["tipo"] == "multipla" else q["risposta"]


def soluzione_quesito(q: dict) -> str:
    if q["tipo"] == "multipla":
        testo = rf"\textbf{{Risposta {q['corretta']}.}} {q['soluzione']}"
        distrattori = [
            rf"  \item {LETTERE[j]}) {o['commento']}" for j, o in enumerate(q["opzione"]) if "commento" in o
        ]
        return testo + "\n\\begin{itemize}\n" + "\n".join(distrattori) + "\n\\end{itemize}"
    return rf"\textbf{{Risposta: {q['risposta']}.}} {q['soluzione']}"


def parti(p: dict) -> list[str]:
    return [f"({chr(97 + i)}) {x}" for i, x in enumerate(p)]


def lampo_latex(q: dict) -> str:
    return f"\\begin{{quesitolampo}}{{ql:{q['id']}}}\n{testo_quesito(q)}\n\\end{{quesitolampo}}\n"


def eserciziario_latex(fonte: dict) -> str:
    problemi = fonte.get("problema", [])
    esame = [q for q in fonte.get("quesito", []) if not q.get("lampo")]
    lampo = [q for q in fonte.get("quesito", []) if q.get("lampo")]
    out = ["% Generato da esercizi.toml: non modificare qui.", "", r"\section*{Problemi}"]
    for livello in (1, 2, 3):
        out += ["", rf"\livello{{{livello}}}{{{NOMI_LIVELLO[livello]}}}"]
        for p in (p for p in problemi if p["livello"] == livello):
            out += ["", rf"\problema\label{{pb:{p['id']}}}", riempi(p["testo"], p.get("dati", {}))]
            if len(p["parte"]) > 1:
                out += ["", *(x + "\n" for x in parti([parte["domanda"] for parte in p["parte"]]))]
    out += ["", r"\section*{Quesiti d'esame}"]
    for q in esame:
        out += ["", rf"\quesito\label{{qe:{q['id']}}}", testo_quesito(q)]

    righe = []
    for p in problemi:
        risultati = [risultato_latex(parte["risultato"]) for parte in p["parte"]]
        valori = risultati[0] if len(risultati) == 1 else "; ".join(parti(risultati))
        righe.append(rf"Problema~\ref{{pb:{p['id']}}} & {valori} \\")
    righe += [rf"Quesito~\ref{{qe:{q['id']}}} & {risposta_breve(q)} \\" for q in esame]
    righe += [rf"Quesito lampo~\ref{{ql:{q['id']}}} & {risposta_breve(q)} \\" for q in lampo]
    out += ["", r"\section*{Risultati rapidi}", "", r"\begin{longtable}{@{}ll@{}}",
            r"\toprule", r"Esercizio & Risultato \\", r"\midrule", r"\endhead", *righe,
            r"\bottomrule", r"\end{longtable}"]

    out += ["", r"\section*{Soluzioni svolte}", "", r"\subsection*{Problemi}"]
    for p in problemi:
        out += ["", rf"\solproblema{{pb:{p['id']}}}"]
        soluzioni = [parte["soluzione"] for parte in p["parte"]]
        out += soluzioni if len(soluzioni) == 1 else [x + "\n" for x in parti(soluzioni)]
    out += ["", r"\subsection*{Quesiti d'esame}"]
    for q in esame:
        out += ["", rf"\solquesito{{qe:{q['id']}}}", soluzione_quesito(q)]
    out += ["", r"\subsection*{Quesiti lampo}"]
    for q in lampo:
        out += ["", rf"\soluzionelampo{{ql:{q['id']}}}", soluzione_quesito(q)]
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# Web: lo stesso contenuto in una pagina con MathJax. Le macro siunitx dei testi
# sono ridefinite in MathJax; il resto del LaTeX in modo testo diventa HTML minimo.


def latex_a_html(testo: str) -> str:
    testo = html.escape(testo, quote=False)
    testo = re.sub(r"\\textbf\{([^}]*)\}", r"<b>\1</b>", testo)
    testo = re.sub(r"\\emph\{([^}]*)\}", r"<em>\1</em>", testo)
    testo = testo.replace(r"\completa", "______").replace("~", " ")
    pezzi = re.split(r"(\$[^$]*\$|\\\[.*?\\\])", testo, flags=re.S)
    for i in range(0, len(pezzi), 2):
        pezzi[i] = re.sub(
            r"(\\(?:SI|num|ang)(?:\[[^]]*\])?\{[^}]*\}(?:\{[^}]*\})?)", r"\\(\1\\)", pezzi[i]
        )
    return "".join(pezzi)


def esercizi_web(fonte: dict) -> list[dict]:
    voci = []
    for p in fonte.get("problema", []):
        voci.append({
            "tipo": "problema",
            "titolo": f"Problema · livello {p['livello']}",
            "testo": latex_a_html(riempi(p["testo"], p.get("dati", {}))),
            "parti": [
                {
                    "domanda": latex_a_html(x.get("domanda", "")),
                    "risultato": latex_a_html(risultato_latex(x["risultato"])),
                    "soluzione": latex_a_html(x["soluzione"]),
                }
                for x in p["parte"]
            ],
        })
    for q in fonte.get("quesito", []):
        voce = {
            "tipo": q["tipo"],
            "titolo": "Quesito lampo" if q.get("lampo") else "Quesito d'esame",
            "testo": latex_a_html(riempi(q["testo"], q.get("dati", {}))),
            "soluzione": latex_a_html(q["soluzione"]),
        }
        if q["tipo"] == "multipla":
            voce["opzioni"] = [
                {"testo": latex_a_html(o["testo"]), "commento": latex_a_html(o.get("commento", ""))}
                for o in q["opzione"]
            ]
            voce["corretta"] = LETTERE.index(q["corretta"])
        else:
            voce["risposta"] = q["risposta"]
        voci.append(voce)
    return voci


PAGINA = Path(__file__).with_name("pagina_esercizi.html")


def pagina_web(fonte: dict, titolo: str) -> str:
    dati = json.dumps(esercizi_web(fonte), ensure_ascii=False).replace("</", "<\\/")
    return PAGINA.read_text(encoding="utf-8").replace("<!--TITOLO-->", html.escape(titolo)).replace(
        "/*ESERCIZI*/[]", dati
    )


# --------------------------------------------------------------------------


def genera(cartella: Path, ud: str) -> tuple[list[str], list[str]]:
    """Legge `cartella/ud/esercizi.toml`, scrive i file generati e restituisce (errori, avvisi).

    LaTeX in `ud/generati/` (eserciziario.tex e un lampo-<id>.tex per quesito lampo),
    pagina web in `build/web/<ud>.html`.
    """
    sorgente = cartella / ud / "esercizi.toml"
    nome = f"{ud}/esercizi.toml"
    try:
        fonte = tomllib.loads(sorgente.read_text(encoding="utf-8"))
        errori, avvisi = controlla(fonte, nome)
    except (tomllib.TOMLDecodeError, KeyError, SyntaxError, NameError, ValueError) as e:
        return [f"{nome}: {type(e).__name__}: {e}"], []
    generati = cartella / ud / "generati"
    generati.mkdir(exist_ok=True)
    (generati / "eserciziario.tex").write_text(eserciziario_latex(fonte), encoding="utf-8")
    for q in fonte.get("quesito", []):
        if q.get("lampo"):
            (generati / f"lampo-{q['id']}.tex").write_text(lampo_latex(q), encoding="utf-8")
    web = cartella / "build" / "web"
    web.mkdir(parents=True, exist_ok=True)
    titolo = fonte.get("titolo", f"Eserciziario {ud.upper()}")
    (web / f"{ud}.html").write_text(pagina_web(fonte, titolo), encoding="utf-8")
    return errori, avvisi
