% fisica.cls — stile del Libro (ricostruito dai PDF UD7, ADR 0003)
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{fisica}[2026/11/02 Fisica per il semestre filtro]

\LoadClass[11pt,a4paper,oneside,openany]{book}

% --- Lingua, caratteri, pagina -------------------------------------------
\RequirePackage[T1]{fontenc}
\RequirePackage{lmodern}
\RequirePackage[italian]{babel}
\RequirePackage{microtype}
\RequirePackage[a4paper,top=2.5cm,bottom=2.5cm,left=2.4cm,right=2.4cm,headheight=14pt]{geometry}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.45em}

% --- Matematica e unità --------------------------------------------------
\RequirePackage{amsmath}
\RequirePackage{mathtools}
\RequirePackage{siunitx}
\sisetup{
  output-decimal-marker = {,},
  exponent-product      = \cdot,
  inter-unit-product    = \,,
  per-mode              = symbol,
  group-minimum-digits  = 5,
}
% nuclide: \nuclide{226}{88}{Ra}
\newcommand{\nuclide}[3]{\prescript{#1}{#2}{\mathrm{#3}}}

% --- Tabelle, liste, figure ----------------------------------------------
\RequirePackage{booktabs}
\RequirePackage{tabularx}
\RequirePackage[inline]{enumitem}
\setlist{itemsep=0.15em,topsep=0.3em}
\RequirePackage{caption}
\captionsetup{font=small,labelfont=bf}
\RequirePackage{tikz}
\usetikzlibrary{arrows.meta,decorations.pathreplacing,calc}
\RequirePackage{pgfplots}
\pgfplotsset{compat=1.18}

% --- Colori dei box ------------------------------------------------------
\RequirePackage{xcolor}
\definecolor{formula}{HTML}{1F4E79}       \definecolor{formulaBg}{HTML}{DCE6F2}
\definecolor{medica}{HTML}{2E6B30}        \definecolor{medicaBg}{HTML}{E6F0E3}
\definecolor{esempio}{HTML}{B5651D}       \definecolor{esempioBg}{HTML}{FDF0DF}
\definecolor{approfondimento}{HTML}{5B3E8A} \definecolor{approfondimentoBg}{HTML}{EEE8F5}
\definecolor{attenzione}{HTML}{A61B1B}    \definecolor{attenzioneBg}{HTML}{FBE5E3}
\definecolor{lampo}{HTML}{00707A}         \definecolor{lampoBg}{HTML}{E0F2F2}
\definecolor{richiamo}{HTML}{4A4A4A}      \definecolor{richiamoBg}{HTML}{EFEFEF}

% --- Intestazioni --------------------------------------------------------
\RequirePackage{titlesec}
\titleformat{\section}{\Large\bfseries}{\thesection}{1em}{}
\titleformat{\subsection}{\large\bfseries}{\thesubsection}{1em}{}
\titlespacing*{\section}{0pt}{1.4em}{0.6em}
\titlespacing*{\subsection}{0pt}{1.1em}{0.4em}

\RequirePackage{fancyhdr}
\newcommand{\udtitolo}{}
\newcommand{\parte}{}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small Fisica -- UD~\theunita: \udtitolo}
\fancyhead[R]{\small\parte}
\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[C]{\small\thepage}\renewcommand{\headrulewidth}{0pt}}

\RequirePackage[hidelinks]{hyperref}
\RequirePackage{bookmark}

% --- Unità didattica, Dispensa, Eserciziario -----------------------------
% Il numero dell'UD si fissa a mano: la numerazione è la stessa nel Libro
% e nella compilazione della singola UD (ADR 0001).
\let\theunita\thechapter
\newcounter{problema}[chapter]
\newcounter{quesito}[chapter]
\newcounter{quesitolampo}[chapter]
\renewcommand{\thequesitolampo}{\arabic{quesitolampo}}

