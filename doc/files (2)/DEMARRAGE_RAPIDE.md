# 🚀 GUIDE DE DÉMARRAGE RAPIDE - APEX-30

## ⏱️ Temps de lecture: 5 minutes

### Étape 1️⃣: Tester avec l'exemple (2 minutes)

```bash
# Lancer l'exemple intégré
python apex30_pronostic.py

# Vous verrez une analyse complète PSG vs Lyon
# avec tous les scores détaillés et la décision finale
```

**Résultat attendu:**
- Rapport complet affiché dans le terminal
- Fichier `rapport_analyse.txt` créé
- Décision claire avec niveau de confiance et mise recommandée

---

### Étape 2️⃣: Valider votre premier match (3 minutes)

```bash
# 1. Copier le template vierge
cp template_vierge.json mon_premier_match.json

# 2. Éditer avec vos données (utilisez votre éditeur préféré)
nano mon_premier_match.json
# ou
vim mon_premier_match.json
# ou ouvrez avec votre éditeur de texte

# 3. Valider le fichier
python valider_config.py mon_premier_match.json

# 4. Si valide, lancer l'analyse
python charger_json.py mon_premier_match.json
```

---

### Étape 3️⃣: Comprendre le résultat (2 minutes)

Après l'analyse, vous obtenez:

**1. Rapport texte (`*_rapport.txt`)**
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

**2. Résultat JSON (`*_resultat.json`)**
```json
{
  "decision": {
    "favori": "Paris SG",
    "confiance": "Forte confiance",
    "pronostic": "Victoire Paris SG",
    "mise_recommandee": "3-5%",
    "parier": true
  }
}
```

---

## 🎯 RÈGLES D'UTILISATION SIMPLES

### ✅ À FAIRE
1. **Analyser au minimum 10 matchs AVANT de parier réellement**
2. **Ne parier QUE si "parier: true" dans le résultat**
3. **Respecter STRICTEMENT les mises recommandées**
4. **Tenir un journal de vos paris** (utilisez `tracker_performance.py`)
5. **Spécialiser sur 1-2 championnats maximum**

### ❌ À NE PAS FAIRE
1. **Parier sur tous les matchs** → Sélectivité = clé du succès
2. **Augmenter les mises après une perte** → Ruine assurée
3. **Ignorer les avertissements du système**
4. **Parier sur un match "pour l'action"** → Émotion ≠ profit
5. **Modifier les mises recommandées à la hausse**

---

## 📊 INTERPRÉTER LES NIVEAUX DE CONFIANCE

| Confiance | Écart Score | Action | Mise |
|-----------|-------------|---------|------|
| **Incertitude** | < 0.5 | ❌ NE PAS PARIER | 0% |
| **Match serré** | 0.5 - 1.5 | ⚠️ Prudence extrême | 1% max |
| **Confiance modérée** | 1.5 - 2.5 | ✅ Pari acceptable | 2-3% |
| **Forte confiance** | > 2.5 | ✅ Excellent pari | 3-5% |

**Important:** Même avec "Forte confiance", il y a risque de perte!

---

## 🔢 DONNÉES MINIMALES REQUISES

### Pour CHAQUE équipe, collectez:

**OBLIGATOIRE (minimum):**
- 5 derniers matchs (résultats V/N/D, buts pour/contre)
- Classement actuel
- Moyenne points/match domicile et extérieur
- Match à domicile ou extérieur?

**FORTEMENT RECOMMANDÉ:**
- 10 derniers matchs (au lieu de 5)
- Expected Goals (xG) pour chaque match
- Joueurs absents importants
- Matchs importants dans les 7 jours avant/après
- Historique des 5 dernières confrontations

**OPTIONNEL (bonus):**
- Tirs cadrés, possession, corners
- Cotes du marché
- Contexte (derby, pression entraîneur, etc.)

---

## 🌐 OÙ TROUVER LES DONNÉES?

### Sites Gratuits Recommandés:

**1. FBref.com** → Statistiques avancées (xG, possession)
```
fbref.com → Recherchez l'équipe → Stats
```

**2. FlashScore.fr** → Résultats et calendrier
```
flashscore.fr → Équipe → Résultats/Calendrier
```

**3. Transfermarkt.fr** → Effectifs et absences
```
transfermarkt.fr → Équipe → Effectif → Blessures
```

**4. Sofascore.com** → Statistiques match par match
```
sofascore.com → Équipe → Derniers matchs
```

---

## ⚡ WORKFLOW RAPIDE (15 minutes par match)

