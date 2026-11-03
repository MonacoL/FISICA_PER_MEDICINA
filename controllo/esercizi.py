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


def numero(v: float, cifre: int, soglia: int = 5) -> str:
    """`v` con `cifre` cifre significative, virgola decimale, notazione siunitx (1,3e13) se
    l'esponente arriva a `soglia` o scende sotto -3 (sotto -2 se la soglia è più bassa)."""
    if v == 0:
        return "0"
    e = math.floor(math.log10(abs(v)))
    basso = -3 if soglia >= 5 else -2
    if e >= soglia or e < basso:
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
    # Per i risultati, notazione scientifica già da 10^3 e da 10^-3: è la forma delle soluzioni
    # svolte, e 1700 sembrerebbe avere 4 cifre significative.
    return grandezza(numero(float(r["valore"]), r["cifre"], soglia=3), r.get("unita"))


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


# Simulazioni: i 31 quesiti di una prova, divisi fra le UD in proporzione ai CFU del
# syllabus (6 CFU in tutto, quote arrotondate; il resto più grande va alla UD2).
QUOTE_UD = {1: 1, 2: 8, 3: 6, 4: 2, 5: 5, 6: 6, 7: 3}
FORMATO_PROVA = {"multipla": 21, "completamento": 10}


# Titolo di una \section o di una \subsection, anche con graffe annidate (\ang{90}).
TITOLO = re.compile(r"\\(?:sub)?section\*?\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}")


def titoli_dispense(cartella: Path) -> dict[int, set[str]]:
    """I titoli delle sezioni e delle sottosezioni di ogni dispensa: quelli che `sezione` può nominare."""
    titoli = {}
    for u in QUOTE_UD:
        dispensa = cartella / f"ud{u}" / "dispensa.tex"
        titoli[u] = set(TITOLO.findall(dispensa.read_text(encoding="utf-8"))) if dispensa.exists() else set()
    return titoli


def controlla_simulazioni(
    fonte: dict, nome: str, titoli: dict[int, set[str]] | None = None
) -> tuple[list[str], list[str]]:
    """Come `controlla`, più il formato di ogni prova: 21 + 10 quesiti e la ripartizione per UD.

    Con `titoli` (da `titoli_dispense`) controlla anche che la `sezione` di ogni quesito
    sia il titolo di una sezione o di una sottosezione della dispensa della sua UD.
    """
    errori, avvisi = controlla(fonte, nome)
    quesiti = fonte.get("quesito", [])
    for q in quesiti:
        if q.get("simulazione") not in (1, 2, 3) or q.get("ud") not in QUOTE_UD:
            errori.append(f"{nome}: qs:{q['id']}: servono simulazione (1-3) e ud (1-7)")
        elif "sezione" not in q:
            errori.append(f"{nome}: qs:{q['id']}: manca la sezione da ripassare")
        elif titoli is not None and q["sezione"] not in titoli.get(q["ud"], set()):
            errori.append(f"{nome}: qs:{q['id']}: «{q['sezione']}» non è un titolo della dispensa della UD{q['ud']}")
    for s in (1, 2, 3):
        prova = [q for q in quesiti if q.get("simulazione") == s]
        tipi = {t: sum(q["tipo"] == t for q in prova) for t in FORMATO_PROVA}
        if tipi != FORMATO_PROVA:
            errori.append(f"{nome}: simulazione {s}: {tipi} invece di {FORMATO_PROVA}")
        per_ud = {u: sum(q.get("ud") == u for q in prova) for u in QUOTE_UD}
        if per_ud != QUOTE_UD:
            avvisi.append(f"{nome}: simulazione {s}: quesiti per UD {per_ud} invece di {QUOTE_UD}")
        lettere = [q["corretta"] for q in prova if q["tipo"] == "multipla"]
        conti = {lettera: lettere.count(lettera) for lettera in LETTERE}
        if lettere and max(conti.values()) > 2 * max(1, min(conti.values())):
            avvisi.append(f"{nome}: simulazione {s}: lettere corrette sbilanciate, {conti}")
    return errori, avvisi


# --------------------------------------------------------------------------
# LaTeX


