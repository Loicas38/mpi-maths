\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{../commun/prepacours}[2026/03/21 Classe LaTeX unifiée Cours/Exos Prépa - Version liseuse]

\LoadClass[a4paper,14pt]{extarticle}

% =============================================================================
% PACKAGES
% =============================================================================
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[french]{babel}
\RequirePackage{amsmath,amsthm,amssymb}
\RequirePackage{mathrsfs}
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
\RequirePackage{etoolbox}
\RequirePackage{pgfplots}
\RequirePackage{titletoc}
\RequirePackage{microtype}
\RequirePackage{xurl}


\setcounter{tocdepth}{0} % Profondeur de la table des matières

% =============================================================================
% CONFIGURATION GÉOMÉTRIE
% =============================================================================
\geometry{
  top=1.7cm,
  bottom=1.9cm,
  left=1cm,
  right=1cm,
  marginparwidth=0pt,
  marginparsep=0pt,
  headheight=16pt
}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.35em}
\linespread{1.06}
\raggedbottom
\setlength{\emergencystretch}{2em}

\newcommand{\passerenmodeexos}{%
  \newgeometry{top=1.7cm, bottom=1.9cm, left=1.5cm, right=1.5cm, marginparwidth=0pt, marginparsep=0pt, headheight=16pt}%
  \fancyhfoffset[R]{0cm}%
}

\newcommand{\passerenmodecours}{%
  \newgeometry{top=1.7cm, bottom=1cm, left=0.5cm, right=0.5cm, marginparwidth=0pt, marginparsep=0pt, headheight=16pt}%
  \fancyhfoffset[R]{0cm}%
}

% =============================================================================
% COULEURS
% =============================================================================
\definecolor{bluebox}{RGB}{36,113,200}
\definecolor{redbox}{RGB}{231,35,35}
\definecolor{greenbox}{RGB}{60,150,200}
\definecolor{sectionblue}{RGB}{13, 114, 202}
\definecolor{examplebar}{RGB}{0,0,0}
\definecolor{ideabar}{RGB}{255,165,0}
\definecolor{exobg}{RGB}{245,247,250}
\definecolor{exoframe}{RGB}{100,110,120}

\hypersetup{
  colorlinks=true,
  linkcolor=sectionblue,
  citecolor=sectionblue,
  urlcolor=sectionblue,
  pdfstartview=FitH,
  pdfpagemode=UseOutlines
}

% =============================================================================
% COMPTEURS ET CHAPITRES
% =============================================================================
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

% =============================================================================
% STYLES TCOLORBOX
% =============================================================================
\tcbset{
  thmbase/.style={
    enhanced, boxrule=0.8pt, arc=2pt,
    left=6pt, right=6pt, top=6pt, bottom=6pt,
    fonttitle=\bfseries
  },
  propstyle/.style={thmbase, colback=bluebox!5, colframe=bluebox},
  theoremstyle/.style={thmbase, colback=greenbox!5, colframe=greenbox},
  defstyle/.style={thmbase, colback=redbox!5, colframe=redbox}
}

\newtcbtheorem[use counter=coursenv, number within=chapitre]{theoreme}{Théorème}{theoremstyle}{thm}
\newtcbtheorem[use counter=coursenv, number within=chapitre]{proposition}{Proposition}{propstyle}{prop}
\newtcbtheorem[use counter=coursenv, number within=chapitre]{corollaire}{Corollaire}{propstyle}{cor}
\newtcbtheorem[use counter=coursenv, number within=chapitre]{definition}{Définition}{defstyle}{def}
\newtcbtheorem[use counter=coursenv, number within=chapitre]{propriete}{Propriété}{propstyle}{propiete}

