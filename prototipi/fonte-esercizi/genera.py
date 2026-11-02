"""PROTOTIPO (#3): dalla fonte unica degli esercizi a LaTeX, pagina web e ricalcolo.

    uv run python prototipi/fonte-esercizi/genera.py

Legge esercizi-ud7.toml e scrive in out/:
  eserciziario.tex   problemi, quesiti, risultati rapidi, soluzioni svolte
  lampo-<id>.tex     un quesito lampo, da \\input-are nella dispensa
  esercizi.html      l'eserciziario online, interattivo
e stampa il rapporto del ricalcolo. Esce con 1 se un controllo fallisce.
"""

import html
import json
import math
import re
import sys
import tomllib
from pathlib import Path

QUI = Path(__file__).parent
LETTERE = "ABCDE"

# Unità scritte come testo semplice nella fonte -> siunitx e testo per il web.
UNITA = {
    "cm": (r"\centi\metre", "cm"),
    "cm^-1": (r"\centi\metre\tothe{-1}", "cm⁻¹"),
    "h": (r"\hour", "h"),
    "MBq": (r"\mega\becquerel", "MBq"),
    "s": (r"\second", "s"),
}


# --------------------------------------------------------------------------
# Modulo puro: lettura, numeri, controlli. Nessun file scritto qui.

def valore(d: dict) -> float:
    """Il valore di un dato: numero TOML, o stringa con la virgola per tenere le cifre ("0,50")."""
    v = d["valore"]
    return float(v.replace(",", ".")) if isinstance(v, str) else float(v)


def numero(v: float, cifre: int) -> str:
    """v con `cifre` cifre significative, virgola decimale, notazione siunitx (1,3e13) se serve."""
    if v == 0:
        return "0"
    e = math.floor(math.log10(abs(v)))
    if e >= 5 or e < -3:
        m = v / 10**e
        return f"{m:.{cifre - 1}f}".replace(".", ",") + f"e{e}"
    return f"{v:.{max(cifre - 1 - e, 0)}f}".replace(".", ",")


def unita(nome: str, n: str) -> str:
    u = UNITA[nome][0]
    opz = "[per-mode=power]" if "tothe" in u else ""
    return rf"\SI{opz}{{{n}}}{{{u}}}"


def dato_latex(d: dict) -> str:
    v = d["valore"]
    n = v if isinstance(v, str) else numero(float(v), len(str(v).replace(".", "").lstrip("0")) or 1)
    return unita(d["unita"], n) if "unita" in d else rf"\num{{{n}}}"


def risultato_latex(r: dict) -> str:
    n = numero(float(r["valore"]), r["cifre"])
    return unita(r["unita"], n) if "unita" in r else rf"\num{{{n}}}"


def riempi(testo: str, dati: dict) -> str:
    return re.sub(r"\{\{(\w+)\}\}", lambda m: dato_latex(dati[m.group(1)]), testo)


def ambiente(fonte: dict, dati: dict) -> dict:
    env = {"math": math, **fonte.get("costanti", {})}
    env.update({k: valore(d) for k, d in dati.items()})
    return env


def uguale(calcolato: float, atteso: float, cifre: int) -> bool:
    return float(f"{calcolato:.{cifre}g}") == float(f"{atteso:.{cifre}g}")


REGOLA_COMPLETAMENTO = re.compile(r"^[0-9A-Za-zÀ-ú,/^x·+\-]{1,16}$")