def opzioni_latex(q: dict) -> str:
    opzioni = [riempi(o["testo"], q.get("dati", {})) for o in q["opzione"]]
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
    # In ordine di livello, come li numera l'eserciziario: così risultati rapidi e soluzioni
    # svolte seguono la numerazione. Dentro un livello resta l'ordine della fonte.
    problemi = sorted(fonte.get("problema", []), key=lambda p: p["livello"])
    esame = [q for q in fonte.get("quesito", []) if not q.get("lampo")]
    lampo = [q for q in fonte.get("quesito", []) if q.get("lampo")]
    # Le sezioni vuote non si scrivono: una UD può avere per ora solo i quesiti lampo.
    out = ["% Generato da esercizi.toml: non modificare qui."]
    if problemi:
        out += ["", r"\section*{Problemi}"]
    for livello in (1, 2, 3):
        if not any(p["livello"] == livello for p in problemi):
            continue
        out += ["", rf"\livello{{{livello}}}{{{NOMI_LIVELLO[livello]}}}"]
        for p in (p for p in problemi if p["livello"] == livello):
            out += ["", rf"\problema\label{{pb:{p['id']}}}", riempi(p["testo"], p.get("dati", {}))]
            if len(p["parte"]) > 1:
                out += ["", *(x + "\n" for x in parti([riempi(parte["domanda"], p.get("dati", {})) for parte in p["parte"]]))]
    if esame:
        # Il titolo non resta da solo in fondo a una pagina.
        out += ["", r"\needspace{10\baselineskip}", r"\section*{Quesiti d'esame}"]
    for q in esame:
        # Testo e opzioni sulla stessa pagina, come all'esame.
        out += ["", r"\needspace{8\baselineskip}", rf"\quesito\label{{qe:{q['id']}}}", testo_quesito(q)]

    righe = []
    for p in problemi:
        # `rapido` sostituisce il risultato formattato quando la parte chiede più cose
        # (es. «140 m; spostamento nullo»); il controllo usa comunque `risultato`.
        risultati = [parte.get("rapido") or risultato_latex(parte["risultato"]) for parte in p["parte"]]
        valori = risultati[0] if len(risultati) == 1 else "; ".join(parti(risultati))
        righe.append(rf"Problema~\ref{{pb:{p['id']}}} & {valori} \\")
    righe += [rf"Quesito~\ref{{qe:{q['id']}}} & {risposta_breve(q)} \\" for q in esame]
    righe += [rf"Quesito lampo~\ref{{ql:{q['id']}}} & {risposta_breve(q)} \\" for q in lampo]
    out += ["", r"\section*{Risultati rapidi}", "", r"\begin{longtable}{@{}l>{\raggedright\arraybackslash}p{0.72\linewidth}@{}}",
            r"\toprule", r"Esercizio & Risultato \\", r"\midrule", r"\endhead", *righe,
            r"\bottomrule", r"\end{longtable}"]

    out += ["", r"\section*{Soluzioni svolte}"]
    if problemi:
        out += ["", r"\subsection*{Problemi}"]
    for p in problemi:
        out += ["", rf"\solproblema{{pb:{p['id']}}}"]
        soluzioni = [parte["soluzione"] for parte in p["parte"]]
        out += soluzioni if len(soluzioni) == 1 else [x + "\n" for x in parti(soluzioni)]
    if esame:
        out += ["", r"\subsection*{Quesiti d'esame}"]
    for q in esame:
        out += ["", rf"\solquesito{{qe:{q['id']}}}", soluzione_quesito(q)]
    if lampo:
        out += ["", r"\subsection*{Quesiti lampo}"]
    for q in lampo:
        out += ["", rf"\soluzionelampo{{ql:{q['id']}}}", soluzione_quesito(q)]
    return "\n".join(out) + "\n"



def prova(fonte: dict, s: int) -> list[dict]:
    """I quesiti della simulazione `s` nell'ordine della prova: prima le risposte multiple,
    poi i completamenti; dentro un tipo in ordine di UD, come il syllabus."""
    quesiti = [q for q in fonte.get("quesito", []) if q.get("simulazione") == s]
    return sorted(quesiti, key=lambda q: (q["tipo"] != "multipla", q["ud"]))


def righe_stimate(q: dict) -> int:
    """Una stima per eccesso delle righe che il quesito occupa in pagina, opzioni comprese:
    è lo spazio che \\needspace chiede, perché nessun quesito si spezzi fra due pagine."""

    def caratteri(s: str) -> int:
        # Nomi delle macro, graffe e dollari non si vedono in pagina.
        return len(re.sub(r"\\[a-zA-Z]+|[{}$]", "", s))

    righe = math.ceil((caratteri(riempi(q["testo"], q.get("dati", {}))) + 14) / 88)
    if q["tipo"] == "multipla":
        opzioni = [riempi(o["testo"], q.get("dati", {})) for o in q["opzione"]]
        if max(len(o) for o in opzioni) < 25:
            righe += 3
        else:
            righe += sum(math.ceil((caratteri(o) + 4) / 84) for o in opzioni) + 1
    return righe + 2


