\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{../commun/prepacours_TD}[2025/06/15 Classe LaTeX pour cours de prépa - Modifiée]

\LoadClass[a4paper,11pt]{article}

% --- Packages essentiels ---
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[french]{babel}
\RequirePackage{amsmath,amsthm,amssymb}
\RequirePackage{xcolor}
\RequirePackage[most]{tcolorbox}
\RequirePackage{geometry}
\RequirePackage{fancyhdr}
\RequirePackage{titlesec}
\RequirePackage{mathpazo}
\RequirePackage{hyperref}
\RequirePackage{tikz}
\RequirePackage{fontawesome5}
\RequirePackage{graphicx}
\RequirePackage{marginnote}
\RequirePackage{needspace}
\RequirePackage{atbegshi}
\RequirePackage[normalem]{ulem}
\RequirePackage{etoolbox} % Pour la gestion avancée des commandes
\RequirePackage{pgfplots}


% --- Configuration Géométrie ---
\geometry{
  top=3cm,
  bottom=2.5cm,
  left=2cm,
  right=2cm,
  headheight=30pt
}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.5em}

% --- Couleurs ---
\definecolor{bluebox}{RGB}{36,113,200}
\definecolor{redbox}{RGB}{231,35,35}
\definecolor{greenbox}{RGB}{60,150,200}
\definecolor{exobg}{RGB}{245,247,250} % Gris très clair pour fond exercice
\definecolor{exoframe}{RGB}{100,110,120} % Gris foncé pour cadre exercice
\definecolor{sectionblue}{RGB}{13, 114, 202}

% --- Compteurs et Chapitres ---
\newcounter{chapitre}
\renewcommand{\thechapitre}{\arabic{chapitre}}

\newcounter{coursenv}[chapitre]
\renewcommand{\thecoursenv}{\thechapitre.\arabic{coursenv}}

