/**
 * Page Register - Design Ultra Dynamique avec Animations Avancées
 */
import { useState, useEffect, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

// Particule type
interface Particle {
  id: number;
  x: number;
  y: number;
  size: number;
  color: string;
  duration: number;
  delay: number;
}

// Étape du formulaire
type FormStep = 1 | 2 | 3;

// Particules statiques
const COLORS = ['from-purple-500', 'from-blue-500', 'from-pink-500', 'from-cyan-500'];
const PARTICLES: Particle[] = Array.from({ length: 25 }, (_, i) => ({
  id: i,
  x: (i * 4) % 100,
  y: (i * 7) % 100,
  size: 2 + (i % 6),
  color: COLORS[i % COLORS.length],
  duration: 10 + (i % 15),
  delay: i % 8
}));

export default function Register() {
  const { register, isLoading, error, clearError } = useAuth();
  
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [success, setSuccess] = useState(false);
  const [validationError, setValidationError] = useState('');
  const [currentStep, setCurrentStep] = useState<FormStep>(1);
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [typingEffect, setTypingEffect] = useState('');
  const [confetti, setConfetti] = useState<{x: number; y: number; color: string}[]>([]);

  // Texte qui s'écrit
  const welcomeText = "Rejoignez l'aventure ! 🚀";
  
  useEffect(() => {
    let index = 0;
    const timer = setInterval(() => {
      if (index <= welcomeText.length) {
        setTypingEffect(welcomeText.slice(0, index));
        index++;
      } else {
        clearInterval(timer);
      }
    }, 80);
    return () => clearInterval(timer);
  }, []);



  // Suivi de la souris
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Password strength checker
  const getPasswordStrength = (password: string) => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^a-zA-Z0-9]/.test(password)) strength++;
    return strength;
  };

  const passwordStrength = getPasswordStrength(formData.password);
  const strengthLabels = ['Très faible', 'Faible', 'Moyen', 'Fort', 'Très fort'];
  const strengthColors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-400', 'bg-green-500'];
  const strengthEmojis = ['😰', '😟', '😐', '😊', '🔥'];

  // Validation par étape
  const canProceedToStep2 = formData.username.length >= 3 && formData.email.includes('@');
  const canProceedToStep3 = formData.password.length >= 8 && formData.password === formData.confirmPassword;

  // Animation confetti
  const triggerConfetti = () => {
    const newConfetti = [];
    const colors = ['#3B82F6', '#8B5CF6', '#EC4899', '#10B981', '#F59E0B'];
    for (let i = 0; i < 50; i++) {
      newConfetti.push({
        x: Math.random() * 100,
        y: Math.random() * 100,
        color: colors[Math.floor(Math.random() * colors.length)]
      });
    }
    setConfetti(newConfetti);
    setTimeout(() => setConfetti([]), 3000);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();
    setValidationError('');

    if (formData.password !== formData.confirmPassword) {
      setValidationError('Les mots de passe ne correspondent pas');
      return;
    }

    if (formData.password.length < 8) {
      setValidationError('Le mot de passe doit contenir au moins 8 caractères');
      return;
    }

    if (formData.username.length < 3) {
      setValidationError('Le nom d\'utilisateur doit contenir au moins 3 caractères');
      return;
    }

    const result = await register({
      username: formData.username,
      email: formData.email,
      password: formData.password
    });

    if (result.success) {
      triggerConfetti();
      setSuccess(true);
    }
  };

  // Page de succès
  if (success) {
    return (
      <div className="min-h-[calc(100vh-80px)] flex items-center justify-center px-4 py-12 relative overflow-hidden">
        {/* Confetti */}
        {confetti.map((c, i) => (
          <div
            key={i}
            className="absolute w-3 h-3 rounded-full animate-[confettiFall_3s_ease-out_forwards]"
            style={{
              left: `${c.x}%`,
              top: '-5%',
              backgroundColor: c.color,
              animationDelay: `${Math.random() * 0.5}s`
            }}
          />
        ))}

        <div className="w-full max-w-md relative z-10">
          <div 
            className="rounded-3xl p-8 md:p-10 border border-slate-700/50 shadow-2xl text-center animate-[scaleIn_0.5s_ease-out]"
            style={{
              background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%)',
              backdropFilter: 'blur(20px)'
            }}
          >
            {/* Cercles animés */}
            <div className="relative inline-flex items-center justify-center">
              <div className="absolute w-32 h-32 rounded-full border-4 border-green-500/30 animate-ping" />
              <div className="absolute w-28 h-28 rounded-full border-2 border-green-400/50 animate-pulse" />
              <div className="relative w-24 h-24 rounded-full bg-gradient-to-br from-green-400 to-emerald-600 flex items-center justify-center shadow-lg shadow-green-500/30">
                <span className="text-5xl animate-bounce">✉️</span>
              </div>
            </div>
            
            <h1 className="text-3xl font-bold text-white mt-8 mb-4 animate-[fadeInUp_0.6s_ease-out]">
              Compte créé ! 🎉
            </h1>
            <p className="text-slate-400 mb-8 animate-[fadeInUp_0.6s_ease-out_0.1s_both]">
              Un email de vérification a été envoyé à <br />
              <span className="text-blue-400 font-medium">{formData.email}</span>
            </p>
            
            {/* Progress visual */}
            <div className="flex justify-center gap-2 mb-8">
              {[1, 2, 3].map((step) => (
                <div key={step} className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center text-white font-bold animate-[popIn_0.3s_ease-out_forwards]" style={{ animationDelay: `${step * 0.2}s` }}>
                    ✓
                  </div>
                  {step < 3 && <div className="w-8 h-1 bg-green-500 animate-[growWidth_0.5s_ease-out_forwards]" style={{ animationDelay: `${step * 0.2 + 0.1}s` }} />}
                </div>
              ))}
            </div>

            <Link
              to="/login"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-blue-500 via-purple-500 to-blue-500 bg-[length:200%_100%] animate-[gradientMove_3s_linear_infinite] text-white font-bold shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 hover:scale-[1.02] transition-all"
            >
              Aller à la connexion
              <span className="animate-[bounceRight_1s_infinite]">→</span>
            </Link>
          </div>
        </div>

        <style>{`
          @keyframes confettiFall {
            0% { transform: translateY(0) rotate(0deg); opacity: 1; }
            100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
          }
          @keyframes scaleIn {
            from { transform: scale(0.8); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
          }
          @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
          }
          @keyframes popIn {
            0% { transform: scale(0); }
            70% { transform: scale(1.2); }
            100% { transform: scale(1); }
          }
          @keyframes growWidth {
            from { width: 0; }
            to { width: 32px; }
          }
          @keyframes bounceRight {
            0%, 100% { transform: translateX(0); }
            50% { transform: translateX(5px); }
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

  return (
    <div className="min-h-[calc(100vh-80px)] flex items-center justify-center px-4 py-12 overflow-hidden">
      {/* Arrière-plan dynamique */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {/* Gradient mesh animé */}
        <div 
          className="absolute inset-0 opacity-20"
          style={{
            background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(139, 92, 246, 0.4) 0%, transparent 50%)`
          }}
        />
        
        {/* Orbes flottants */}
        <div className="absolute top-1/3 right-1/5 w-[500px] h-[500px] bg-gradient-to-r from-purple-500/15 to-pink-500/15 rounded-full blur-3xl animate-[float_12s_ease-in-out_infinite]" />
        <div className="absolute bottom-1/3 left-1/5 w-[400px] h-[400px] bg-gradient-to-r from-blue-500/15 to-cyan-500/15 rounded-full blur-3xl animate-[float_15s_ease-in-out_infinite_reverse]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-full blur-3xl animate-[pulse_4s_ease-in-out_infinite]" />
        
        {/* Particules */}
        {PARTICLES.map((particle) => (
          <div
            key={particle.id}
            className={`absolute rounded-full bg-gradient-to-t ${particle.color} to-white/50 animate-[floatUp_linear_infinite]`}
            style={{
              left: `${particle.x}%`,
              bottom: '-5%',
              width: `${particle.size}px`,
              height: `${particle.size}px`,
              animationDuration: `${particle.duration}s`,
              animationDelay: `${particle.delay}s`
            }}
          />
        ))}
        
        {/* Grille néon */}
        <div className="absolute inset-0 opacity-[0.03]">
          <div className="h-full w-full" style={{
            backgroundImage: `
              linear-gradient(rgba(139, 92, 246, 0.5) 1px, transparent 1px),
              linear-gradient(90deg, rgba(139, 92, 246, 0.5) 1px, transparent 1px)
            `,
            backgroundSize: '60px 60px'
          }} />
        </div>
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Card */}
        <div 
          className="relative rounded-3xl p-8 md:p-10 border border-slate-700/50 shadow-2xl transition-all duration-500"
          style={{
            background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%)',
            backdropFilter: 'blur(20px)'
          }}
        >
          {/* Bordure animée */}
          <div className="absolute -inset-[1px] rounded-3xl bg-gradient-to-r from-purple-500 via-pink-500 to-blue-500 opacity-30 blur-sm animate-[spin_8s_linear_infinite]" style={{ zIndex: -1 }} />
          
          {/* Header */}
          <div className="text-center mb-8">
            {/* Logo animé avec orbite */}
            <div className="relative inline-flex items-center justify-center mb-6">
              {/* Orbite */}
              <div className="absolute w-24 h-24 rounded-full border border-purple-500/20 animate-spin" style={{ animationDuration: '10s' }}>
                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-purple-500" />
              </div>
              <div className="absolute w-28 h-28 rounded-full border border-blue-500/20 animate-spin" style={{ animationDuration: '15s', animationDirection: 'reverse' }}>
                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-blue-500" />
              </div>
              
              {/* Logo central */}
              <div className="relative w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center shadow-lg shadow-purple-500/30 transform hover:scale-110 hover:rotate-6 transition-all duration-300">
                <span className="text-4xl">🚀</span>
              </div>
            </div>
            
            {/* Titre avec effet machine à écrire */}
            <h1 className="text-3xl font-bold text-white mb-2 h-10">
              {typingEffect}
              <span className="animate-pulse">|</span>
            </h1>
            <p className="text-slate-400">
              Créez votre compte en quelques étapes
            </p>
            
            {/* Progress Steps */}
            <div className="flex justify-center gap-2 mt-6">
              {[1, 2, 3].map((step) => (
                <div key={step} className="flex items-center">
                  <div 
                    className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all duration-500 ${
                      currentStep >= step 
                        ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white scale-100' 
                        : 'bg-slate-700 text-slate-500 scale-90'
                    } ${currentStep === step ? 'ring-4 ring-purple-500/30 animate-pulse' : ''}`}
                  >
                    {currentStep > step ? '✓' : step}
                  </div>
                  {step < 3 && (
                    <div className={`w-8 h-1 rounded transition-all duration-500 ${currentStep > step ? 'bg-gradient-to-r from-purple-500 to-blue-500' : 'bg-slate-700'}`} />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Error Message */}
          {(error || validationError) && (
            <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm flex items-center gap-3 animate-[shake_0.5s_ease-in-out]">
              <span className="text-xl animate-pulse">⚠️</span>
              <span>{error || validationError}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Step 1: Username & Email */}
            <div className={`space-y-5 transition-all duration-500 ${currentStep === 1 ? 'opacity-100 translate-x-0' : 'opacity-0 absolute -translate-x-full'}`}>
              {currentStep === 1 && (
                <>
                  {/* Username */}
                  <div className={`transform transition-all duration-300 ${focusedField === 'username' ? 'scale-[1.02]' : ''}`}>
                    <label className={`block text-sm font-medium mb-2 transition-colors ${focusedField === 'username' ? 'text-purple-400' : 'text-slate-300'}`}>
                      Nom d'utilisateur
                    </label>
                    <div className="relative group">
                      <div className={`absolute -inset-1 rounded-xl bg-gradient-to-r from-purple-500 to-blue-500 opacity-0 blur transition-all duration-300 ${focusedField === 'username' ? 'opacity-30' : 'group-hover:opacity-20'}`} />
                      <div className="relative flex items-center">
                        <span className={`absolute left-4 transition-all duration-300 ${focusedField === 'username' ? 'text-purple-400 scale-110' : 'text-slate-500'}`}>
                          👤
                        </span>
                        <input
                          type="text"
                          required
                          value={formData.username}
                          onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                          onFocus={() => setFocusedField('username')}
                          onBlur={() => setFocusedField(null)}
                          className="w-full pl-12 pr-12 py-4 rounded-xl bg-slate-800/50 border border-slate-700 text-white placeholder-slate-500 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/30 transition-all outline-none"
                          placeholder="VotrePseudo"
                        />
                        {formData.username.length >= 3 && (
                          <span className="absolute right-4 text-green-400 animate-[popIn_0.3s_ease-out]">✓</span>
                        )}
                      </div>
                    </div>
                    <p className={`text-xs mt-1 transition-colors ${formData.username.length >= 3 ? 'text-green-400' : 'text-slate-500'}`}>
                      {formData.username.length}/3 caractères minimum
                    </p>
                  </div>

                  {/* Email */}
                  <div className={`transform transition-all duration-300 ${focusedField === 'email' ? 'scale-[1.02]' : ''}`}>
                    <label className={`block text-sm font-medium mb-2 transition-colors ${focusedField === 'email' ? 'text-purple-400' : 'text-slate-300'}`}>
                      Email
                    </label>
                    <div className="relative group">
                      <div className={`absolute -inset-1 rounded-xl bg-gradient-to-r from-purple-500 to-blue-500 opacity-0 blur transition-all duration-300 ${focusedField === 'email' ? 'opacity-30' : 'group-hover:opacity-20'}`} />
                      <div className="relative flex items-center">
                        <span className={`absolute left-4 transition-all duration-300 ${focusedField === 'email' ? 'text-purple-400 scale-110' : 'text-slate-500'}`}>
                          📧
                        </span>
                        <input
                          type="email"
                          required
                          value={formData.email}
                          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                          onFocus={() => setFocusedField('email')}
                          onBlur={() => setFocusedField(null)}
                          className="w-full pl-12 pr-12 py-4 rounded-xl bg-slate-800/50 border border-slate-700 text-white placeholder-slate-500 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/30 transition-all outline-none"
                          placeholder="votre@email.com"
                        />
                        {formData.email.includes('@') && formData.email.includes('.') && (
                          <span className="absolute right-4 text-green-400 animate-[popIn_0.3s_ease-out]">✓</span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Next Button */}
                  <button
                    type="button"
                    onClick={() => canProceedToStep2 && setCurrentStep(2)}
                    disabled={!canProceedToStep2}
                    className={`w-full py-4 rounded-xl font-bold text-lg transition-all duration-300 ${
                      canProceedToStep2 
                        ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white hover:shadow-lg hover:shadow-purple-500/30 hover:scale-[1.02]' 
                        : 'bg-slate-700 text-slate-500 cursor-not-allowed'
                    }`}
                  >
                    Continuer →
                  </button>
                </>
              )}
            </div>

            {/* Step 2: Password */}
            <div className={`space-y-5 transition-all duration-500 ${currentStep === 2 ? 'opacity-100 translate-x-0' : currentStep < 2 ? 'opacity-0 translate-x-full' : 'opacity-0 -translate-x-full'}`}>
              {currentStep === 2 && (
                <>
                  {/* Password */}
                  <div className={`transform transition-all duration-300 ${focusedField === 'password' ? 'scale-[1.02]' : ''}`}>
                    <label className={`block text-sm font-medium mb-2 transition-colors ${focusedField === 'password' ? 'text-purple-400' : 'text-slate-300'}`}>
                      Mot de passe
                    </label>
                    <div className="relative group">
                      <div className={`absolute -inset-1 rounded-xl bg-gradient-to-r from-purple-500 to-blue-500 opacity-0 blur transition-all duration-300 ${focusedField === 'password' ? 'opacity-30' : 'group-hover:opacity-20'}`} />
                      <div className="relative">
                        <span className={`absolute left-4 top-1/2 -translate-y-1/2 transition-all duration-300 ${focusedField === 'password' ? 'text-purple-400 scale-110' : 'text-slate-500'}`}>
                          🔒
                        </span>
                        <input
                          type={showPassword ? 'text' : 'password'}
                          required
                          value={formData.password}
                          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                          onFocus={() => setFocusedField('password')}
                          onBlur={() => setFocusedField(null)}
                          className="w-full pl-12 pr-12 py-4 rounded-xl bg-slate-800/50 border border-slate-700 text-white placeholder-slate-500 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/30 transition-all outline-none"
                          placeholder="Minimum 8 caractères"
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
                    
                    {/* Password Strength - Animated bars */}
                    {formData.password && (
                      <div className="mt-4 animate-[fadeInUp_0.3s_ease-out]">
                        <div className="flex gap-1 mb-2">
                          {[...Array(5)].map((_, i) => (
                            <div
                              key={i}
                              className={`h-2 flex-1 rounded-full transition-all duration-500 ${
                                i < passwordStrength ? strengthColors[passwordStrength - 1] : 'bg-slate-700'
                              }`}
                              style={{
                                transform: i < passwordStrength ? 'scaleY(1.2)' : 'scaleY(1)',
                                transitionDelay: `${i * 50}ms`
                              }}
                            />
                          ))}
                        </div>
                        <div className="flex justify-between items-center">
                          <p className={`text-sm font-medium ${passwordStrength >= 4 ? 'text-green-400' : passwordStrength >= 3 ? 'text-yellow-400' : 'text-slate-500'}`}>
                            Force : {strengthLabels[Math.max(0, passwordStrength - 1)] || 'Très faible'}
                          </p>
                          <span className="text-2xl animate-bounce">{strengthEmojis[Math.max(0, passwordStrength - 1)] || '😰'}</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Confirm Password */}
                  <div className={`transform transition-all duration-300 ${focusedField === 'confirm' ? 'scale-[1.02]' : ''}`}>
                    <label className={`block text-sm font-medium mb-2 transition-colors ${focusedField === 'confirm' ? 'text-purple-400' : 'text-slate-300'}`}>
                      Confirmer le mot de passe
                    </label>
                    <div className="relative group">
                      <div className={`absolute -inset-1 rounded-xl bg-gradient-to-r from-purple-500 to-blue-500 opacity-0 blur transition-all duration-300 ${focusedField === 'confirm' ? 'opacity-30' : 'group-hover:opacity-20'}`} />
                      <div className="relative">
                        <span className={`absolute left-4 top-1/2 -translate-y-1/2 transition-all duration-300 ${focusedField === 'confirm' ? 'text-purple-400 scale-110' : 'text-slate-500'}`}>
                          🔐
                        </span>
                        <input
                          type={showPassword ? 'text' : 'password'}
                          required
                          value={formData.confirmPassword}
                          onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                          onFocus={() => setFocusedField('confirm')}
                          onBlur={() => setFocusedField(null)}
                          className={`w-full pl-12 pr-12 py-4 rounded-xl bg-slate-800/50 border text-white placeholder-slate-500 focus:ring-2 transition-all outline-none ${
                            formData.confirmPassword && formData.password !== formData.confirmPassword
                              ? 'border-red-500 focus:border-red-500 focus:ring-red-500/30'
                              : formData.confirmPassword && formData.password === formData.confirmPassword
                              ? 'border-green-500 focus:border-green-500 focus:ring-green-500/30'
                              : 'border-slate-700 focus:border-purple-500 focus:ring-purple-500/30'
                          }`}
                          placeholder="Retapez le mot de passe"
                        />
                        {formData.confirmPassword && (
                          <span className={`absolute right-4 top-1/2 -translate-y-1/2 text-xl animate-[popIn_0.3s_ease-out] ${
                            formData.password === formData.confirmPassword ? 'text-green-400' : 'text-red-400'
                          }`}>
                            {formData.password === formData.confirmPassword ? '✅' : '❌'}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Navigation buttons */}
                  <div className="flex gap-3">
                    <button
                      type="button"
                      onClick={() => setCurrentStep(1)}
                      className="flex-1 py-4 rounded-xl bg-slate-700 text-white font-bold hover:bg-slate-600 transition-all duration-300"
                    >
                      ← Retour
                    </button>
                    <button
                      type="button"
                      onClick={() => canProceedToStep3 && setCurrentStep(3)}
                      disabled={!canProceedToStep3}
                      className={`flex-1 py-4 rounded-xl font-bold transition-all duration-300 ${
                        canProceedToStep3 
                          ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white hover:shadow-lg hover:shadow-purple-500/30 hover:scale-[1.02]' 
                          : 'bg-slate-700 text-slate-500 cursor-not-allowed'
                      }`}
                    >
                      Continuer →
                    </button>
                  </div>
                </>
              )}
            </div>

            {/* Step 3: Confirmation */}
            <div className={`space-y-5 transition-all duration-500 ${currentStep === 3 ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-full'}`}>
              {currentStep === 3 && (
                <>
                  {/* Summary */}
                  <div className="space-y-4 p-6 rounded-xl bg-slate-800/30 border border-slate-700/50">
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      📋 Récapitulatif
                    </h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center py-2 border-b border-slate-700/50">
                        <span className="text-slate-400">Pseudo</span>
                        <span className="text-white font-medium">{formData.username}</span>
                      </div>
                      <div className="flex justify-between items-center py-2 border-b border-slate-700/50">
                        <span className="text-slate-400">Email</span>
                        <span className="text-white font-medium">{formData.email}</span>
                      </div>
                      <div className="flex justify-between items-center py-2">
                        <span className="text-slate-400">Mot de passe</span>
                        <span className="text-green-400 flex items-center gap-1">
                          Sécurisé {strengthEmojis[passwordStrength - 1]}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Terms */}
                  <p className="text-xs text-slate-500 text-center">
                    En créant un compte, vous acceptez nos{' '}
                    <Link to="/terms" className="text-purple-400 hover:underline">
                      Conditions d'utilisation
                    </Link>{' '}
                    et notre{' '}
                    <Link to="/privacy" className="text-purple-400 hover:underline">
                      Politique de confidentialité
                    </Link>
                  </p>

                  {/* Navigation buttons */}
                  <div className="flex gap-3">
                    <button
                      type="button"
                      onClick={() => setCurrentStep(2)}
                      className="flex-1 py-4 rounded-xl bg-slate-700 text-white font-bold hover:bg-slate-600 transition-all duration-300"
                    >
                      ← Retour
                    </button>
                    <button
                      type="submit"
                      disabled={isLoading}
                      className="flex-1 py-4 rounded-xl overflow-hidden font-bold text-white relative transition-all duration-300 disabled:opacity-50"
                    >
                      <div className="absolute inset-0 bg-gradient-to-r from-green-500 via-emerald-500 to-green-500 bg-[length:200%_100%] animate-[gradientMove_3s_linear_infinite]" />
                      <span className="relative flex items-center justify-center gap-2">
                        {isLoading ? (
                          <>
                            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                            </svg>
                            Création...
                          </>
                        ) : (
                          <>
                            Créer mon compte 🎉
                          </>
                        )}
                      </span>
                    </button>
                  </div>
                </>
              )}
            </div>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-4 my-8">
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-slate-600 to-transparent" />
            <span className="text-slate-500 text-sm">ou</span>
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-slate-600 to-transparent" />
          </div>

          {/* Login Link */}
          <p className="text-center text-slate-400">
            Déjà un compte ?{' '}
            <Link 
              to="/login" 
              className="text-purple-400 hover:text-purple-300 font-semibold transition-all duration-300 relative group"
            >
              <span className="relative">
                Se connecter
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-purple-400 group-hover:w-full transition-all duration-300" />
              </span>
            </Link>
          </p>
        </div>

        {/* Features avec animation au hover */}
        <div className="mt-8 grid grid-cols-3 gap-4 text-center">
          {[
            { icon: '🎯', label: 'Pronostics IA', delay: 0 },
            { icon: '📊', label: 'Stats détaillées', delay: 0.1 },
            { icon: '🏆', label: '65%+ réussite', delay: 0.2 }
          ].map((feature, i) => (
            <div 
              key={i}
              className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/30 hover:border-purple-500/50 hover:bg-slate-800/50 transition-all duration-300 hover:scale-105 hover:-translate-y-1 cursor-default group animate-[fadeInUp_0.5s_ease-out_both]"
              style={{ animationDelay: `${feature.delay}s` }}
            >
              <span className="text-3xl group-hover:scale-110 inline-block transition-transform duration-300">{feature.icon}</span>
              <p className="text-xs text-slate-500 mt-2 group-hover:text-slate-400 transition-colors">{feature.label}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Styles */}
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0) translateX(0) rotate(0deg); }
          25% { transform: translateY(-30px) translateX(15px) rotate(5deg); }
          50% { transform: translateY(-15px) translateX(-15px) rotate(-5deg); }
          75% { transform: translateY(-40px) translateX(10px) rotate(3deg); }
        }
        
        @keyframes floatUp {
          0% { transform: translateY(0); opacity: 0; }
          10% { opacity: 0.8; }
          90% { opacity: 0.8; }
          100% { transform: translateY(-100vh); opacity: 0; }
        }
        
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          20% { transform: translateX(-8px); }
          40% { transform: translateX(8px); }
          60% { transform: translateX(-5px); }
          80% { transform: translateX(5px); }
        }
        
        @keyframes popIn {
          0% { transform: scale(0) rotate(-20deg); opacity: 0; }
          70% { transform: scale(1.2) rotate(5deg); }
          100% { transform: scale(1) rotate(0deg); opacity: 1; }
        }
        
        @keyframes gradientMove {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        
        @keyframes pulse {
          0%, 100% { opacity: 0.3; transform: scale(1); }
          50% { opacity: 0.5; transform: scale(1.1); }
        }
        
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