```
1. Ouvrir template_vierge.json → 30 secondes
2. Collecter données Équipe A → 5 minutes
   - FBref: 10 derniers matchs + xG
   - Transfermarkt: absences
3. Collecter données Équipe B → 5 minutes
4. Ajouter H2H et cotes → 2 minutes
5. Valider le fichier → 10 secondes
   python valider_config.py mon_match.json
6. Lancer l'analyse → 5 secondes
   python charger_json.py mon_match.json
7. Lire le rapport et décider → 2 minutes
```

---

## 📈 GESTION DE BANKROLL 101

### Exemple avec 1000€ de bankroll:

```
Bankroll totale: 1000€ = 100 unités (1 unité = 10€)

Paris par niveau:
- Forte confiance (5 unités): 50€
- Confiance modérée (3 unités): 30€
- Match serré (1 unité): 10€

RÈGLES STRICTES:
✅ Maximum 5% (50€) sur UN seul pari
✅ Maximum 15% (150€) engagés en même temps
❌ JAMAIS dépasser ces limites
```

**Pourquoi ces limites?**
- Vous protègent de la ruine
- Permettent de survivre aux séries de pertes
- Capitalisent sur les séries de gains

---

## 🎓 VOTRE PREMIER MOIS

### Semaine 1-2: Formation (0€ misé)
- Analysez 20-30 matchs
- Notez vos prédictions
- Comparez avec les résultats réels
- Identifiez vos points forts

### Semaine 3-4: Test en conditions réelles (mises minimales)
- Pariez 0.5% par pari maximum
- Appliquez STRICTEMENT le système
- Tenez votre journal religieusement
- Analysez vos erreurs

### Mois 2+: Montée en puissance
- Si ROI > 5% après 50 paris → Augmentez à 1-5%
- Si ROI < 0% → STOP, analysez, ajustez
- Spécialisez-vous sur ce qui fonctionne

---

## 🆘 PROBLÈMES COURANTS

**Q: "J'ai un taux de réussite de 70% mais je perds de l'argent"**
R: Vous pariez à trop faibles cotes. Visez minimum 1.80

**Q: "Le système me dit de ne pas parier sur 90% des matchs"**
R: ✅ PARFAIT! C'est le but. Qualité > Quantité

**Q: "Je n'ai pas toutes les données (xG, etc.)"**
R: Le système fonctionne quand même, mais avec moins de précision

**Q: "Puis-je modifier les poids des modules?"**
R: Oui, mais SEULEMENT après 100+ paris analysés

**Q: "Ça prend trop de temps de collecter les données"**
R: Normal au début. Après 10 matchs, vous serez 3x plus rapide

---

## ✅ CHECKLIST AVANT VOTRE PREMIER PARI

- [ ] J'ai analysé au moins 10 matchs en mode "entraînement"
- [ ] J'ai défini ma bankroll totale
- [ ] J'ai calculé la taille de 1 unité (1% de ma bankroll)
- [ ] Le système indique "parier: true"
- [ ] Le niveau de confiance est au moins "Confiance modérée"
- [ ] Je respecte la mise recommandée SANS l'augmenter
- [ ] J'ai un fichier Excel/Google Sheets pour tracer mes paris
- [ ] Je sais que je peux perdre cette mise
- [ ] Je ne parie PAS sous le coup de l'émotion

---

## 🎯 OBJECTIF RÉALISTE

**Mois 1-3:** ROI de 0-5% (apprentissage)
**Mois 4-6:** ROI de 5-10% (maîtrise)
**Mois 7+:** ROI de 10-15% (expertise)

**Si vous atteignez 15% de ROI constant sur 100+ paris:**
Félicitations, vous faites partie des 5% meilleurs!

---

## ⚠️ AVERTISSEMENT FINAL

**Le gambling peut créer une dépendance.**

Si vous constatez:
- Augmentation progressive de vos mises
- Besoin de "récupérer" les pertes
- Paris en dehors du système
- Stress ou anxiété liés aux paris
- Impact négatif sur votre vie

→ **ARRÊTEZ IMMÉDIATEMENT** et consultez un spécialiste.

---

## 📞 PROCHAINES ÉTAPES

1. ✅ Lancer l'exemple: `python apex30_pronostic.py`
2. ✅ Lire le README.md complet
3. ✅ Analyser votre premier match
4. ✅ Tenir votre journal avec `tracker_performance.py`

**Bon courage et que la discipline soit avec vous! 🎯**

---

*Système APEX-30 - La patience et la discipline battent toujours l'impulsivité*
