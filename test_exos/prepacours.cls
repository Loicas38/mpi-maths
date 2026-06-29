\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{prepacours}[2025/06/15 Classe LaTeX pour cours de prépa - Modifiée]

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
\RequirePackage[normalem]{ulem}
\RequirePackage{etoolbox} % Pour la gestion avancée des commandes

% --- Configuration Géométrie ---
\geometry{
  top=2.5cm, bottom=2.5cm, left=2cm, right=2cm, % Marges standardisées pour exos
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

\newcounter{numexo}
\setcounter{numexo}{0}

% Style pour l'énoncé de l'exercice
\newtcolorbox[use counter=numexo]{exercicebox}[1][]{
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
  \hypertarget{exo:\thenumexo}{}
  \begin{exercicebox}[title={Exercice \thenumexo \hfill \hyperlink{sol:\thenumexo}{\small \faArrowRight~Voir correction}}]
}{
  \end{exercicebox}
}

% Environnement Correction
\newtcolorbox{correctionbox}[1][]{
  enhanced,
  colback=white,
  colframe=sectionblue,
  coltitle=sectionblue,
  fonttitle=\bfseries\large,
  title={Correction Exercice #1},
  detach title,
  before upper={\hypertarget{sol:#1}{}\textbf{\textcolor{sectionblue}{\faPen~Correction Exercice #1}} \hfill \hyperlink{exo:#1}{\small \faArrowUp~Retour énoncé}\par\vspace{0.5em}\hrule\vspace{0.5em}},
  boxrule=0pt,
  leftrule=3pt,
  sharp corners,
  breakable,
}

\newenvironment{correction}[1]{
  \begin{correctionbox}[#1]
}{
  \end{correctionbox}
}


% --- Commandes Mathématiques Standard ---
\renewcommand{\tagform@}[1]{#1}
\renewcommand{\theequation}{}
\newcommand{\R}{\mathbb{R}}
\newcommand{\N}{\mathbb{N}}
\newcommand{\C}{\mathbb{C}}
\newcommand{\Z}{\mathbb{Z}}
\newcommand{\Q}{\mathbb{Q}}
\newcommand{\dx}{\,\mathrm{d}x}
\newcommand{\dt}{\,\mathrm{d}t}

% --- En-têtes et Pieds de page ---
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{Suites et Séries de Fonctions}
\fancyhead[R]{\thepage}
\renewcommand{\headrulewidth}{0.5pt}

% --- Titres ---
\titleformat{\section}{\normalfont\Large\bfseries\color{sectionblue}}{\thesection}{1em}{}
\titleformat{\subsection}{\normalfont\large\bfseries\color{sectionblue}}{\thesubsection}{1em}{}

\endinput