def controlla(fonte: dict) -> list[str]:
    """Ogni riga è un problema trovato; lista vuota = tutto a posto."""
    errori = []
    for p in fonte.get("problema", []):
        for i, parte in enumerate(p["parte"]):
            r = parte["risultato"]
            v = eval(parte["calcolo"], ambiente(fonte, p.get("dati", {})))
            if not uguale(v, r["valore"], r["cifre"]):
                errori.append(f"pb:{p['id']} parte {i + 1}: il conto dà {v:.4g}, il testo dichiara {float(r['valore']):g}")
        if p["livello"] == 2 and len(p["parte"]) < 2:
            errori.append(f"pb:{p['id']}: livello 2 con un solo passaggio")
    lettere = []
    for q in fonte.get("quesito", []):
        dove = f"{'ql' if q.get('lampo') else 'qe'}:{q['id']}"
        env = ambiente(fonte, q.get("dati", {}))
        if q["tipo"] == "multipla":
            ops = q["opzione"]
            if len(ops) != 5:
                errori.append(f"{dove}: {len(ops)} opzioni invece di 5")
            k = LETTERE.index(q["corretta"])
            lettere.append(q["corretta"])
            for j, o in enumerate(ops):
                if j != k and "commento" not in o:
                    errori.append(f"{dove}: il distrattore {LETTERE[j]} non ha commento")
            if "calcolo" in q:
                v = eval(q["calcolo"], env)
                if "valore" not in ops[k] or not math.isclose(v, ops[k]["valore"], rel_tol=1e-9):
                    errori.append(f"{dove}: il conto dà {v:.4g}, che non è l'opzione {q['corretta']}")
        else:
            risp = q["risposta"]
            if not REGOLA_COMPLETAMENTO.match(risp) or "." in risp:
                errori.append(f"{dove}: risposta «{risp}» fuori dalle regole del completamento")
            if "calcolo" in q:
                v = eval(q["calcolo"], env)
                if not math.isclose(v, float(risp.replace(",", ".")), rel_tol=1e-9):
                    errori.append(f"{dove}: il conto dà {v:.4g}, la risposta è {risp}")
    conti = {L: lettere.count(L) for L in LETTERE}
    if lettere and max(conti.values()) > 2 * max(1, min(conti.values())):
        errori.append(f"lettere corrette sbilanciate: {conti} (avviso, conta solo a eserciziario completo)")
    return errori


# --------------------------------------------------------------------------
# LaTeX

def opzioni_latex(q: dict) -> str:
    ops = [o["testo"] for o in q["opzione"]]
    if max(len(o) for o in ops) < 25:
        return r"\opzioni" + "".join(f"{{{o}}}" for o in ops)
    righe = "\n".join(rf"  \item {o}" for o in ops)
    return f"\\begin{{opzionilunghe}}\n{righe}\n\\end{{opzionilunghe}}"


def testo_quesito(q: dict) -> str:
    t = riempi(q["testo"], q.get("dati", {}))
    return t + ("\n" + opzioni_latex(q) if q["tipo"] == "multipla" else "")


def risposta_breve(q: dict) -> str:
    return q["corretta"] if q["tipo"] == "multipla" else q["risposta"]


def soluzione_quesito(q: dict) -> str:
    if q["tipo"] == "multipla":
        s = rf"\textbf{{Risposta {q['corretta']}.}} {q['soluzione']}"
        distr = [rf"  \item {LETTERE[j]}) {o['commento']}" for j, o in enumerate(q["opzione"]) if "commento" in o]
        return s + "\n\\begin{itemize}\n" + "\n".join(distr) + "\n\\end{itemize}"
    return rf"\textbf{{Risposta: {q['risposta']}.}} {q['soluzione']}"


def lampo_latex(q: dict) -> str:
    return f"\\begin{{quesitolampo}}{{ql:{q['id']}}}\n{testo_quesito(q)}\n\\end{{quesitolampo}}\n"


def eserciziario_latex(fonte: dict, titolo: str) -> str:
    out = [f"\\eserciziario{{{titolo}}}", "", r"\section*{Problemi}"]
    nomi = {1: "Applicazione diretta delle formule", 2: "Problemi a due passaggi", 3: "Problemi di media difficoltà"}
    pb = fonte.get("problema", [])
    for liv in (1, 2, 3):
        out += ["", rf"\livello{{{liv}}}{{{nomi[liv]}}}"]
        for p in (p for p in pb if p["livello"] == liv):
            out += ["", rf"\problema\label{{pb:{p['id']}}}", riempi(p["testo"], p.get("dati", {}))]
            if len(p["parte"]) > 1:
                out += [f"({chr(97 + i)}) {parte['domanda']}" for i, parte in enumerate(p["parte"])]
    qe = [q for q in fonte.get("quesito", []) if not q.get("lampo")]
    ql = [q for q in fonte.get("quesito", []) if q.get("lampo")]
    out += ["", r"\section*{Quesiti d'esame}"]
    for q in qe:
        out += ["", rf"\quesito\label{{qe:{q['id']}}}", testo_quesito(q)]
    # Risultati rapidi
    righe = []
    for p in pb:
        rs = [risultato_latex(parte["risultato"]) for parte in p["parte"]]
        val = rs[0] if len(rs) == 1 else "; ".join(f"({chr(97 + i)}) {r}" for i, r in enumerate(rs))
        righe.append(rf"Problema~\ref{{pb:{p['id']}}} & {val} \\")
    righe += [rf"Quesito~\ref{{qe:{q['id']}}} & {risposta_breve(q)} \\" for q in qe]
    righe += [rf"Quesito lampo~\ref{{ql:{q['id']}}} & {risposta_breve(q)} \\" for q in ql]
    out += ["", r"\section*{Risultati rapidi}", "", r"\begin{center}", r"\begin{tabular}{@{}ll@{}}",
            r"\toprule", r"Esercizio & Risultato \\", r"\midrule", *righe, r"\bottomrule", r"\end{tabular}", r"\end{center}"]
    # Soluzioni svolte
    out += ["", r"\section*{Soluzioni svolte}", "", r"\subsection*{Problemi}"]
    for p in pb:
        out += ["", rf"\solproblema{{pb:{p['id']}}}"]
        if len(p["parte"]) == 1:
            out.append(p["parte"][0]["soluzione"])
        else:
            out += [f"({chr(97 + i)}) {parte['soluzione']}\n" for i, parte in enumerate(p["parte"])]
    out += ["", r"\subsection*{Quesiti d'esame}"]
    for q in qe:
        out += ["", rf"\solquesito{{qe:{q['id']}}}", soluzione_quesito(q)]
    out += ["", r"\subsection*{Quesiti lampo}"]
    for q in ql:
        out += ["", rf"\soluzionelampo{{ql:{q['id']}}}", soluzione_quesito(q)]
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# Web: lo stesso contenuto, in una pagina con MathJax (le macro siunitx usate
# dai testi sono ridefinite in MathJax, il testo LaTeX diventa HTML minimo).

