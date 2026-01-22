# 📖 DOCUMENTATION COMPLÈTE - LOGIQUE PAPA

## 🎯 Objectif

Papa analyse le **classement au championnat** et le **niveau de la ligue** pour prédire le résultat.

---

## 📊 ÉTAPE PAR ÉTAPE - Comment Papa calcule

### **ÉTAPE 1 : Récupérer les positions au classement**

```python
# Ligne 412-413 dans prediction_service.py
home_entry = self._get_team_position(standings, match.home_team_id)
away_entry = self._get_team_position(standings, match.away_team_id)
```

**Ce qui se passe** :

- On cherche l'équipe domicile dans le classement
- On cherche l'équipe extérieur dans le classement
- Chaque `entry` contient : `position`, `points`, `won`, `draw`, `lost`, `goalsFor`, `playedGames`, etc.

**Exemple** :

```json
{
  "position": 3,
  "points": 45,
  "playedGames": 20,
  "won": 14,
  "goalsFor": 38,
  "goalsAgainst": 12
}
```

---

### **ÉTAPE 2 : Calculer la "force" basée sur la position**

```python
# Lignes 418-426
if home_entry:
    home_pos = home_entry.get("position", total_teams // 2)  # Ex: position 3
    home_strength = 1 - (home_pos / total_teams)             # Ex: 1 - (3/20) = 0.85
    home_form = self._calculate_form_score(home_entry.get("form", ""))
    home_goals_avg = home_entry.get("goalsFor", 20) / max(1, home_entry.get("playedGames", 1))
else:
    home_strength = 0.5  # Si pas trouvé dans le classement, on met 50%
```

**Explication du calcul de `home_strength`** :

- `total_teams` = nombre total d'équipes au championnat (ex: 20 en Ligue 1)
- `home_pos` = position de l'équipe (ex: 3ème)
- `home_strength = 1 - (position / total)`
  - **1er sur 20** : `1 - (1/20) = 0.95` (95% de force)
  - **10ème sur 20** : `1 - (10/20) = 0.50` (50% de force)
  - **20ème sur 20** : `1 - (20/20) = 0.00` (0% de force)

**Interprétation** :

- Plus l'équipe est bien classée → Plus `home_strength` est élevé
- L'équipe 1ère a 95% de force, la dernière a 0%

---

### **ÉTAPE 3 : Récupérer le niveau du championnat**

```python
# Ligne 466
league_level = self._get_league_strength(match.competition_code)
```

**Ce que contient `LEAGUE_STRENGTH`** (lignes 32-69) :

```python
LEAGUE_STRENGTH = {
    "PL": 1.00,   # Premier League (Angleterre) = 100%
    "PD": 0.98,   # La Liga (Espagne) = 98%
    "BL1": 0.92,  # Bundesliga (Allemagne) = 92%
    "SA": 0.90,   # Serie A (Italie) = 90%
    "FL1": 0.85,  # Ligue 1 (France) = 85%
    "PPL": 0.80,  # Primeira Liga (Portugal) = 80%
    "EL": 0.52,   # Eliteserien (Norvège) = 52%
    "BFL": 0.38,  # Bulgaria = 38%
    # ... etc
}
```

**Pourquoi c'est important** :

- Un 5ème de Premier League peut battre un 1er de Norvège
- Papa compare le NIVEAU du championnat, pas juste la position

---

### **ÉTAPE 4 : Ajuster la force avec le niveau de ligue**

```python
# Lignes 467-468
papa_home_strength = home_strength * league_level
papa_away_strength = away_strength * league_level
```

**Exemple concret : PSG (5ème FL1) vs Bodø/Glimt (1er Norvège)**

**PSG :**

- Position : 5/20 → `home_strength = 1 - (5/20) = 0.75` (75%)
- Ligue 1 : `league_level = 0.85` (85%)
- **Force Papa PSG** : `0.75 × 0.85 = 0.6375` (63.75%)

**Bodø/Glimt :**

- Position : 1/16 → `away_strength = 1 - (1/16) = 0.9375` (93.75%)
- Norvège : `league_level = 0.52` (52%)
- **Force Papa Bodø** : `0.9375 × 0.52 = 0.4875` (48.75%)

**Résultat** : PSG plus fort que Bodø selon Papa (63.75% > 48.75%) malgré une moins bonne position !

---

### **ÉTAPE 5 : Prédire le score**

```python
# Lignes 470-473
papa_home_score, papa_away_score = self._predict_score(
    papa_home_strength, papa_away_strength,
    home_goals_avg, away_goals_avg
)
```

**Comment `_predict_score` fonctionne** (lignes 212-250) :