def simulazioni_latex(fonte: dict) -> str:
    out = ["% Generato da simulazioni/esercizi.toml: non modificare qui."]
    for s in (1, 2, 3):
        quesiti = prova(fonte, s)
        out += ["", rf"\simulazione{{{s}}}"]
        for q in quesiti:
            out += ["", rf"\needspace{{{righe_stimate(q)}\baselineskip}}", rf"\quesito\label{{qs:{q['id']}}}", testo_quesito(q)]
        righe = [rf"\ref{{qs:{q['id']}}} & {risposta_breve(q)} & {q['ud']} \\" for q in quesiti]
        out += ["", rf"\soluzionisimulazione{{{s}}}", "", r"\begin{longtable}{@{}lll@{}}",
                r"\toprule", r"Quesito & Risposta & UD \\", r"\midrule", r"\endhead", *righe,
                r"\bottomrule", r"\end{longtable}", "", r"\subsection*{Soluzioni svolte}"]
        for q in quesiti:
            out += ["", rf"\solquesito{{qs:{q['id']}}}(UD~{q['ud']}, «{q['sezione']}») ", soluzione_quesito(q)]
    return "\n".join(out) + "\n"

# --------------------------------------------------------------------------
# Web: lo stesso contenuto in una pagina con MathJax. Le macro siunitx dei testi
# sono ridefinite in MathJax; il resto del LaTeX in modo testo diventa HTML minimo.


# Il nome del libro in PDF accanto alle pagine web: `controllo` lo copia lì dopo averlo compilato.
PDF_WEB = "fisica-per-medicina.pdf"


def latex_a_html(testo: str) -> str:
    testo = html.escape(testo, quote=False)
    testo = re.sub(r"\\textbf\{([^}]*)\}", r"<b>\1</b>", testo)
    testo = re.sub(r"\\emph\{([^}]*)\}", r"<em>\1</em>", testo)
    testo = testo.replace(r"\completa", "______").replace("~", " ")
    # Le figure TikZ non si vedono nella pagina: al loro posto un rimando al PDF.
    testo = re.sub(
        r"\\begin\{center\}\s*\\input\{[^}]*\}\s*\\end\{center\}",
        '<p><em>(La figura è nel <a href="' + PDF_WEB + '" download>libro in PDF</a>.)</em></p>',
        testo,
    )
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
                    "domanda": latex_a_html(riempi(x.get("domanda", ""), p.get("dati", {}))),
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
                {"testo": latex_a_html(riempi(o["testo"], q.get("dati", {}))), "commento": latex_a_html(o.get("commento", ""))}
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


INDICE = Path(__file__).with_name("indice_esercizi.html")


def indice_web(cartella: Path) -> str:
    """La pagina indice: un collegamento per ogni fonte degli esercizi, le UD in ordine e le simulazioni in fondo."""
    fonti = sorted(cartella.glob("*/esercizi.toml"), key=lambda f: (f.parent.name == "simulazioni", f.parent.name))
    voci = []
    for fonte in fonti:
        ud = fonte.parent.name
        titolo = tomllib.loads(fonte.read_text(encoding="utf-8")).get("titolo", f"Eserciziario {ud.upper()}")
        voci.append(f'<li><a href="{ud}.html">{html.escape(titolo, quote=False)}</a></li>')
    return INDICE.read_text(encoding="utf-8").replace("<!--VOCI-->", "\n".join(voci))


# --------------------------------------------------------------------------


def genera(cartella: Path, ud: str) -> tuple[list[str], list[str]]:
    """Legge `cartella/ud/esercizi.toml`, scrive i file generati e restituisce (errori, avvisi).

    LaTeX in `ud/generati/` (eserciziario.tex e un lampo-<id>.tex per quesito lampo;
    simulazioni.tex per la cartella `simulazioni`),
    pagina web in `build/web/<ud>.html`, con l'indice di tutte in `build/web/index.html`.
    """
    sorgente = cartella / ud / "esercizi.toml"
    nome = f"{ud}/esercizi.toml"
    try:
        fonte = tomllib.loads(sorgente.read_text(encoding="utf-8"))
        simulazioni = ud == "simulazioni"
        if simulazioni:
            errori, avvisi = controlla_simulazioni(fonte, nome, titoli_dispense(cartella))
        else:
            errori, avvisi = controlla(fonte, nome)
    except (tomllib.TOMLDecodeError, KeyError, SyntaxError, NameError, ValueError) as e:
        return [f"{nome}: {type(e).__name__}: {e}"], []
    generati = cartella / ud / "generati"
    generati.mkdir(exist_ok=True)
    if simulazioni:
        (generati / "simulazioni.tex").write_text(simulazioni_latex(fonte), encoding="utf-8")
    else:
        (generati / "eserciziario.tex").write_text(eserciziario_latex(fonte), encoding="utf-8")
    for q in fonte.get("quesito", []):
        if q.get("lampo"):
            (generati / f"lampo-{q['id']}.tex").write_text(lampo_latex(q), encoding="utf-8")
    web = cartella / "build" / "web"
    web.mkdir(parents=True, exist_ok=True)
    titolo = fonte.get("titolo", f"Eserciziario {ud.upper()}")
    (web / f"{ud}.html").write_text(pagina_web(fonte, titolo), encoding="utf-8")
    (web / "index.html").write_text(indice_web(cartella), encoding="utf-8")
    return errori, avvisi
