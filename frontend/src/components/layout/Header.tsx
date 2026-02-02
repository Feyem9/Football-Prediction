/**
 * Header Component - Navigation Mobile-First avec Auth
 */
import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

export default function Header() {
  const location = useLocation();
  const { user, isAuthenticated, isLoading , logout} = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  
  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  const navLinks = [
    { path: '/', label: 'Accueil', icon: '🏠' },
    { path: '/sure', label: 'Match Sûr', icon: '🎯' },
    { path: '/history', label: 'Historique', icon: '📊' },
    { path: '/today', label: 'Aujourd\'hui', icon: '📅' },
    { path: '/matches', label: 'Matchs', icon: '⚽' },
    { path: '/standings/PL', label: 'Classements', icon: '🏆' },
  ];

  const handleLogout = async () => {
    await logout();
    setUserMenuOpen(false);
  };
  
  return (
    <header className="sticky top-0 z-50 glass border-b border-slate-700/50">
      <nav className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <span className="text-2xl md:text-3xl group-hover:rotate-12 transition-transform duration-300">⚽</span>
            <span className="text-xl md:text-2xl font-black">
              <span className="text-blue-400">Prono</span>
              <span className="text-purple-400">score</span>
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-2">
            {navLinks.map((link) => (
              <Link 
                key={link.path}
                to={link.path} 
                className={`px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${
                  isActive(link.path)
                    ? 'bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-white border border-blue-500/30' 
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                {link.label}
              </Link>
            ))}
            
            {/* Lien Profil - visible uniquement quand connecté */}
            {isAuthenticated && (
              <Link 
                to="/profile" 
                className={`px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${
                  isActive('/profile')
                    ? 'bg-gradient-to-r from-purple-500/20 to-pink-500/20 text-white border border-purple-500/30' 
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                👤 Profil
              </Link>
            )}
          </div>

          {/* Auth Button - Desktop */}
          <div className="hidden md:flex items-center gap-3 ml-4">
            {isLoading ? (
              <div className="w-8 h-8 rounded-full bg-slate-700 animate-pulse" />
            ) : isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 hover:border-blue-500/50 transition-all"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-sm font-bold">
                    {user?.username?.charAt(0).toUpperCase() || '👤'}
                  </div>
                  <span className="text-sm text-white font-medium max-w-[100px] truncate">
                    {user?.username}
                  </span>
                  <svg className={`w-4 h-4 text-slate-400 transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* Dropdown Menu */}
                {userMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 glass rounded-xl border border-slate-700/50 shadow-xl py-2 z-50">
                    <Link
                      to="/profile"
                      onClick={() => setUserMenuOpen(false)}
                      className="flex items-center gap-3 px-4 py-2.5 text-slate-300 hover:text-white hover:bg-slate-800/50 transition-colors"
                    >
                      <span>👤</span> Mon Profil
                    </Link>
                    <Link
                      to="/history"
                      onClick={() => setUserMenuOpen(false)}
                      className="flex items-center gap-3 px-4 py-2.5 text-slate-300 hover:text-white hover:bg-slate-800/50 transition-colors"
                    >
                      <span>📊</span> Historique
                    </Link>
                    <div className="border-t border-slate-700 my-2" />
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-red-400 hover:bg-red-500/10 transition-colors"
                    >
                      <span>🚪</span> Déconnexion
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <Link
                to="/login"
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 text-white text-sm font-bold shadow-lg shadow-purple-500/20 hover:shadow-purple-500/30 hover:scale-105 transition-all"
              >
                Connexion
              </Link>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button 
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-slate-800 transition-colors"
            aria-label="Toggle menu"
          >
            <div className="w-6 h-5 flex flex-col justify-between">
              <span className={`h-0.5 bg-white rounded transition-all duration-300 ${mobileMenuOpen ? 'rotate-45 translate-y-2' : ''}`} />
              <span className={`h-0.5 bg-white rounded transition-all duration-300 ${mobileMenuOpen ? 'opacity-0' : ''}`} />
              <span className={`h-0.5 bg-white rounded transition-all duration-300 ${mobileMenuOpen ? '-rotate-45 -translate-y-2' : ''}`} />
            </div>
          </button>
        </div>

        {/* Mobile Menu */}
        <div className={`md:hidden overflow-hidden transition-all duration-300 ${mobileMenuOpen ? 'max-h-80 mt-4' : 'max-h-0'}`}>
          <div className="flex flex-col gap-2 pb-4">
            {navLinks.map((link) => (
              <Link 
                key={link.path}
                to={link.path} 
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${
                  isActive(link.path)
                    ? 'bg-gradient-to-r from-blue-500/20 to-purple-500/20 text-white border border-blue-500/30' 
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                <span>{link.icon}</span>
                {link.label}
              </Link>
            ))}
            
            {/* Lien Profil mobile - visible uniquement quand connecté */}
            {isAuthenticated && (
              <Link 
                to="/profile" 
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-semibold transition-all ${
                  isActive('/profile')
                    ? 'bg-gradient-to-r from-purple-500/20 to-pink-500/20 text-white border border-purple-500/30' 
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                <span>👤</span>
                Mon Profil
              </Link>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
}
