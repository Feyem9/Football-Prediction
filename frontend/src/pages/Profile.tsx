/**
 * Page Profile - Dashboard utilisateur
 */
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export default function Profile() {
  const navigate = useNavigate();
  const { user, isAuthenticated, isLoading, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  // Redirect to login if not authenticated
  if (!isLoading && !isAuthenticated) {
    navigate('/login');
    return null;
  }

  if (isLoading) {
    return (
      <div className="min-h-[calc(100vh-80px)] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-slate-400">Chargement...</p>
        </div>
      </div>
    );
  }

  // Calculate member since
  const memberSince = user?.created_at 
    ? new Date(user.created_at).toLocaleDateString('fr-FR', { 
        year: 'numeric', 
        month: 'long' 
      })
    : 'Janvier 2026';

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">
          👤 Mon Profil
        </h1>
        <p className="text-slate-400">
          Gérez vos informations et paramètres
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Profile Card */}
        <div className="md:col-span-1">
          <div className="glass rounded-2xl p-6 border border-slate-700/50">
            {/* Avatar */}
            <div className="flex flex-col items-center text-center mb-6">
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-4xl shadow-lg shadow-purple-500/20 mb-4">
                {user?.username?.charAt(0).toUpperCase() || '👤'}
              </div>
              <h2 className="text-xl font-bold text-white">
                {user?.username || 'Utilisateur'}
              </h2>
              <p className="text-slate-400 text-sm">
                {user?.email}
              </p>
              
              {/* Verification Badge */}
              <div className={`mt-3 inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium ${
                user?.email_verified 
                  ? 'bg-green-500/10 text-green-400 border border-green-500/30'
                  : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/30'
              }`}>
                {user?.email_verified ? '✓ Email vérifié' : '⚠️ Email non vérifié'}
              </div>
            </div>

            {/* Stats */}
            <div className="border-t border-slate-700/50 pt-6 space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-slate-400 text-sm">Membre depuis</span>
                <span className="text-white font-medium">{memberSince}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400 text-sm">Plan</span>
                <span className="text-blue-400 font-medium">Gratuit</span>
              </div>
            </div>

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="w-full mt-6 py-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 font-medium hover:bg-red-500/20 transition-colors"
            >
              🚪 Se déconnecter
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="md:col-span-2 space-y-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="glass rounded-xl p-4 border border-slate-700/50">
              <div className="text-3xl font-bold text-white">0</div>
              <div className="text-slate-400 text-sm">Pronostics vus</div>
            </div>
            <div className="glass rounded-xl p-4 border border-slate-700/50">
              <div className="text-3xl font-bold text-green-400">0</div>
              <div className="text-slate-400 text-sm">Gagnés</div>
            </div>
            <div className="glass rounded-xl p-4 border border-slate-700/50">
              <div className="text-3xl font-bold text-red-400">0</div>
              <div className="text-slate-400 text-sm">Perdus</div>
            </div>
            <div className="glass rounded-xl p-4 border border-slate-700/50">
              <div className="text-3xl font-bold text-blue-400">--</div>
              <div className="text-slate-400 text-sm">Taux réussite</div>
            </div>
          </div>

          {/* Settings Cards */}
          <div className="glass rounded-2xl p-6 border border-slate-700/50">
            <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              ⚙️ Paramètres
            </h3>
            
            <div className="space-y-4">
              {/* Notifications */}
              <div className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
                <div>
                  <h4 className="text-white font-medium">Notifications Email</h4>
                  <p className="text-slate-400 text-sm">Recevez les pronostics du jour</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" />
                  <div className="w-11 h-6 bg-slate-700 rounded-full peer peer-checked:after:translate-x-full peer-checked:bg-blue-500 after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
                </label>
              </div>

              {/* Dark Mode */}
              <div className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
                <div>
                  <h4 className="text-white font-medium">Mode Sombre</h4>
                  <p className="text-slate-400 text-sm">Toujours activé</p>
                </div>
                <span className="text-green-400">✓ Activé</span>
              </div>

              {/* Language */}
              <div className="flex items-center justify-between p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
                <div>
                  <h4 className="text-white font-medium">Langue</h4>
                  <p className="text-slate-400 text-sm">Interface de l'application</p>
                </div>
                <span className="text-white">🇫🇷 Français</span>
              </div>
            </div>
          </div>

          {/* Upgrade Card */}
          <div className="relative overflow-hidden rounded-2xl p-6 bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/30">
            <div className="absolute top-0 right-0 w-40 h-40 bg-blue-500/10 rounded-full blur-3xl" />
            <div className="relative">
              <span className="inline-block px-3 py-1 rounded-full bg-blue-500/20 text-blue-400 text-sm font-medium mb-3">
                ⭐ PREMIUM
              </span>
              <h3 className="text-xl font-bold text-white mb-2">
                Passez à Premium
              </h3>
              <p className="text-slate-300 mb-4">
                Accédez à tous les pronostics premium, analyses détaillées et plus encore.
              </p>
              <button className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold hover:shadow-lg hover:shadow-purple-500/25 transition-all">
                Voir les offres →
              </button>
            </div>
          </div>

          {/* Danger Zone */}
          <div className="glass rounded-2xl p-6 border border-red-500/20">
            <h3 className="text-xl font-bold text-red-400 mb-4 flex items-center gap-2">
              ⚠️ Zone dangereuse
            </h3>
            <p className="text-slate-400 text-sm mb-4">
              Actions irréversibles sur votre compte
            </p>
            <button className="px-4 py-2 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm font-medium hover:bg-red-500/20 transition-colors">
              Supprimer mon compte
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
