# SYSTÈME APEX-30 - GUIDE D'UTILISATION

## 📖 Description

APEX-30 est un système professionnel de pronostic sportif basé sur 30 ans d'expérience. Il analyse les matchs selon 8 modules principaux avec pondération scientifique.

## 🎯 Philosophie

**"La discipline vaut mieux que 100 analyses moyennes"**

- Sélectivité extrême (10-15% des matchs)
- Gestion rigoureuse de bankroll
- Traçabilité complète
- Approche scientifique, pas émotionnelle

## 📦 Fichiers du Système

```
apex30_pronostic.py     → Script principal avec toute la logique
charger_json.py         → Utilitaire pour charger depuis JSON
config_exemple.json     → Template de configuration
README.md               → Ce guide
```

## 🚀 Installation

### Prérequis
- Python 3.7+
- Aucune dépendance externe (100% Python natif)

### Installation
```bash
# Télécharger les fichiers
# Aucune installation requise, tout fonctionne en natif!
```

## 📊 Utilisation

### Méthode 1: Depuis Python (Code Direct)

```python
from apex30_pronostic import (
    APEX30Analyzer, EquipeData, MatchData, 
    HistoriqueH2H, CotesMarche, JoueurAbsent, MatchAVenir
)

# 1. Créer les données des équipes
matchs_equipe_a = [
    MatchData(
        date="2025-01-20",
        domicile=True,
        resultat="V",  # V=Victoire, N=Nul, D=Défaite
        buts_pour=3,
        buts_contre=1,
        adversaire_classement=8,
        competition="Championnat",
        xg_pour=2.8,
        xg_contre=0.9,
        possession=62,
        tirs_cadres=8,
        corners_obtenus=6,
        corners_concedes=3
    ),
    # ... ajouter 9 autres matchs pour un total de 10
]

equipe_a = EquipeData(
    nom="Paris SG",
    matchs_historique=matchs_equipe_a,
    classement_actuel=1,
    points_domicile_saison=2.5,
    points_exterieur_saison=1.9,
    est_domicile=True,
    situation="Titre",
    joueurs_absents=[
        JoueurAbsent("Mbappé", "Attaquant", 9, 5)
    ]
)

# 2. Créer l'historique H2H
h2h = HistoriqueH2H(
    victoires_equipe_a=3,
    nuls=1,
    victoires_equipe_b=1,
    matchs_serres=3,
    derniers_gagnants=['A', 'N', 'A', 'B', 'A']
)

# 3. Ajouter les cotes (optionnel)
cotes = CotesMarche(
    victoire_equipe_a=1.65,
    nul=3.80,
    victoire_equipe_b=5.50
)

# 4. Lancer l'analyse
analyzer = APEX30Analyzer()
resultat = analyzer.analyser_match(equipe_a, equipe_b, h2h, cotes)

# 5. Accéder aux résultats
print(f"Score Équipe A: {resultat['equipe_a']['score_total']}")
print(f"Pronostic: {resultat['decision']['pronostic']}")
print(f"Mise recommandée: {resultat['decision']['mise_recommandee']}")
```

### Méthode 2: Depuis JSON (Recommandé)

**Étape 1:** Créer votre fichier de configuration JSON

```json
{
  "equipe_a": {
    "nom": "Manchester City",
    "classement_actuel": 2,
    "points_domicile_saison": 2.6,
    "points_exterieur_saison": 2.1,
    "est_domicile": true,
    "situation": "Titre",
    "matchs_historique": [
      {
        "date": "2025-01-20",
        "domicile": true,
        "resultat": "V",
        "buts_pour": 3,
        "buts_contre": 0,
        "adversaire_classement": 6,
        "competition": "Championnat",
        "xg_pour": 3.2,
        "xg_contre": 0.6
      }
      // ... 9 autres matchs
    ],
    "joueurs_absents": []
  },
  "equipe_b": { /* ... */ },
  "historique_h2h": { /* ... */ },
  "cotes": { /* ... */ }
}
```

**Étape 2:** Lancer l'analyse

```bash
python charger_json.py mon_match.json
```

**Étape 3:** Consulter les résultats

Le système génère automatiquement:
- `mon_match_rapport.txt` - Rapport détaillé complet
- `mon_match_resultat.json` - Résultat structuré JSON

## 🔍 Modules d'Analyse

### Module 1: IFP (Indice de Forme Pondéré)
- Analyse des 10 derniers matchs
- Pondération par qualité adversaire, localisation, récence
- Échelle: 0 (Critique) à 3+ (Excellente)

### Module 2: Force Offensive & Défensive
- Combine buts, xG, tirs cadrés
- Ajusté selon la force des adversaires
- Échelle: 0-10 pour chaque

### Module 3: Facteur Domicile/Extérieur
- Personnalisé par équipe (ratio domicile/extérieur)
- Évite les coefficients fixes arbitraires
- Impact: -0.3 à +0.8

### Module 4: Fatigue
- Analyse calendrier 15 jours avant/après
- Poids selon type de compétition
- Impact: 0 à -0.8

### Module 5: Motivation
- Situation au classement
- Contexte émotionnel (derby, etc.)
- Situation entraîneur
- Score: -2 à +3

### Module 6: Absences
- Évaluation personnalisée par joueur (0-10)
- Impact cumulatif
- Bonus pour blessures de longue date

### Module 7: Historique H2H
- Tendance sur 5 derniers matchs
- Détection domination psychologique
- Impact: 0 à +1.0

### Module 8: Analyse du Marché
- Détection value bets
- Analyse mouvements de cotes
- Comparaison avec nos probabilités

## 📈 Interprétation des Résultats

### Niveaux de Confiance

