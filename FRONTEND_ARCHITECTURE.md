# 🎨 Architecture Frontend Pronoscore

## Vue d'Ensemble

Application web moderne pour consulter les matchs et prédictions de football.

---

## Stack Technologique

| Technologie       | Rôle             | Justification             |
| ----------------- | ---------------- | ------------------------- |
| **Next.js 15**    | Framework        | SSR, routing, performance |
| **TypeScript**    | Type safety      | Robustesse du code        |
| **Tailwind CSS**  | Styling          | Rapidité, moderne         |
| **Zustand**       | State management | Léger, simple             |
| **React Query**   | API fetching     | Cache, refetch auto       |
| **Framer Motion** | Animations       | UX premium                |

---

## Structure des Dossiers

```
frontend/
├── src/
│   ├── app/                    # App Router (Next.js 15)
│   │   ├── page.tsx            # Homepage
│   │   ├── layout.tsx          # Layout principal
│   │   ├── matches/
│   │   │   ├── page.tsx        # Liste des matchs
│   │   │   └── [id]/
│   │   │       └── page.tsx    # Détail match + prédiction
│   │   ├── standings/
│   │   │   └── [competition]/
│   │   │       └── page.tsx    # Classement par compétition
│   │   ├── predictions/
│   │   │   └── page.tsx        # Toutes les prédictions
│   │   ├── auth/
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   └── profile/
│   │       └── page.tsx        # Profil utilisateur
│   │
│   ├── components/
│   │   ├── ui/                 # Composants réutilisables
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Badge.tsx
│   │   │   └── Skeleton.tsx
│   │   ├── matches/
│   │   │   ├── MatchCard.tsx
│   │   │   ├── MatchList.tsx
│   │   │   └── LiveScore.tsx
│   │   ├── predictions/
│   │   │   ├── PredictionCard.tsx
│   │   │   ├── LogicBreakdown.tsx   # Affiche les 3 logiques
│   │   │   └── ConsensusIndicator.tsx
│   │   ├── standings/
│   │   │   ├── StandingsTable.tsx
│   │   │   └── TeamRow.tsx
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Footer.tsx
│   │       ├── Sidebar.tsx
│   │       └── Navigation.tsx
│   │
│   ├── lib/
│   │   ├── api.ts              # Client API (fetch wrapper)
│   │   ├── auth.ts             # Logique auth (JWT)
│   │   └── utils.ts            # Helpers
│   │
│   ├── hooks/
│   │   ├── useMatches.ts
│   │   ├── usePrediction.ts
│   │   ├── useAuth.ts
│   │   └── useStandings.ts
│   │
│   ├── types/
│   │   ├── match.ts
│   │   ├── prediction.ts
│   │   ├── user.ts
│   │   └── api.ts
│   │
│   └── styles/
│       └── globals.css
│
├── public/
│   ├── icons/
│   └── images/
│
├── tailwind.config.ts
├── next.config.js
└── package.json
```

---

## Pages Principales

### 1. Homepage (`/`)

- Hero avec match du jour
- Prédictions du jour (les plus sûres)
- Compétitions rapides

### 2. Matchs (`/matches`)

- Filtres: compétition, date, statut
- Cards de matchs avec scores/prédictions
- Vue calendrier optionnelle

### 3. Détail Match (`/matches/[id]`)

- Score (ou prédiction si à venir)
- **3 Logiques de prédiction** (Papa, Grand Frère, Ma Logique)
- Indicateur de consensus
- Statistiques H2H

### 4. Classements (`/standings/[competition]`)

- Tableau interactif
- Forme récente (5 derniers matchs)
- Stats cliquables

### 5. Authentification (`/auth/*`)

- Login / Register
- Forgot password
- OAuth (futur)
- Profile
- Logout

---

## Composant Clé: PredictionCard

```tsx
// components/predictions/PredictionCard.tsx
interface PredictionCardProps {
  homeTeam: string;
  awayTeam: string;
  homeGoals: number;
  awayGoals: number;
  confidence: number;
  consensus: "FORT" | "MOYEN" | "FAIBLE";
  logics: {
    papa?: { betTip: string; confidence: number };
    grandFrere?: { betTip: string; confidence: number };
    maLogique?: { betTip: string; confidence: number };
  };
}
```

---

## Intégration API

```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchMatches(params?: {
  competition?: string;
  limit?: number;
}) {
  const response = await fetch(
    `${API_BASE}/api/v1/matches?${new URLSearchParams(params)}`
  );
  return response.json();
}

export async function fetchCombinedPrediction(matchId: number) {
  const response = await fetch(
    `${API_BASE}/api/v1/matches/${matchId}/prediction/combined`
  );
  return response.json();
}
```

---

## Design System

### Couleurs

```css
:root {
  --primary: #3b82f6; /* Bleu */
  --secondary: #10b981; /* Vert */
  --accent: #f59e0b; /* Orange */
  --background: #0f172a; /* Dark */
  --card: #1e293b;
  --text: #f8fafc;
}
```

### Indicateurs de Consensus

| Niveau | Couleur  | Badge             |
| ------ | -------- | ----------------- |
| FORT   | 🟢 Vert  | Haute confiance   |
| MOYEN  | 🟡 Jaune | Confiance modérée |
| FAIBLE | 🔴 Rouge | Faible confiance  |

---

## Prochaines Étapes

1. **Créer le projet Next.js** avec TypeScript
2. **Configurer Tailwind** avec le design system
3. **Implémenter les pages** dans l'ordre:
   - Homepage
   - Liste des matchs
   - Détail match avec prédictions
   - Classements
   - Auth
4. **Tester** l'intégration avec le backend
5. **Déployer** sur Vercel

---

## Estimation

| Phase                | Durée      |
| -------------------- | ---------- |
| Setup & Config       | 1-2h       |
| Homepage             | 2-3h       |
| Matchs & Prédictions | 4-5h       |
| Classements          | 2h         |
| Auth                 | 3h         |
| Polish & Tests       | 3h         |
| **Total**            | **15-18h** |