def latex_a_html(t: str) -> str:
    t = html.escape(t, quote=False)
    t = re.sub(r"\\textbf\{([^}]*)\}", r"<b>\1</b>", t)
    t = re.sub(r"\\emph\{([^}]*)\}", r"<em>\1</em>", t)
    t = t.replace(r"\completa", "______")
    # \SI fuori dalla matematica: va messo fra \( \)
    parti = re.split(r"(\$[^$]*\$|\\\[.*?\\\])", t, flags=re.S)
    for i in range(0, len(parti), 2):
        parti[i] = re.sub(r"(\\(?:SI|num)(?:\[[^]]*\])?\{[^}]*\}(?:\{[^}]*\})?)", r"\\(\1\\)", parti[i])
    return "".join(parti)


def esercizi_web(fonte: dict) -> list[dict]:
    voci = []
    for p in fonte.get("problema", []):
        voci.append({
            "tipo": "problema", "titolo": f"Problema · livello {p['livello']}",
            "testo": latex_a_html(riempi(p["testo"], p.get("dati", {}))),
            "parti": [{"domanda": latex_a_html(x.get("domanda", "")),
                       "risultato": latex_a_html(risultato_latex(x["risultato"])),
                       "soluzione": latex_a_html(x["soluzione"])} for x in p["parte"]],
        })
    for q in fonte.get("quesito", []):
        v = {"tipo": q["tipo"], "titolo": ("Quesito lampo" if q.get("lampo") else "Quesito d'esame"),
             "testo": latex_a_html(riempi(q["testo"], q.get("dati", {}))),
             "soluzione": latex_a_html(q["soluzione"])}
        if q["tipo"] == "multipla":
            v["opzioni"] = [{"testo": latex_a_html(o["testo"]), "commento": latex_a_html(o.get("commento", ""))} for o in q["opzione"]]
            v["corretta"] = LETTERE.index(q["corretta"])
        else:
            v["risposta"] = q["risposta"]
        voci.append(v)
    return voci


PAGINA = (QUI / "pagina.html").read_text(encoding="utf-8")


def main() -> int:
    fonte = tomllib.loads((QUI / "esercizi-ud7.toml").read_text(encoding="utf-8"))
    out = QUI / "out"
    out.mkdir(exist_ok=True)
    errori = controlla(fonte)
    (out / "eserciziario.tex").write_text(eserciziario_latex(fonte, "Prototipo della fonte unica"), encoding="utf-8")
    for q in fonte.get("quesito", []):
        if q.get("lampo"):
            (out / f"lampo-{q['id']}.tex").write_text(lampo_latex(q), encoding="utf-8")
    dati = json.dumps(esercizi_web(fonte), ensure_ascii=False)
    (out / "esercizi.html").write_text(PAGINA.replace("/*ESERCIZI*/[]", dati), encoding="utf-8")
    print("Ricalcolo e controlli di formato:")
    for e in errori:
        print("  " + e)
    if not errori:
        print("  tutto torna")
    print(f"Scritti in {out}: eserciziario.tex, lampo-*.tex, esercizi.html")
    return 1 if [e for e in errori if "avviso" not in e] else 0


if __name__ == "__main__":
    sys.exit(main())