\newtcolorbox{theorement}[2][]{theoremstyle, fonttitle=\bfseries, title={Théorème~\refstepcounter{coursenv}\thecoursenv}, #1}
\newtcolorbox{propositionnt}[2][]{propstyle, fonttitle=\bfseries, title={Proposition~\refstepcounter{coursenv}\thecoursenv}, #1}
\newtcolorbox{corollairent}[2][]{propstyle, fonttitle=\bfseries, title={Corollaire~\refstepcounter{coursenv}\thecoursenv}, #1}
\newtcolorbox{definitionnt}[2][]{defstyle, fonttitle=\bfseries, title={Définition~\refstepcounter{coursenv}\thecoursenv}, #1}

\theoremstyle{remark}
\newtheorem*{remarque}{Remarque}

\newtcolorbox{exemple}[1][]{
  enhanced, breakable, enhanced jigsaw, pad at break=2mm,
  colback=white, colframe=white, boxrule=0pt,
  left=8pt, right=0pt, top=6pt, bottom=6pt,
  borderline west={2pt}{0pt}{examplebar},
  title={},
  before upper={\textbf{\color{examplebar}Exemple} \par\vspace{0.2em}},
  #1
}

\newcommand{\ampoule}{\faLightbulb}

\newcommand{\idee}[1]{%
  \needspace{5\baselineskip}%
  \begin{tcolorbox}[
    enhanced, breakable,
    colback=yellow!5, colframe=ideabar,
    boxrule=0.8pt, arc=2pt,
    left=5pt, right=5pt, top=5pt, bottom=5pt,
    fonttitle=\bfseries,
    title={\ampoule~Idée de la preuve},
    coltitle=white, colbacktitle=ideabar
  ]
  \small\raggedright #1
  \end{tcolorbox}%
}

\newcommand{\danger}[1]{%
  \needspace{5\baselineskip}%
  \begin{tcolorbox}[
    enhanced, breakable,
    colback=white, colframe=redbox,
    boxrule=0.8pt, arc=2pt,
    left=5pt, right=5pt, top=5pt, bottom=5pt,
    fonttitle=\bfseries,
    title={\skull~Attention !},
    coltitle=red, colbacktitle=white
  ]
  \small\raggedright #1
  \end{tcolorbox}%
}

\newcommand{\marginenote}[2]{%
  \needspace{5\baselineskip}%
  \begin{tcolorbox}[
    enhanced, breakable,
    colback=white, colframe=bluebox,
    boxrule=0.8pt, arc=2pt,
    left=5pt, right=5pt, top=5pt, bottom=5pt,
    fonttitle=\bfseries,
    title={#1},
    coltitle=sectionblue, colbacktitle=white
  ]
  \small\raggedright #2
  \end{tcolorbox}%
}


% =============================================================================
% ENVIRONNEMENTS EXERCICES & CORRECTIONS (CORRIGÉS)
% =============================================================================
\newcounter{numexo}[chapitre]
\renewcommand{\thenumexo}{\arabic{numexo}}

% Boîte Exercice interne
\newtcolorbox{exercicebox}[1][]{
  enhanced,
  colback=exobg, colframe=exoframe,
  coltitle=white, fonttitle=\bfseries\large,
  title={Exercice \thenumexo},
  attach boxed title to top left={xshift=5mm, yshift=-3mm},
  boxed title style={colback=exoframe, sharp corners},
  boxrule=0.5pt, top=10pt, breakable,
  #1
}

% Environnement Exercice
\newenvironment{exercice}{
  \refstepcounter{numexo}
  \phantomsection % Assure une ancre correcte
  % Cible unique : exo.CHAPITRE.NUMERO (ex: exo.9.1)
  \hypertarget{exo.\arabic{chapitre}.\arabic{numexo}}{} 
  \begin{exercicebox}[title={Exercice \thenumexo \hfill \hyperlink{sol.\arabic{chapitre}.\arabic{numexo}}{\small \faArrowRight~Voir correction}}]
}{
  \end{exercicebox}
}

% Boîte Correction interne (Argument MANDATOIRE cette fois pour éviter les erreurs)
\newtcolorbox{correctionbox}[1]{
  enhanced,
  colback=white, colframe=sectionblue,
  coltitle=sectionblue, fonttitle=\bfseries\large,
  title={Correction Exercice #1},
  detach title,
  before upper={%
    \phantomsection % Assure une ancre correcte
    % Cible unique : sol.CHAPITRE.NUMERO (utilise l'argument #1 donné par l'utilisateur)
    \hypertarget{sol.\arabic{chapitre}.#1}{}%
    \textbf{\textcolor{sectionblue}{\faPen~Correction Exercice #1}}%
    \hfill \hyperlink{exo.\arabic{chapitre}.#1}{\small \faArrowUp~Retour énoncé}\par\vspace{0.5em}\hrule\vspace{0.5em}%
  },
  boxrule=0pt, leftrule=3pt, sharp corners, breakable,
}

% Wrapper pour Correction
\newenvironment{correction}[1]{
  \begin{correctionbox}{#1}
}{
  \end{correctionbox}
}

% =============================================================================
% EN-TÊTES ET PIEDS DE PAGE
% =============================================================================
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\footnotesize Chapitre~\@numchapitre{} -- \@titrechapitre}
\fancyhead[R]{\footnotesize \thepage}
\fancyhfoffset[R]{0cm}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0pt}

%\fancyfoot[L]{}
%\fancyfoot[C]{\scriptsize \@filiere\enspace--\enspace\@etablissement}
%\fancyfoot[R]{}

\fancypagestyle{premierepageschapitre}{%
  \fancyhf{}
  \setlength{\headheight}{34pt}
  \fancyhead[L]{\parbox[c][34pt][c]{0.8\textwidth}{\Large\bfseries\raggedright\@titrechapitre}}
  \fancyhead[R]{\parbox[c][34pt][c]{0.15\textwidth}{\raggedleft\LARGE\bfseries\color{sectionblue}\@numchapitre}}
  \renewcommand{\headrulewidth}{0.4pt}
  \renewcommand{\footrulewidth}{0pt}
  \fancyhfoffset[R]{0cm}
}

\newcommand{\pagedegarde}{
  \newgeometry{top=2cm, bottom=2cm, left=2cm, right=2cm}
  \thispagestyle{empty}
  \begin{center}
    {\LARGE \bfseries Chapitre~\@numchapitre{} -- \@titrechapitre \par}
  \end{center}
    \vspace{0.5cm}
    \tableofcontents
    \vfill
  \begin{center}
    {\large Année \@annee \par}
    {\small Version du \today \par}
  \end{center}
  \newpage
  \passerenmodecours
  \thispagestyle{premierepageschapitre}
}

\newcommand{\restaurergeometrie}{%
  \clearpage
  \passerenmodecours
  \pagestyle{fancy}
}

% =============================================================================
% COMMANDES MATHS & TITRES
% =============================================================================
\renewcommand{\tagform@}[1]{#1}
\renewcommand{\theequation}{}


\@addtoreset{section}{chapitre}
\@addtoreset{subsection}{section} 

\renewcommand{\thesection}{\thechapitre.\arabic{section}}
\renewcommand{\thesubsection}{\thesection.\arabic{subsection}}

\renewcommand*\l@section{\@dottedtocline{1}{1.5em}{2.5em}}
\renewcommand*\l@subsection{\@dottedtocline{2}{4.5em}{3em}}

% Formatage personnalisé pour les chapitres dans la table des matières
\newcommand{\l@chapitre}[2]{%
  \vspace{0.5em}%
  \ifnum \c@tocdepth >\m@ne
    \addpenalty{-\@highpenalty}%
    \setlength\@tempdima{6em}% Largeur pour "Chapitre XX"
    \begingroup
      \parindent \z@ \rightskip \@pnumwidth
      \parfillskip -\@pnumwidth
      \leavevmode \bfseries\large
      \advance\leftskip\@tempdima
      \hskip -\leftskip
      {\textcolor{sectionblue}{#1}}\nobreak\
      \leaders\hbox{$\m@th\mkern \@dotsep mu\hbox{.}\mkern \@dotsep mu$}\hfill
      \nobreak\hb@xt@\@pnumwidth{\hss #2}\par
      \penalty\@highpenalty
    \endgroup
  \fi
  \vspace{0.2em}%
}

% Configuration hyperref pour le niveau chapitre
\providecommand{\toclevel@chapitre}{0}
\providecommand{\toclevel@section}{1}
\providecommand{\toclevel@subsection}{2}

\titleformat{\section}
  {\normalfont\Large\bfseries\color{sectionblue}}
  {\thesection}{1em}{}
  [\vspace{0.35em}]

\titlespacing*{\section}{0em}{1.4ex plus .7ex minus .2ex}{0.8ex plus .2ex}

\titleformat{\subsection}
  {\normalfont\large\bfseries}
  {\color{sectionblue}\thesubsection}{1em}{}
  [\vspace{0.2em}]

\titlespacing*{\subsection}{0em}{1.2ex plus .7ex minus .2ex}{0.6ex plus .2ex}

\titleformat{\subsubsection}
  {\normalfont\large\bfseries}
  {\color{sectionblue}}{1em}{\uline}
  [\vspace{0.3em}]

\titlespacing*{\subsubsection}{0em}{1.2ex plus .7ex minus .2ex}{0.6ex plus .2ex}

\titlespacing*{\paragraph}{0em}{1.2ex plus .7ex minus .2ex}{0.6ex plus .2ex}

% Commande pour démarrer un chapitre dans le document intégral
% (sans page de garde ni table des matières propre au chapitre)
\newcommand{\chapitreintegral}[2]{%
  \clearpage
  \passerenmodecours % S'assure d'être en géométrie "Cours" (avec marge)
  \setchapitre{#1}%
  \gdef\@numchapitre{#1}%
  \gdef\@titrechapitre{#2}%
  \markboth{Chapitre #1 -- #2}{}%
  % Marquer le début du contenu pour titletoc
  \startcontents[chapters]%
  % Page de table des matières sans en-tête ni pied de page
  \newgeometry{
    top=2cm,
    bottom=2cm,
    left=2cm,
    right=2cm
  }
  \thispagestyle{empty}%
  \vfill
  \begin{center}
    {\LARGE\bfseries Chapitre {#1} : #2\par}
    \vspace{0.3cm}
    {\large\bfseries Table des matières\par}
    \vspace{0.5cm}
    \begin{minipage}{0.95\textwidth}
      % Affiche uniquement sections (niveau 1) et subsections (niveau 2)
      \printcontents[chapters]{}{1}{\setcounter{tocdepth}{2}}
    \end{minipage}
  \end{center}
  \vfill
  \restaurergeometrie % Restaure la géométrie "Cours" pour le contenu
  \clearpage
  % Ajouter une entrée dans la table des matières globale
  \addcontentsline{toc}{chapitre}{\protect\numberline{Chapitre #1}#2}%
  % Appliquer le style d'en-tête spécial pour la première page
  \thispagestyle{premierepageschapitre}%
  
}

\endinput