\newcommand{\annee}[1]{\gdef\@annee{#1}}
\newcommand{\filiere}[1]{\gdef\@filiere{#1}}
\newcommand{\etablissement}[1]{\gdef\@etablissement{#1}}
\newcommand{\auteur}[1]{\gdef\@auteur{#1}}

\newcommand{\@numchapitre}{}
\newcommand{\@titrechapitre}{}
\newcommand{\@annee}{}
\newcommand{\@filiere}{}
\newcommand{\@etablissement}{}
\newcommand{\@auteur}{}

\newcommand{\setchapitre}[1]{%
  \setcounter{chapitre}{#1}%
  \addtocounter{chapitre}{-1}%
  \refstepcounter{chapitre}%
  \setcounter{coursenv}{0}%
}

\newcommand{\chapitre}[2]{%
  \setchapitre{#1}%
  \gdef\@numchapitre{#1}%
  \gdef\@titrechapitre{#2}%
  \markboth{Chapitre #1 -- #2}{}%
}

% --- Styles Tcolorbox existants (Théorèmes etc) ---
\tcbset{
  thmbase/.style={
    enhanced, boxrule=0.8pt, arc=2pt,
    left=6pt, right=6pt, top=6pt, bottom=6pt,
    fonttitle=\bfseries
  },
  propstyle/.style={thmbase, colback=bluebox!5, colframe=bluebox},
  theoremstyle/.style={thmbase, colback=greenbox!5, colframe=greenbox},
  defstyle/.style={thmbase, colback=redbox!5, colframe=redbox},
}

% --- Nouveaux Environnements Exercice / Correction ---

\newcounter{numexo}[chapitre]
\renewcommand{\thenumexo}{\arabic{numexo}}

% Style pour l'énoncé de l'exercice
\newtcolorbox{exercicebox}[1][]{
  enhanced,
  colback=exobg,
  colframe=exoframe,
  coltitle=white,
  fonttitle=\bfseries\large,
  title={Exercice \thenumexo},
  attach boxed title to top left={xshift=5mm, yshift=-3mm},
  boxed title style={colback=exoframe, sharp corners},
  boxrule=0.5pt,
  top=10pt,
  breakable,
  #1
}

% Environnement Exercice (wrapper pour ajouter la cible hyperref)
\newenvironment{exercice}{
  \refstepcounter{numexo}
  \phantomsection % Assure une ancre correcte
  % Cible unique : exo.CHAPITRE.NUMERO (ex: exo.9.1)
  \hypertarget{exo.\arabic{chapitre}.\arabic{numexo}}{} 
  \begin{exercicebox}[title={Exercice \thenumexo \hfill \hyperlink{sol.\arabic{chapitre}.\arabic{numexo}}{\small \faArrowRight~Voir correction}}]
}{
  \end{exercicebox}
}

% Environnement Correction
\newtcolorbox{correctionbox}[1]{
  enhanced,
  colback=white,
  colframe=sectionblue,
  coltitle=sectionblue,
  fonttitle=\bfseries\large,
  title={Correction Exercice #1},
  detach title,
  before upper={%
    \phantomsection % Assure une ancre correcte
    % Cible unique : sol.CHAPITRE.NUMERO (utilise l'argument #1 donné par l'utilisateur)
    \hypertarget{sol.\arabic{chapitre}.#1}{}%
    \textbf{\textcolor{sectionblue}{\faPen~Correction Exercice #1}}%
    \hfill \hyperlink{exo.\arabic{chapitre}.#1}{\small \faArrowUp~Retour énoncé}\par\vspace{0.5em}\hrule\vspace{0.5em}%
  },
  boxrule=0pt,
  leftrule=3pt,
  sharp corners,
  breakable,
}

\newenvironment{correction}[1]{
  \begin{correctionbox}{#1}
}{
  \end{correctionbox}
}


% --- Commandes Mathématiques Standard ---
\renewcommand{\tagform@}[1]{#1}
\renewcommand{\theequation}{}



% --- En-têtes et Pieds de page ---
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\thepage}
\fancyhead[R]{Chapitre~\@numchapitre{} -- \@titrechapitre}
\renewcommand{\headrulewidth}{0.5pt}

\fancyfoot[L]{\@filiere}
\fancyfoot[C]{\@etablissement}
\fancyfoot[R]{\@auteur}

\fancypagestyle{premierepageschapitre}{%
  \fancyhf{}
  \setlength{\headheight}{70pt}
  \fancyhead[L]{\parbox[c][70pt][c]{14cm}{\fontsize{24}{28}\selectfont\bfseries\raggedright\@titrechapitre}}
  \fancyhead[R]{\parbox[c][70pt][c]{3cm}{\raggedleft\fontsize{50}{40}\selectfont\bfseries\color{sectionblue}\@numchapitre}}
  \renewcommand{\headrulewidth}{0.8pt}
  \renewcommand{\footrulewidth}{0pt}
}

% --- Titres ---
\@addtoreset{section}{chapitre}
\@addtoreset{subsection}{section}

\renewcommand{\thesection}{\thechapitre.\arabic{section}}
\renewcommand{\thesubsection}{\thesection.\arabic{subsection}}

\titleformat{\section}
  {\normalfont\LARGE\bfseries\color{sectionblue}}
  {\thesection}{1em}{}
  [\vspace{0.5em}]

\titlespacing*{\section}{-1.5em}{2ex plus 1ex minus .2ex}{1ex plus .2ex}

\titleformat{\subsection}
  {\normalfont\Large\bfseries}
  {\color{sectionblue}\thesubsection}{1em}{}
  [\vspace{0.3em}]

\titlespacing*{\subsection}{-3em}{2ex plus 1ex minus .2ex}{1ex plus .2ex}

\titleformat{\subsubsection}
  {\normalfont\large\bfseries}
  {\color{sectionblue}}{1em}{\uline}
  [\vspace{0.3em}]

\titlespacing*{\subsubsection}{2em}{2ex plus 1ex minus .2ex}{1ex plus .2ex}

\titlespacing*{\paragraph}{1.5em}{2ex plus 1ex minus .2ex}{1ex plus .2ex}

\endinput