```python
def _predict_score(self, home_strength, away_strength, home_goals_avg, away_goals_avg):
    # 1. Calculer la différence de force
    strength_diff = home_strength - away_strength

    # 2. Déterminer qui a l'avantage
    if strength_diff > 0.15:  # Domicile beaucoup plus fort
        home_score = round(home_goals_avg * 1.2)  # +20% de buts
        away_score = round(away_goals_avg * 0.8)  # -20% de buts
    elif strength_diff < -0.15:  # Extérieur beaucoup plus fort
        home_score = round(home_goals_avg * 0.8)
        away_score = round(away_goals_avg * 1.2)
    else:  # Match équilibré
        home_score = round(home_goals_avg * 1.0)
        away_score = round(away_goals_avg * 1.0)

    # 3. Limiter les scores extrêmes
    home_score = max(0, min(5, home_score))
    away_score = max(0, min(5, away_score))

    return home_score, away_score
```

**Exemple avec PSG vs Bodø** (suite) :

- Différence : `0.6375 - 0.4875 = 0.15` → Match équilibré (juste au seuil)
- Moyenne buts PSG : 2.1 buts/match
- Moyenne buts Bodø : 1.5 buts/match
- **Score Papa** : `PSG 2 - 2 Bodø` (arrondi à l'entier)

---

### **ÉTAPE 6 : Calculer la confiance**

```python
# Ligne 474
papa_confidence = min(0.9, 0.5 + abs(home_strength - away_strength) * 0.5)
```

**Formule** :

- Confiance de base : 50%
- Bonus : `écart de force × 0.5`
- Maximum : 90%

**Exemples** :

- **Match équilibré** (0.75 vs 0.73) : `0.5 + |0.02| × 0.5 = 0.51` → **51% confiance**
- **Grande différence** (0.95 vs 0.20) : `0.5 + |0.75| × 0.5 = 0.875` → **87.5% confiance**

**Interprétation** :

- Plus l'écart est grand → Plus Papa est sûr de lui
- Match serré → Papa moins confiant

---

### **ÉTAPE 7 : Générer le conseil de pari**

```python
# Ligne 475
papa_tip = self._generate_bet_tip(papa_home_score, papa_away_score, papa_confidence)
```

**Logique** (lignes 252-271) :

```python
def _generate_bet_tip(self, home_score, away_score, confidence):
    if home_score > away_score:
        return f"Victoire domicile ({home_score}-{away_score})"
    elif away_score > home_score:
        return f"Victoire extérieur ({home_score}-{away_score})"
    else:
        return f"Match nul ({home_score}-{away_score})"
```

**Exemple** : Si Papa prédit PSG 2 - 1 Bodø → `"Victoire domicile (2-1)"`

---

## ✅ RÉSUMÉ - Ce que Papa fait :

1. ✅ Récupère la position de chaque équipe au classement
2. ✅ Calcule une "force" (0-1) basée sur la position
3. ✅ Ajuste cette force selon le niveau du championnat
4. ✅ Compare les forces pour prédire un score
5. ✅ Calcule sa confiance selon l'écart entre les équipes
6. ✅ Génère un conseil de pari

---

## 🔮 AMÉLIORATIONS PRÉVUES :

### **1. Détecter les matchs importants à venir (3 jours)**

```python
# À implémenter dans _predict_papa_logic()
upcoming_important_match = self._check_upcoming_important_match(team_id, match_date)
if upcoming_important_match:
    # Réduire la confiance de 10-20%
    papa_confidence *= 0.85
    # Ou prédire un score plus serré (rotation d'effectif)
```

### **2. Détecter les matchs importants récents (3 jours)**

```python
recent_important_match = self._check_recent_important_match(team_id, match_date)
if recent_important_match:
    # Équipe fatiguée → réduire la force
    papa_home_strength *= 0.90
```

### **3. Vérifier si c'est le même championnat**

```python
# Si match CL mais équipes de championnats différents
if competition_code == "CL":
    # Comparer les championnats domestiques
    home_league = get_domestic_league(home_team_id)  # Ex: "FL1"
    away_league = get_domestic_league(away_team_id)  # Ex: "EL"
    # Utiliser les standings domestiques au lieu de CL
```

---

## 📝 NOTES TECHNIQUES :

**Constantes importantes** :

- `WEIGHT_STANDINGS = 0.35` (35% du poids total sur position)
- `WEIGHT_LEAGUE = 0.15` (15% du poids total sur niveau ligue)
- `HOME_ADVANTAGE = 0.12` (12% bonus domicile de base)

**Limites actuelles** :

- Ne prend pas encore en compte la fatigue (matchs récents)
- Ne prend pas encore en compte la rotation (matchs importants à venir)
- Pour matchs CL, utilise le classement CL au lieu des championnats domestiques

---

**Fichier source** : `/backend/app/services/prediction_service.py`
**Lignes** : 464-476 (Logique Papa)