% \unita{numero}{titolo}{sottotitolo}
\newcommand{\unita}[3]{%
  \clearpage
  \setcounter{chapter}{\numexpr#1-1\relax}%
  \refstepcounter{chapter}%
  \renewcommand{\udtitolo}{#2}%
  \addcontentsline{toc}{chapter}{UD~#1\quad #2}%
  \thispagestyle{plain}%
  \begin{center}
    \vspace*{1.5em}
    {\LARGE\bfseries Unità didattica #1\par}\vspace{0.6em}
    {\Large #2\par}\vspace{0.3em}
    {\normalsize #3\par}
    \vspace{1.5em}
  \end{center}}

\newcommand{\dispensa}{\renewcommand{\parte}{Dispensa}}

\newcommand{\eserciziario}[1]{%
  \clearpage
  \renewcommand{\parte}{Eserciziario}%
  \phantomsection\addcontentsline{toc}{section}{Eserciziario}%
  \thispagestyle{fancy}%
  \begin{center}
    {\LARGE\bfseries Eserciziario\par}\vspace{0.4em}
    {\large Unità didattica \theunita\ -- \udtitolo\par}\vspace{0.2em}
    {\normalsize #1\par}
  \end{center}}

% --- Box -----------------------------------------------------------------
\RequirePackage[most]{tcolorbox}
\tcbset{
  fisbox/.style 2 args={
    enhanced, breakable,
    colframe=#1, colback=#2, coltitle=white,
    fonttitle=\bfseries\small,
    boxrule=0.6pt, arc=2pt,
    left=10pt, right=10pt, top=4pt, bottom=4pt,
    toptitle=1.5pt, bottomtitle=1.5pt,
    before skip=0.8em, after skip=0.8em,
    before upper={\setlength{\parskip}{0.45em}},
  },
}

\NewDocumentEnvironment{applicazione}{m}
  {\begin{tcolorbox}[fisbox={medica}{medicaBg},title={Applicazione medica: #1}]}
  {\end{tcolorbox}}

\NewDocumentEnvironment{approfondimento}{m}
  {\begin{tcolorbox}[fisbox={approfondimento}{approfondimentoBg},title={Approfondimento: #1}]}
  {\end{tcolorbox}}

\NewDocumentEnvironment{esempio}{o}
  {\begin{tcolorbox}[fisbox={esempio}{esempioBg},
     title={\IfNoValueTF{#1}{Esempio svolto}{Esempio svolto: #1}}]}
  {\end{tcolorbox}}

\NewDocumentEnvironment{attenzione}{o}
  {\begin{tcolorbox}[fisbox={attenzione}{attenzioneBg},
     title={\IfNoValueTF{#1}{Attenzione}{Attenzione: #1}}]}
  {\end{tcolorbox}}

\NewDocumentEnvironment{richiamo}{m}
  {\begin{tcolorbox}[fisbox={richiamo}{richiamoBg},title={Richiamo di matematica: #1}]}
  {\end{tcolorbox}}

% Formula: il corpo è matematica (gather*). Ogni Formula finisce anche nel
% riepilogo che chiude la Dispensa (\riepilogoformule, ADR 0004).
\ExplSyntaxOn
\tl_new:N \g__fis_formule_tl
\NewDocumentEnvironment{formula}{o +b}
  {
    \IfNoValueTF{#1}
      { \begin{tcolorbox}[fisbox={formula}{formulaBg}, ams~gather*] #2 \end{tcolorbox} }
      { \begin{tcolorbox}[fisbox={formula}{formulaBg}, ams~gather*, title={#1}] #2 \end{tcolorbox} }
    \tl_gput_right:Nn \g__fis_formule_tl
      { \item[] \IfNoValueF{#1}{\textbf{#1}} \begin{gather*} #2 \end{gather*} }
  }
  {}
\NewDocumentCommand{\riepilogoformule}{}
  {
    \section*{Formule~da~ricordare}
    \addcontentsline{toc}{section}{Formule~da~ricordare}
    \begin{tcolorbox}[fisbox={formula}{formulaBg}]
      \begin{itemize}[leftmargin=0pt]
        \tl_use:N \g__fis_formule_tl
      \end{itemize}
    \end{tcolorbox}
    \tl_gclear:N \g__fis_formule_tl
  }
\ExplSyntaxOff

% Quesito lampo: la Soluzione svolta sta nell'Eserciziario della stessa UD.
% \begin{quesitolampo}{etichetta} ... \end{quesitolampo}
% \soluzionelampo{etichetta} nell'Eserciziario.
\NewDocumentEnvironment{quesitolampo}{m}
  {\begin{tcolorbox}[fisbox={lampo}{lampoBg},unbreakable,
     title={Quesito lampo~\refstepcounter{quesitolampo}\thequesitolampo\label{#1}}]}
  {\par\hfill{\small\itshape Soluzione svolta a pag.~\pageref{sol-#1}}
   \end{tcolorbox}}

\newcommand{\soluzionelampo}[1]{%
  \par\medskip\phantomsection\label{sol-#1}%
  \textbf{Quesito lampo~\ref{#1}} {\small(pag.~\pageref{#1})}.\ }

% --- Esercizi (provvisorio: il formato vero lo decide il ticket "Fonte unica
% degli esercizi") -------------------------------------------------------
\newcommand{\livello}[2]{\subsection*{Livello #1 -- #2}}
\newcommand{\problema}{%
  \par\medskip\refstepcounter{problema}\textbf{Problema~\theproblema.}\ }
\newcommand{\quesito}{%
  \par\medskip\refstepcounter{quesito}\textbf{Quesito~\thequesito.}\ }
\newcommand{\solproblema}[1]{\par\medskip\textbf{Problema~\ref{#1}.}\ }
\newcommand{\solquesito}[1]{\par\medskip\textbf{Quesito~\ref{#1}.}\ }

% Cinque opzioni su una riga: \opzioni{..}{..}{..}{..}{..}
\newcommand{\opzioni}[5]{%
  \par\smallskip
  \begin{tabularx}{\linewidth}{@{}*{5}{>{\raggedright\arraybackslash}X}@{}}
    \textbf{A)} #1 & \textbf{B)} #2 & \textbf{C)} #3 & \textbf{D)} #4 & \textbf{E)} #5
  \end{tabularx}\par}
% Cinque opzioni una per riga, per opzioni lunghe
\newenvironment{opzionilunghe}
  {\begin{enumerate}[label=\textbf{\Alph*)},leftmargin=2em]}
  {\end{enumerate}}
% Spazio per la risposta a Completamento
\newcommand{\completa}{\underline{\hspace{2.5cm}}}
