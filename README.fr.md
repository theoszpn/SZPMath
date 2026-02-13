# SZPMath (Alpha v1.0)
[English Version](./README.md) | **Version Française**\
SZPMath est un outil pédagogique dédié au calcul mathématique avancé, conçu pour offrir une interface fluide, dynamique et interractive. Développé en Python 3.13, il combine la puissance de calcul de NumPy et Matplotlib avec une interface utilisateur moderne sous PySide6.\
Disponible sur Windows, MacOS et Linux.

## Fonctionnalités
**Algèbre Linéaire** : Calcul matriciel, Résolution de systèmes avec Gauss/Cramer, étude d'espaces et sous espaces vectoriels, diagonalisation, rendu en 2D et 3D de transformations et combinaisons linéaires.

**Calculus** : Visualisation interactive et dynamique de fonctions, étude de limites/continuité, calcul dérivé et intégral.

**Statistiques** : Analyse de séries discrètes et continues : paramètres de tendance centrale/dispertion/forme, visualisation avec des graphs et boxplots.

**Probabilités** : Arrangements, Analyse interractive de lois discrètes (Binomiale, Poisson, Géometrique) et continues (Normale, Exponentielle).

## Stack Technique (Édition 2026)
Le projet utilise les dernières versions stables pour garantir performance et compatibilité :

**Interface Graphique** : PySide6 (v6.8.2) pour un rendu natif et une gestion optimisée du High DPI.

**Moteur de Calcul** : NumPy (v2.2.0+) pour les calculs numériques intensifs et SymPy pour le calcul symbolique.

**Visualisation** : 

OpenGL (v3.1.10) pour le rendu 3D.

PyQtGraph (v0.13.3) pour les graphiques interactifs temps réel.

Matplotlib (v3.10.x) pour les rendus statistiques de haute qualité.

**Packaging** : PyInstaller pour la distribution d'exécutables autonomes sous Windows.

## Installation (Utilisateur)
Pour installer le logiciel (en .exe), suivre le guide utilisateur de la dernière release.

## Installation (Développement)
Pour cloner le projet et l'exécuter localement :

**Pour cloner :**

**Bash**\
git clone https://github.com/theoszpn/SZPMath.git
cd SZPMath

**Pour créer un environnement virtuel (Recommandé) :**

**Bash**\
python -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate

**Pour installer les dépendances :**

**Bash**\
pip install -r requirements.txt

**Pour Lancer l'application :**

**Bash**\
python main.py

## Structure du Projet

SZPMath_aplha/\
├── assets/\
├── modules/\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── algebra/\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── calculus/\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── probas/\
│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── statistics/\
├── main.py\
├── .gitignore\
├── README.md\
├── requirements.txt\
└── screenshots/


## Roadmap & Évolutions

[ ] Implémentation d'un système d'authentification utilisateur.

[ ] Sauvegarde des calculs en base de données SQLite locale.

[ ] Version Premium avec support du calcul tensoriel.

[ ] Export des graphiques en PDF/LaTeX.

## Développé par **Théo SZAPPANYOS**, Projet réalisé dans le cadre d'un portfolio technique (Février 2026).

## Annexes :

**Captures d'écran | Algèbre Linéaire**
![Aperçu résolution système Cramer](screenshots/SZPMath_Cramer_Solver.png)
![Aperçu analyse sous-espaces vectoriels](screenshots/SZPMath_Vector_Spaces.png)
![Aperçu visualisation 3D](screenshots/SZPMath_3D_Visualization.png)

**Captures d'écran | Statistiques**
![Aperçu analyse formes](screenshots/SZPMath_Stats_Shape.png)
![Aperçu graphiques d'analyse](screenshots/SZPMath_Stats_Graphs.png)

**Captures d'écran | Probabilités**
![Aperçu interface loi binomiale](screenshots/SZPMath_Probas_Binom.png)
![Aperçu interface loi normale](screenshots/SZPMath_Probas_Normale.png)

**Captures d'écran | Calculus**
![Aperçu interface dérivées](screenshots/SZPMath_Calculus_Derivatives.png)
![Aperçu interface intégrales](screenshots/SZPMath_Probas_Normale.png)