| Écart de Score | Confiance | Mise Recommandée | Action |
|----------------|-----------|------------------|--------|
| < 0.5 | Incertitude | 0% | ❌ NE PAS PARIER |
| 0.5 - 1.5 | Match serré | 1% | ⚠️ Prudence |
| 1.5 - 2.5 | Confiance modérée | 2-3% | ✅ Pari acceptable |
| > 2.5 | Forte confiance | 3-5% | ✅ Excellent pari |

### Exemple de Rapport

```
================================================================================
🎯 DÉCISION FINALE
================================================================================
Niveau de confiance: Forte confiance
Pronostic: Victoire Paris SG
Mise recommandée: 3-5% de la bankroll

💎 Value Bet identifiée: Équipe A (+12.3%)

✅ EXCELLENT PARI - Forte confiance
================================================================================
```

## 🎲 Règles d'Or (OBLIGATOIRES)

### 1. Sélectivité Extrême
- Ne pariez QUE si écart > 1.5 ET value bet détectée
- Maximum 15% des matchs analysés
- Confiance minimum 70%

### 2. Gestion de Bankroll

```
Bankroll = 100 unités

Forte confiance (>2.5): 3-5 unités
Confiance modérée (1.5-2.5): 2-3 unités
Faible confiance: 1 unité

JAMAIS > 5% sur un seul pari
JAMAIS > 15% engagés simultanément
```

### 3. Traçabilité

Tenez un journal Excel/Google Sheets:
```
Date | Match | Pronostic | Cote | Mise | Résultat | ROI
```

Analysez mensuellement:
- Quels modules sont les plus prédictifs?
- Quels types de matchs maîtrisez-vous?
- Où perdez-vous de l'argent?

### 4. Spécialisation

Après 6 mois, concentrez-vous sur:
- 2-3 championnats maximum
- Types de matchs où vous excellez
- Marchés spécifiques (1X2, Buts, etc.)

## ⚠️ Signaux d'Alerte - NE PAS PARIER

- ❌ > 3 joueurs clés incertains
- ❌ Cotes aberrantes (possible match truqué)
- ❌ Météo extrême non prise en compte
- ❌ Vous pariez par "ennui"
- ❌ Intuition sans données

## 🔧 Personnalisation

### Ajuster les Poids

Dans `apex30_pronostic.py`, modifiez les poids (total doit = 1.0):

```python
POIDS = {
    'ifp': 0.25,              # Forme
    'force_offensive': 0.15,   # Attaque
    'solidite_defensive': 0.15, # Défense
    'facteur_domicile': 0.10,  # Domicile/Extérieur
    'fatigue': 0.05,           # Calendrier
    'motivation': 0.15,        # Enjeu
    'absences': 0.10,          # Blessures
    'h2h': 0.05               # Historique
}
```

### Ajouter des Modules

Vous pouvez créer vos propres modules:

```python
def _calculer_mon_module(self, equipe: EquipeData) -> float:
    """Votre logique personnalisée"""
    score = 0
    # ... votre calcul
    return score
```

## 📚 Données Requises

### Données Minimales (pour fonctionner)
- 10 derniers matchs de chaque équipe
- Résultats (V/N/D), buts pour/contre
- Classement actuel
- Domicile/Extérieur pour le match

### Données Recommandées (pour précision)
- Expected Goals (xG)
- Possession, tirs cadrés, corners
- Calendrier (matchs avant/après)
- Joueurs absents
- Historique H2H
- Cotes du marché

### Où Trouver les Données?

**Gratuites:**
- FBref.com (statistiques avancées)
- Transfermarkt (effectifs, absences)
- FlashScore (résultats, calendrier)
- Sofascore (statistiques de match)

**Payantes (professionnelles):**
- Opta Sports
- StatsBomb
- Wyscout
- InStat

## 🎓 Conseils de Pro

### Pour Débuter
1. Commencez avec 1 championnat que vous connaissez
2. Analysez 50 matchs SANS parier (back-testing)
3. Notez TOUTES vos analyses
4. Identifiez vos forces/faiblesses

### Pour Progresser
1. Spécialisez-vous (ex: Ligue 1, matchs du milieu de tableau)
2. Comparez vos prédictions vs résultats réels
3. Ajustez les poids selon vos résultats
4. Développez votre propre "edge"

### Pour Exceller
1. Automatisez la collecte de données
2. Créez votre base de données historique
3. Testez différentes stratégies de mise
4. Restez DISCIPLINÉ (le plus important!)

## ❓ FAQ

**Q: Quel taux de réussite puis-je espérer?**
R: Avec discipline et spécialisation: 60-70% sur vos paris sélectionnés (pas tous les matchs!)

**Q: Combien de temps pour une analyse?**
R: 15-20 minutes pour collecter les données, 2 secondes pour l'analyse!

**Q: Puis-je utiliser ce système pour des paris en live?**
R: Non, conçu pour l'analyse pré-match. Le live nécessite d'autres outils.

**Q: Ça marche pour d'autres sports?**
R: La logique est transposable mais les poids et modules doivent être adaptés.

**Q: C'est légal?**
R: Oui, c'est un outil d'analyse. Vérifiez les lois sur les paris dans votre pays.

## 📞 Support

Pour toute question ou amélioration:
1. Consultez d'abord ce README
2. Examinez le code source (très commenté)
3. Testez avec l'exemple fourni

## 📄 Licence

Usage personnel et éducatif uniquement.
Pariez de manière responsable.

---

**Rappel:** Le gambling peut créer une dépendance. Ne pariez jamais plus que ce que vous pouvez vous permettre de perdre. Cet outil est une aide à la décision, pas une garantie de gains.

---

*Système APEX-30 - 30 ans d'expérience condensés en code*
*Version 1.0 - Janvier 2025*
