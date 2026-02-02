/**
 * Pronoscore App - Application de prédictions de football
 * 
 * Structure:
 * - /                 : Liste des matchs
 * - /today            : Matchs du jour (terminés, en cours, à venir)
 * - /matches/:id      : Détail d'un match avec prédiction
 * - /standings/:comp  : Classements par compétition
 * - /login            : Connexion utilisateur
 * - /register         : Inscription utilisateur
 * - /profile          : Profil utilisateur
 */
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/layout/Header';
import Home from './pages/Home';
import TodayMatches from './pages/TodayMatches';
import SureMatch from './pages/SureMatch';
import History from './pages/History';
import MatchDetail from './pages/MatchDetail';
import Standings from './pages/Standings';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <Header />
        <main className="pb-12">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/today" element={<TodayMatches />} />
            <Route path="/sure" element={<SureMatch />} />
            <Route path="/history" element={<History />} />
            <Route path="/matches" element={<Home />} />
            <Route path="/matches/:id" element={<MatchDetail />} />
            <Route path="/standings" element={<Standings />} />
            <Route path="/standings/:competition" element={<Standings />} />
            {/* Auth Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </main>
        
        {/* Footer */}
        <footer className="bg-slate-900/50 border-t border-slate-800 py-6">
          <div className="container mx-auto px-4 text-center">
            <p className="text-slate-500 text-sm">
              ⚽ Pronoscore 2026 - Prédictions basées sur 3 logiques familiales
            </p>
            <p className="text-slate-600 text-xs mt-2">
              API: football-prediction-mbil.onrender.com
            </p>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;
