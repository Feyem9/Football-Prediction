/**
 * Page Login - Design Ultra Dynamique avec Animations
 */
import { useState, useEffect, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

// Particule flottante
interface Particle {
  id: number;
  x: number;
  y: number;
  size: number;
  duration: number;
  delay: number;
}

// Particules statiques (générées une seule fois)
const PARTICLES: Particle[] = Array.from({ length: 20 }, (_, i) => ({
  id: i,
  x: (i * 5) % 100,
  y: (i * 7) % 100,
  size: 2 + (i % 4),
  duration: 10 + (i % 10),
  delay: i % 5
}));

export default function Login() {
  const navigate = useNavigate();
  const { login, isLoading, error, clearError } = useAuth();
  
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovering, setIsHovering] = useState(false);


  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();

    const result = await login(formData);
    if (result.success) {
      navigate('/profile');
    }
  };

  return (
    <div className="min-h-[calc(100vh-80px)] flex items-center justify-center px-4 py-12 overflow-hidden">
      {/* Arrière-plan dynamique animé */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {/* Gradient mesh animé */}
        <div 
          className="absolute inset-0 opacity-30"
          style={{
            background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(59, 130, 246, 0.3) 0%, transparent 50%)`
          }}
        />
        
        {/* Orbes flottants */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-r from-blue-500/20 to-cyan-500/20 rounded-full blur-3xl animate-[float_8s_ease-in-out_infinite]" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-full blur-3xl animate-[float_10s_ease-in-out_infinite_reverse]" />
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-gradient-to-r from-indigo-500/15 to-violet-500/15 rounded-full blur-3xl animate-[float_12s_ease-in-out_infinite]" />
        
        {/* Particules */}
        {PARTICLES.map((particle) => (
          <div
            key={particle.id}
            className="absolute rounded-full bg-white/10 animate-[floatUp_linear_infinite]"
            style={{
              left: `${particle.x}%`,
              bottom: '-10%',
              width: `${particle.size}px`,
              height: `${particle.size}px`,
              animationDuration: `${particle.duration}s`,
              animationDelay: `${particle.delay}s`
            }}
          />
        ))}
        
        {/* Lignes de grille */}
        <div className="absolute inset-0 opacity-5">
          <div className="h-full w-full" style={{
            backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
            backgroundSize: '50px 50px'
          }} />
        </div>
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Card avec effet glass morphism avancé */}
        <div 
          className={`relative rounded-3xl p-8 md:p-10 border transition-all duration-500 ${
            isHovering 
              ? 'border-blue-500/50 shadow-[0_0_60px_-12px_rgba(59,130,246,0.5)]' 
              : 'border-slate-700/50 shadow-2xl'
          }`}
          style={{
            background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%)',
            backdropFilter: 'blur(20px)'
          }}
          onMouseEnter={() => setIsHovering(true)}
          onMouseLeave={() => setIsHovering(false)}
        >
          {/* Bordure brillante animée */}
          <div className="absolute inset-0 rounded-3xl overflow-hidden">
            <div className="absolute inset-0 opacity-0 hover:opacity-100 transition-opacity duration-500">
              <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-blue-500 to-transparent animate-[shimmer_2s_infinite]" />
            </div>
          </div>

          {/* Header avec animation */}
          <div className="text-center mb-8 relative">
            {/* Logo animé */}
            <div className="inline-flex items-center justify-center relative">
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 blur-xl opacity-50 animate-pulse" />
              <div className="relative w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-purple-500/30 transform hover:scale-110 hover:rotate-3 transition-all duration-300">
                <span className="text-4xl animate-bounce">⚽</span>
              </div>
            </div>
            
            <h1 className="text-3xl font-bold text-white mt-6 mb-2 animate-[fadeInUp_0.6s_ease-out]">
              Bon retour !
            </h1>
            <p className="text-slate-400 animate-[fadeInUp_0.6s_ease-out_0.1s_both]">
              Connectez-vous pour accéder à vos pronostics
            </p>
          </div>

          {/* Message d'erreur animé */}
          {error && (
            <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm flex items-center gap-3 animate-[shake_0.5s_ease-in-out]">
              <span className="text-xl animate-pulse">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email avec animation */}
            <div className={`transform transition-all duration-300 ${focusedField === 'email' ? 'scale-[1.02]' : ''}`}>
              <label className={`block text-sm font-medium mb-2 transition-colors duration-300 ${focusedField === 'email' ? 'text-blue-400' : 'text-slate-300'}`}>
                Email
              </label>
              <div className="relative group">
                {/* Glow effect */}
                <div className={`absolute -inset-1 rounded-xl bg-gradient-to-r from-blue-500 to-purple-500 opacity-0 blur transition-all duration-300 ${focusedField === 'email' ? 'opacity-30' : 'group-hover:opacity-20'}`} />
                
                <div className="relative">
                  <span className={`absolute left-4 top-1/2 -translate-y-1/2 transition-all duration-300 ${focusedField === 'email' ? 'text-blue-400 scale-110' : 'text-slate-500'}`}>
                    📧
                  </span>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    onFocus={() => setFocusedField('email')}
                    onBlur={() => setFocusedField(null)}
                    className="w-full pl-12 pr-4 py-4 rounded-xl bg-slate-800/50 border border-slate-700 text-white placeholder-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 transition-all outline-none"
                    placeholder="votre@email.com"
                  />
                </div>
              </div>
            </div>

            {/* Password avec animation */}
            <div className={`transform transition-all duration-300 ${focusedField === 'password' ? 'scale-[1.02]' : ''}`}>
              <label className={`block text-sm font-medium mb-2 transition-colors duration-300 ${focusedField === 'password' ? 'text-blue-400' : 'text-slate-300'}`}>
                Mot de passe
              </label>
              <div className="relative group">
                {/* Glow effect */}
                <div className={`absolute -inset-1 rounded-xl bg-gradient-to-r from-blue-500 to-purple-500 opacity-0 blur transition-all duration-300 ${focusedField === 'password' ? 'opacity-30' : 'group-hover:opacity-20'}`} />
                
                <div className="relative">
                  <span className={`absolute left-4 top-1/2 -translate-y-1/2 transition-all duration-300 ${focusedField === 'password' ? 'text-blue-400 scale-110' : 'text-slate-500'}`}>
                    🔒
                  </span>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    onFocus={() => setFocusedField('password')}
                    onBlur={() => setFocusedField(null)}
                    className="w-full pl-12 pr-12 py-4 rounded-xl bg-slate-800/50 border border-slate-700 text-white placeholder-slate-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 transition-all outline-none"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-all duration-300 hover:scale-110"
                  >
                    {showPassword ? '🙈' : '👁️'}
                  </button>
                </div>
              </div>
            </div>

            {/* Forgot Password */}
            <div className="flex justify-end">
              <Link 
                to="/forgot-password" 
                className="text-sm text-blue-400 hover:text-blue-300 transition-all duration-300 hover:translate-x-1"
              >
                Mot de passe oublié ? →
              </Link>
            </div>

            {/* Submit Button avec effet ripple */}
            <button
              type="submit"
              disabled={isLoading}
              className="relative w-full py-4 rounded-xl overflow-hidden font-bold text-lg text-white transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed group"
            >
              {/* Background gradient animé */}
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 via-purple-500 to-blue-500 bg-[length:200%_100%] animate-[gradientMove_3s_linear_infinite]" />
              
              {/* Shine effect */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
              </div>
              
              {/* Shadow */}
              <div className="absolute inset-0 shadow-lg shadow-purple-500/30 group-hover:shadow-purple-500/50 transition-all duration-300" />
              
              {/* Content */}
              <span className="relative flex items-center justify-center gap-2">
                {isLoading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Connexion...
                  </>
                ) : (
                  <>
                    Se connecter
                    <span className="group-hover:translate-x-1 transition-transform duration-300">→</span>
                  </>
                )}
              </span>
            </button>
          </form>

          {/* Divider animé */}
          <div className="flex items-center gap-4 my-8">
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-slate-600 to-transparent" />
            <span className="text-slate-500 text-sm px-2">ou</span>
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-slate-600 to-transparent" />
          </div>

          {/* Register Link */}
          <p className="text-center text-slate-400">
            Pas encore de compte ?{' '}
            <Link 
              to="/register" 
              className="text-blue-400 hover:text-blue-300 font-semibold transition-all duration-300 relative group"
            >
              <span className="relative">
                Créer un compte
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-blue-400 group-hover:w-full transition-all duration-300" />
              </span>
            </Link>
          </p>
        </div>

        {/* Trust Badges avec animation */}
        <div className="mt-8 flex justify-center gap-8">
          <span className="flex items-center gap-2 text-slate-500 text-sm hover:text-slate-400 transition-colors duration-300 cursor-default group">
            <span className="text-green-400 group-hover:scale-110 transition-transform duration-300">🔒</span>
            SSL Sécurisé
          </span>
          <span className="flex items-center gap-2 text-slate-500 text-sm hover:text-slate-400 transition-colors duration-300 cursor-default group">
            <span className="text-blue-400 group-hover:scale-110 transition-transform duration-300">✓</span>
            RGPD Conforme
          </span>
        </div>
      </div>

      {/* Styles pour les animations */}
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0) translateX(0); }
          25% { transform: translateY(-20px) translateX(10px); }
          50% { transform: translateY(-10px) translateX(-10px); }
          75% { transform: translateY(-30px) translateX(5px); }
        }
        
        @keyframes floatUp {
          0% { transform: translateY(0); opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { transform: translateY(-100vh); opacity: 0; }
        }
        
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-5px); }
          75% { transform: translateX(5px); }
        }
        
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        
        @keyframes gradientMove {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
      `}</style>
    </div>
  );
}
