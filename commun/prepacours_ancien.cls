\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{../commun/prepacours}[2025/06/15 Classe LaTeX pour cours de prépa]

\LoadClass[a4paper,11pt]{article}

% Packages essentiels
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[french]{babel}
\RequirePackage{amsmath,amsthm,amssymb}
\RequirePackage{xcolor}
\RequirePackage[most]{tcolorbox} % CHANGÉ : ajouter "most"
\RequirePackage{geometry}
\RequirePackage{fancyhdr}
\RequirePackage{titlesec}
\RequirePackage{lipsum}
\RequirePackage{mathpazo}
\RequirePackage{hyperref}
\RequirePackage{tikz}
\RequirePackage{fontawesome5}
\RequirePackage{graphicx}
\RequirePackage{marginnote}
\RequirePackage{afterpage}
\RequirePackage{atbegshi}
\RequirePackage[normalem]{ulem}
\RequirePackage{needspace}
\RequirePackage{mathrsfs}





\setcounter{tocdepth}{2} % Profondeur de la table des matières

% Marges - plus d'espace à droite pour les notes marginales
\geometry{
  top=2.5cm,
  bottom=2.5cm,
  left=2cm,
  right=5cm,
  marginparwidth=3.5cm,
  marginparsep=0.5cm,
  headheight=30pt % Hauteur d'en-tête normale pour les pages standard
}

% Pas d'indentation des paragraphes
\setlength{\parindent}{0pt}

% Début des commandes contenant des @
\makeatletter

% Couleurs personnalisées
\definecolor{bluebox}{RGB}{36,113,200}
\definecolor{redbox}{RGB}{231,35,35}
\definecolor{greenbox}{RGB}{60,150,200} %
\definecolor{examplebar}{RGB}{0,0,0}
\definecolor{ideabar}{RGB}{255,165,0} % Couleur orange pour l'idée

% Styles pour les boîtes
\tcbset{
  propstyle/.style={
    enhanced,
    colback=bluebox!5,
    colframe=bluebox,
    boxrule=0.8pt,
    arc=2pt,
    left=6pt,
    right=6pt,
    top=6pt,
    bottom=6pt,
    % drop shadow % Ajout d'une ombre portée
  },
  theoremstyle/.style={
    enhanced,
    colback=greenbox!5,
    colframe=greenbox,
    boxrule=0.8pt,
    arc=2pt,
    left=6pt,
    right=6pt,
    top=6pt,
    bottom=6pt,
    % drop shadow % Ajout d'une ombre portée
  },
  defstyle/.style={
    enhanced,
    colback=redbox!5,
    colframe=redbox,
    boxrule=0.8pt,
    arc=2pt,
    left=6pt,
    right=6pt,
    top=6pt,
    bottom=6pt,
    % drop shadow % Ajout d'une ombre portée
  },
  examplestyle/.style={
    enhanced,
    colback=gray!5,
    colframe=examplebar,
    boxrule=0.5pt,
    borderline west={2pt}{0pt}{examplebar},
    arc=1pt,
    left=6pt,
    right=6pt,
    top=6pt,
    bottom=6pt
  },
  ideastyle/.style={
    enhanced,
    colback=yellow!10,
    colframe=ideabar,
    boxrule=0.5pt,
    borderline west={3pt}{0pt}{ideabar},
    arc=1pt,
    left=6pt,
    right=6pt,
    top=6pt,
    bottom=6pt,
    breakable
  }
}

