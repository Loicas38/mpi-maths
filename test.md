# Équations Différentielles (MPI*)

## 1. Ordre 1 & Raccords
- **Méthode expresse**
  - Multiplier par 
$$e^{A(t)}$$
  - Reconnaître $(y e^A)'$
- **Valeurs absolues**
  - Sur un intervalle continu, $\lambda e^{-\ln|u|} \to \frac{\lambda}{\pm u}$
  - Le signe est absorbé par la constante $\lambda$
- **Raccords en $t_0$**
  - Faire un **DL à l'ordre 1** (prouve la dérivabilité)
  - Montrer que la solution est **DSE** (donne la classe $\mathcal{C}^\infty$)

## 2. Systèmes Diff. ($Y' = AY + B$)
- **$A$ Trigonalisable ($A=PTP^{-1}$)**
  - Poser $Z = P^{-1}Y$ $\Rightarrow$ $Z' = TZ + P^{-1}B$
  - Résoudre en remontant (de $z_n$ à $z_1$)
- **$A(t)$ non constante**
  - Exponentielle matricielle souvent FAUSSE !
  - Trouver une base de Vecteurs Propres **indépendante de $t$**
- **Récupérer solutions réelles**
  - Si $(Z, \bar{Z})$ base complexe $\to$ prendre $(Re(Z), Im(Z))$

## 3. Ordre 2 non constant ($y''+ay'+by=d$)
- **Objectif :** Trouver $g$ connaissant $f$
- **Abaissement de l'ordre (Lagrange)**
  - Poser $g = fz$
  - Injecter pour avoir une E.D. d'ordre 1 en $z'$
  - *Avantage :* Gère les seconds membres
- **Wronskien**
  - Formule : $(\frac{g}{f})' = \frac{e^{-A}}{f^2}$
  - *Avantage :* Immédiat par intégration
  - *Inconvénient :* Sans second membre

## 4. Équations Fonctionnelles
- **Équations Intégrales**
  - Dériver via le Théorème Fondamental de l'Analyse
  - **Obligatoire :** Vérifier la réciproque !
- **Involutions $f(-x)$**
  - **Méthode de la parité :** $f = g + h$ (paire + impaire)
  - Identifier pour obtenir 2 équations (ou 1 système découplé $z = g+ih$)
  - Réciproque inutile (équivalence de la décomposition)
- **Autres Involutions $\tau(x)$**
  - Substituer $x$ par $\tau(x)$, dériver, combiner les lignes
  - Réciproque obligatoire !

## 5. Théorie (Cauchy & Isomorphismes)
- **Théorème de Cauchy**
  - Utile pour prouver l'unicité ou la nullité
  - Évaluation de $y, y'$ en **un seul point $t_0$**
- **Isomorphisme $y \mapsto (y(t_0), y'(t_0))$**
  - Transfert d'un espace fonctionnel (dur) vers $\mathbb{R}^2$ (facile)
  - Conserve les bases et l'indépendance linéaire
- **Wronskien "théorique"**
  - Étude du signe de $W'$ pour l'entrelacement des zéros
  - Trouver un équivalent d'une solution non explicite