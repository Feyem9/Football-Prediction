# 🎰 Guide des Cotes de Paris - Pronoscore

## Vue d'ensemble

L'intégration **The Odds API** permet de récupérer les cotes de paris en temps réel et de calculer si un pari a de la **valeur** (Value Bet).

---

## 📊 Qu'est-ce qu'une Cote ?

Une **cote** représente le gain potentiel pour chaque euro misé.

### Exemple :

| Cote | Signification | Mise 10€ → Gain  |
| ---- | ------------- | ---------------- |
| 1.50 | Favori        | 15€ (profit 5€)  |
| 2.00 | 50/50         | 20€ (profit 10€) |
| 3.00 | Outsider      | 30€ (profit 20€) |

### Formule de gain :

```
Gain = Mise × Cote
Profit = Gain - Mise = Mise × (Cote - 1)
```

---

## 🧮 Probabilité Implicite

Chaque cote cache une **probabilité implicite** que le bookmaker estime.

### Formule :

```
Probabilité Implicite = 1 / Cote × 100
```

### Exemples :

| Cote | Probabilité Implicite |
| ---- | --------------------- |
| 1.50 | 66.7%                 |
| 2.00 | 50.0%                 |
| 2.50 | 40.0%                 |
| 3.00 | 33.3%                 |
| 4.00 | 25.0%                 |

---

## 🔥 Qu'est-ce qu'un Value Bet ?

Un **Value Bet** existe quand **notre estimation de probabilité** est **supérieure** à celle du bookmaker.

### Principe :

```
Si Notre Probabilité > Probabilité Implicite du Bookmaker
   → C'est un VALUE BET ✅
```

### Exemple concret :

**Match : VfL Wolfsburg vs Borussia Dortmund**

| Données                   | Valeur                   |
| ------------------------- | ------------------------ |
| Cote Victoire Dortmund    | 1.81                     |
| Prob. Implicite Bookmaker | 1/1.81 = **55.2%**       |
| Confiance APEX-30         | **70%**                  |
| **Différence (Value)**    | 70% - 55.2% = **+14.8%** |

→ On a **14.8% de value** = Le bookmaker sous-estime Dortmund ! 🔥

---

## 📈 Expected Value (EV) - La Valeur Espérée

L'**EV** (Expected Value) mesure le profit moyen sur le long terme.

### Formule :

```
EV = (Probabilité × Profit) - ((1 - Probabilité) × Mise)

Simplifié pour 1€ :
EV = (Notre_Prob × (Cote - 1)) - (1 - Notre_Prob)
```

### Exemple :

```
Cote = 1.81
Notre Prob = 70% (0.70)

EV = (0.70 × (1.81 - 1)) - (1 - 0.70)
EV = (0.70 × 0.81) - 0.30
EV = 0.567 - 0.30
EV = +0.267 = +26.7%
```

→ Pour chaque 10€ misé, on gagne en moyenne **2.67€** sur le long terme.

---

## 🎯 Recommandations de Mise

Le système génère des recommandations basées sur l'EV et la Value :

| EV    | Value | Recommandation                               |
| ----- | ----- | -------------------------------------------- |
| > 15% | > 10% | 🔥 **EXCELLENT** - Miser 3-5% de la bankroll |
| > 8%  | > 5%  | ✅ **BON** - Miser 2-3% de la bankroll       |
| > 0%  | > 0%  | ⚠️ **MARGINAL** - Miser 1% max               |
| ≤ 0%  | ≤ 0%  | ❌ **PAS DE VALUE** - Ne pas miser           |

### Gestion de Bankroll :

- **Bankroll** = Capital total dédié aux paris
- Ne jamais miser plus de **5%** sur un seul pari
- Adapter la mise selon la value trouvée

---

## 🏆 Championnats Supportés

| Code | Championnat       | Clé API                              |
| ---- | ----------------- | ------------------------------------ |
| PL   | Premier League    | soccer_epl                           |
| BL1  | Bundesliga        | soccer_germany_bundesliga            |
| SA   | Serie A           | soccer_italy_serie_a                 |
| PD   | La Liga           | soccer_spain_la_liga                 |
| FL1  | Ligue 1           | soccer_france_ligue_one              |
| CL   | Champions League  | soccer_uefa_champs_league            |
| EL   | Europa League     | soccer_uefa_europa_league            |
| ECL  | Conference League | soccer_uefa_europa_conference_league |
| DED  | Eredivisie        | soccer_netherlands_eredivisie        |
| PPL  | Primeira Liga     | soccer_portugal_primeira_liga        |

---

## 🔌 Endpoints API

### Récupérer les cotes d'un match

```bash
GET /api/v1/odds/{match_id}
```

**Réponse :**

```json
{
  "match_id": 562,
  "home_team": "VfL Wolfsburg",
  "away_team": "Borussia Dortmund",
  "odds_home": 4.6,
  "odds_draw": 4.21,
  "odds_away": 1.81,
  "odds_updated_at": "2026-02-05T05:48:46"
}
```

### Rafraîchir les cotes d'un match

```bash
POST /api/v1/odds/{match_id}/refresh
```

### Rafraîchir toutes les cotes à venir

```bash
POST /api/v1/odds/refresh-all?limit=50
```

**Réponse :**

```json
{
  "updated": 19,
  "failed": 1,
  "skipped": 0
}
```

### Analyser un Value Bet

```bash
GET /api/v1/odds/{match_id}/value-bet?bet_type=away
```

**Paramètres :**

- `bet_type`: `home`, `draw`, ou `away`

**Réponse :**

```json
{
  "is_value_bet": true,
  "expected_value": 0.267,
  "value_percentage": 14.8,
  "implied_probability": 55.2,
  "our_probability": 70.0,
  "recommendation": "🔥 EXCELLENT - Forte value, miser 3-5% de la bankroll"
}
```

---

## 💡 Stratégie Recommandée

### 1. Identifier les Value Bets

- Utiliser l'endpoint `/value-bet` pour chaque match
- Chercher les paris avec **value > 5%** et **EV > 0.05**

### 2. Filtrer par confiance APEX-30

- Ne parier que si la **confiance APEX-30 > 60%**
- Éviter les matchs avec confiance < 50%

### 3. Diversifier

- Ne pas mettre tous les œufs dans le même panier
- Répartir sur plusieurs matchs avec value positive

### 4. Suivre les résultats

- Utiliser le Journal de Précision pour tracker les gains/pertes
- Ajuster la stratégie selon les résultats

---

## ⚠️ Avertissement

> Les paris sportifs comportent des risques. Ne misez que ce que vous pouvez vous permettre de perdre. Un value bet ne garantit pas de gagner à chaque fois, mais d'être profitable **sur le long terme** si l'analyse est correcte.

---

## 📚 Ressources

- [The Odds API Documentation](https://the-odds-api.com/liveapi/guides/v4/)
- [Kelly Criterion Calculator](https://www.pinnacle.com/en/betting-resources/betting-tools/kelly-criterion-calculator)
- [Understanding Value Betting](https://www.pinnacle.com/en/betting-resources/betting-strategy/value-betting-explained)