% Supprime le numéro ET les parenthèses des équations
\renewcommand{\tagform@}[1]{#1}
\renewcommand{\theequation}{}

% --- Compteur de chapitre manuel ---
\newcounter{chapitre}
\renewcommand{\thechapitre}{\arabic{chapitre}}

\newcommand{\setchapitre}[1]{%
  \setcounter{chapitre}{#1}%
  \addtocounter{chapitre}{-1}%
  \refstepcounter{chapitre}%
  \setcounter{coursenv}{0}%
}

% --- Compteur global pour tous les environnements ---
\newcounter{coursenv}[chapitre]
\renewcommand{\thecoursenv}{\thechapitre.\arabic{coursenv}}

% --- Contrôle d'affichage des titres ---
\newif\ifaffichertitres
\affichertitrestrue % Par défaut, les titres sont affichés

\newcommand{\affichertitres}{\affichertitrestrue}
\newcommand{\masquertitres}{\affichertitresfalse}

% --- Environnements mathématiques avec compteur global ---
\newtcbtheorem[use counter=coursenv, number within=chapitre]{theoreme}{Théorème}%
{theoremstyle, fonttitle=\bfseries, title={~: #2}}{thm}

\newtcbtheorem[use counter=coursenv, number within=chapitre]{proposition}{Proposition}%
{propstyle, fonttitle=\bfseries, title={~: #2}}{prop}

\newtcbtheorem[use counter=coursenv, number within=chapitre]{corollaire}{Corollaire}%
{propstyle, fonttitle=\bfseries, title={~: #2}}{cor}

\newtcbtheorem[use counter=coursenv, number within=chapitre]{definition}{Définition}%
{defstyle, fonttitle=\bfseries, title={~: #2}}{def}

\newtcbtheorem[use counter=coursenv, number within=chapitre]{propriete}{Propriété}%
{propstyle, fonttitle=\bfseries, title={~: #2}}{propiete}

% Environnements sans titre (versions "nt" = no title)
% Ces environnements n'affichent que le nom de l'environnement et le numéro, sans titre personnalisé
% Utilisation de newtcolorbox pour un contrôle total

\newtcolorbox{theorement}[2][]{
  theoremstyle,
  fonttitle=\bfseries,
  title={Théorème~\refstepcounter{coursenv}\thecoursenv},
  #1
}

\newtcolorbox{propositionnt}[2][]{
  propstyle,
  fonttitle=\bfseries,
  title={Proposition~\refstepcounter{coursenv}\thecoursenv},
  #1
}

\newtcolorbox{corollairent}[2][]{
  propstyle,
  fonttitle=\bfseries,
  title={Corollaire~\refstepcounter{coursenv}\thecoursenv},
  #1
}

\newtcolorbox{definitionnt}[2][]{
  defstyle,
  fonttitle=\bfseries,
  title={Définition~\refstepcounter{coursenv}\thecoursenv},
  #1
}

\newtcolorbox{proprietent}[2][]{
  propstyle,
  fonttitle=\bfseries,
  title={Propriété~\refstepcounter{coursenv}\thecoursenv},
  #1
}

% Environnement remarque dans le style amsthm (comme proof)
\newtheoremstyle{remarque}% nom du style
  {3pt}% espace avant
  {3pt}% espace après
  {\normalfont}% police du corps
  {}% indentation
  {\itshape}% police du titre
  {.}% ponctuation après le titre
  { }% espace après le titre
  {}% spécification du titre

\theoremstyle{remarque}
\newtheorem*{remarque}{Remarque}



% Environnement exemple avec sidebar (barre latérale)
\newtcolorbox{exemple}[1][]{
  enhanced,
  breakable,
  enhanced jigsaw,
  pad at break=2mm,
  colback=white,
  colframe=white,
  boxrule=0pt,
  left=8pt,
  right=0pt,
  top=6pt,
  bottom=6pt,
  borderline west={2pt}{0pt}{examplebar},
  title={},
  before upper={\textbf{\color{examplebar}Exemple} \par\vspace{0.2em}},
  #1
}

% Commande pour l'ampoule avec FontAwesome
% \newcommand{\ampoule}{\faLightbulb[regular]}
\newcommand{\ampoule}{\includegraphics[height=1.2em]{../commun/images/ampoule.png}}

% Environnement pour l'idée de la preuve dans la marge droite
\newcommand{\idee}[1]{%
  % Vérifier l'espace disponible et éviter les coupures
  \needspace{4\baselineskip}%
  \vspace{-1.6em}%
  \marginnote{%
    \begin{tcolorbox}[
      enhanced,
      colback=yellow!5,
      colframe=ideabar,
      boxrule=0.8pt,
      arc=2pt,
      left=4pt,
      right=4pt,
      top=4pt,
      bottom=4pt,
      width=\marginparwidth,
      fonttitle=\scriptsize\bfseries,
      title={\ampoule~Idée de la preuve},
      coltitle=white,
      colbacktitle=ideabar,
      breakable=false,
      % drop shadow % Ajout d'une ombre portée
    ]
    \scriptsize\raggedright
    #1
    \end{tcolorbox}%
  }%
}



% Entêtes de page standard
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\thepage}
\fancyhead[R]{Chapitre~\@numchapitre{} -- \@titrechapitre}
% Étendre l'en-tête sur toute la largeur (y compris la marge droite)
\fancyhfoffset[R]{3cm}


\newcommand{\annee}[1]{\gdef\@annee{#1}}
\newcommand{\chapitre}[2]{%
  \setchapitre{#1}%
  \gdef\@numchapitre{#1}%
  \gdef\@titrechapitre{#2}%
  \markboth{Chapitre #1 -- #2}{}%
}

\newcommand{\@numchapitre}{}


% pied de page 
\newcommand{\filiere}[1]{\gdef\@filiere{#1}}
\newcommand{\etablissement}[1]{\gdef\@etablissement{#1}}
\newcommand{\auteur}[1]{\gdef\@auteur{#1}}

\newcommand{\@filiere}{}
\newcommand{\@etablissement}{}
\newcommand{\@auteur}{}


\fancyfoot[L]{\@filiere}
\fancyfoot[C]{\@etablissement}
\fancyfoot[R]{\@auteur}



% Définir un style d'en-tête spécial pour la première page de chapitre (deuxième page du document)
\fancypagestyle{premierepageschapitre}{%
  \fancyhf{} % Effacer tous les en-têtes et pieds de page
  % Augmenter temporairement la hauteur de l'en-tête pour cette page
  \setlength{\headheight}{70pt}
  % gère le titre du chapitre à gauche (AGRANDI)
  \fancyhead[L]{%
    \parbox[c][70pt][c]{12cm}{%
      \fontsize{24}{28}\selectfont\bfseries\raggedright%
      \@titrechapitre%
    }%
  }
  % gère le numéro de chapitre à droite (AGRANDI)
  \fancyhead[R]{%
    \parbox[c][70pt][c]{3cm}{%
      \raggedleft\fontsize{50}{40}\selectfont\bfseries\color{sectionblue}%
      \@numchapitre%
    }%
  }
  \fancyfoot[L]{\@filiere}
  \fancyfoot[C]{\@etablissement}
  \fancyfoot[R]{\@auteur}
  \renewcommand{\headrulewidth}{0.8pt}
  \fancyhfoffset[R]{3cm}
}

% Commande pour passer au style d'en-tête normal après la première page de contenu
\newcommand{\passerenstylestandard}{%
  \clearpage%
  \pagestyle{fancy}%
  \setlength{\headheight}{30pt}% Remettre la hauteur normale
}



% Page de garde
\newcommand{\pagedegarde}{
  % Géométrie spéciale pour la page de garde (marges symétriques)
  \newgeometry{
    top=3cm,
    bottom=3cm,
    left=3cm,
    right=3cm
  }
  \thispagestyle{empty}
  %\vspace*{1cm}
  \begin{center}
    {\Huge \bfseries Chapitre~\@numchapitre{} -- \@titrechapitre \par}
    %\vspace{2cm}
    %{\large \today \par}
    \vspace{1cm}
    \tableofcontents
    \vfill
    {\Large Année \@annee \par}
    \vspace{0.5cm}
    {\normalsize Version du \today \par}
  \end{center}
  \newpage
  % Restauration de la géométrie normale avec en-tête agrandi pour la première page de contenu
  \newgeometry{
    top=3.5cm, % Plus d'espace en haut pour l'en-tête agrandi
    bottom=2.5cm,
    left=2cm,
    right=5cm,
    marginparwidth=3.5cm,
    marginparsep=0.5cm,
    headheight=70pt % Hauteur agrandie pour la première page de contenu
  }
  % Appliquer le style spécial à la première page de contenu
  \thispagestyle{premierepageschapitre}
}

% Commande pour revenir au style de page normal après la première page de contenu
% À utiliser quand vous voulez passer de l'en-tête agrandi aux en-têtes standards
\newcommand{\restaurergeometrie}{%
  \clearpage
  % Restaurer la géométrie normale
  \newgeometry{
    top=2.5cm,
    bottom=2.5cm,
    left=2cm,
    right=5cm,
    marginparwidth=3.5cm,
    marginparsep=0.5cm,
    headheight=30pt % Hauteur normale
  }
  \pagestyle{fancy}
}

% Commande pour démarrer un chapitre dans le document intégral
% (sans page de garde ni table des matières propre au chapitre)
\newcommand{\chapitreintegral}[2]{%
  \clearpage
  % Restauration de la géométrie normale avec en-tête agrandi pour la première page de contenu
  \newgeometry{
    top=3.5cm, % Plus d'espace en haut pour l'en-tête agrandi
    bottom=2.5cm,
    left=2cm,
    right=5cm,
    marginparwidth=3.5cm,
    marginparsep=0.5cm,
    headheight=70pt % Hauteur agrandie pour la première page de contenu
  }
  % Définir le chapitre courant
  \setchapitre{#1}%
  \gdef\@numchapitre{#1}%
  \gdef\@titrechapitre{#2}%
  \markboth{Chapitre #1 -- #2}{}%
  % Ajouter une entrée de chapitre dans la table des matières
  \addcontentsline{toc}{chapitre}{\protect\numberline{Chapitre #1}#2}%
  % Appliquer le style spécial à la première page de contenu
  \thispagestyle{premierepageschapitre}
}



\definecolor{sectionblue}{RGB}{13, 114, 202}

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

% Redéfinition de \l@section pour augmenter la largeur du numéro
\renewcommand*\l@section{\@dottedtocline{1}{1.5em}{2.5em}}
\renewcommand*\l@subsection{\@dottedtocline{2}{4.5em}{3em}}

% Configuration hyperref pour le niveau chapitre
\providecommand{\toclevel@chapitre}{0}
\providecommand{\toclevel@section}{1}
\providecommand{\toclevel@subsection}{2}

% Décalage des titres de section et sous-section
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

\renewcommand{\thesection}{\thechapitre.\arabic{section}}
\renewcommand{\thesubsection}{\thesection.\arabic{subsection}}

% Réinitialisation des compteurs
\@addtoreset{section}{chapitre}
\@addtoreset{subsection}{section}

% symbole attention
\newcommand{\attention}{\tikz[scale=0.2,baseline=-0.6ex]{
  \draw[fill=yellow,draw=black] (0,0) -- (1,2) -- (2,0) -- cycle;
  \node at (1,0.7) {\textbf{!}};
}}

\makeatother
