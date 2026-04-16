# ⚡ ÉnergiePro — Analyse Technico-Économique des Énergies Renouvelables

> Application professionnelle Streamlit · Interface française · Résultats en USD

---

## 🚀 Démarrage rapide

```bash
# 1. Cloner / dézipper le projet
cd energie_app

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'application
streamlit run app.py
```

Ouvrez votre navigateur à l'adresse : **http://localhost:8501**

---

## 📐 Architecture de l'application

```
energie_app/
├── app.py            ← Application Streamlit principale (~750 lignes)
├── requirements.txt  ← Dépendances Python
└── README.md         ← Ce fichier
```

---

## 🖥️ Pages disponibles

| Page | Description |
|------|-------------|
| 🏠 Accueil | Hero, fonctionnalités, formules, approche économique |
| ☀️ Photovoltaïque | Paramètres · Calculs · 3 graphiques · Tableau annuel |
| 🌬️ Éolien | Paramètres · Calculs physiques · 3 graphiques · Tableau |
| ⚖️ Comparaison | Graphe barres · Tableau vert/rouge · Radar normalisé |
| 📊 Résultats | Synthèse · Tableau CSV · Export PDF |

---

## ☀️ Module Photovoltaïque

### Entrées
| Paramètre | Valeur par défaut | Unité |
|-----------|:-----------------:|-------|
| Puissance installée | 100 | kWc |
| Irradiation solaire | 1 800 | kWh/m²/an |
| Performance Ratio | 80 | % |
| Coût d'investissement | 150 000 | $ USD |
| Coût maintenance annuel | 2 250 | $ USD/an |
| Durée de vie | 25 | ans |
| Taux d'actualisation | 7 | % |
| LCOE de référence réseau | 0.12 | $/kWh |

### Formule de production
```
E (kWh/an) = P_kWc × Irradiation × PR
```

---

## 🌬️ Module Éolien

### Entrées
| Paramètre | Valeur par défaut | Unité |
|-----------|:-----------------:|-------|
| Puissance nominale | 500 | kW |
| Vitesse vent moyenne | 7.5 | m/s |
| Densité de l'air | 1.225 | kg/m³ |
| Coefficient Cp | 0.40 | — |
| Facteur de charge | 30 | % |
| Coût d'investissement | 1 500 000 | $ USD |
| Coût maintenance annuel | 37 500 | $ USD/an |
| Durée de vie | 20 | ans |
| Taux d'actualisation | 8 | % |

### Formules physiques
```
P (W)       = 0.5 × ρ × A × V³ × Cp
E (kWh/an)  = P_kW × 8 760 × Facteur_de_charge
```

---

## 💰 Indicateurs économiques

### Approche sans prix de vente
L'analyse est **exclusivement basée sur les coûts et la production**.  
La valeur économique de l'énergie = LCOE de référence réseau × production annuelle.

| Indicateur | Formule | Unité |
|-----------|---------|-------|
| **LCOE** | ΣCoûts_actualisés / ΣÉnergie_actualisée | $/kWh |
| **VAN** | Σ Ft/(1+r)^t − I₀ | $ USD |
| **IRR** | VAN(IRR) = 0 [Newton-Raphson] | % |
| **Temps de retour** | I₀ / Flux_net_annuel | années |

---

## 📊 Graphiques Plotly interactifs

1. **📈 Cash-Flow** — Flux annuels (barres) + CF cumulé + CF actualisé cumulé
2. **⚡ Production mensuelle** — Profil sinusoïdal sur 12 mois (MWh)
3. **🧾 Répartition des coûts** — Camembert : investissement vs O&M
4. **⚖️ Comparaison** — Barres groupées (production, LCOE, VAN, IRR)
5. **🕸️ Radar normalisé** — Profil de performance multi-critères

---

## 📄 Rapport PDF

Le rapport généré contient :
- Page de garde avec date
- Tableau des paramètres d'entrée
- Liste des équipements
- Tableau des résultats économiques complets
- Tableau comparatif PV vs Éolien (si les deux analyses ont été réalisées)
- Pied de page avec mention de la source

Format : **A4 · Français · Montants en USD**

---

## 🛠️ Stack technique

| Outil | Usage |
|-------|-------|
| **Python 3.8+** | Langage principal |
| **Streamlit** | Interface web interactive |
| **NumPy** | Calculs vectorisés |
| **Pandas** | Tableaux de données |
| **Plotly** | Graphiques interactifs |
| **ReportLab** | Génération PDF |

---

## 🎨 Design

- Thème sombre sophistiqué (fond ardoise `#0B1120`)
- Accents teal/cyan `#14B8A6` et ambre `#F59E0B`
- Police **Sora** (titres) + **JetBrains Mono** (valeurs)
- Cards KPI avec dégradés et effets hover
- Tableau comparatif avec couleurs win/lose

---

*Développé à des fins pédagogiques — Étudiants en Génie Électrique & Énergies Renouvelables*
