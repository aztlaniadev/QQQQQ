import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate, useParams } from 'react-router-dom';
import axios from 'axios';

// UI Components (assumed to be available)
const Button = ({ children, className = '', variant = 'default', size = 'default', disabled = false, onClick, type = 'button' }) => (
  <button 
    type={type}
    className={`px-4 py-2 rounded font-medium ${className} ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
    onClick={onClick}
    disabled={disabled}
  >
    {children}
  </button>
);

const Card = ({ children, className = '' }) => (
  <div className={`rounded-lg border shadow-sm ${className}`}>
    {children}
  </div>
);

const CardHeader = ({ children }) => <div className="flex flex-col space-y-1.5 p-6">{children}</div>;
const CardTitle = ({ children, className = '' }) => <h3 className={`text-2xl font-semibold leading-none tracking-tight ${className}`}>{children}</h3>;
const CardContent = ({ children, className = '' }) => <div className={`p-6 pt-0 ${className}`}>{children}</div>;

const Input = ({ className = '', ...props }) => (
  <input className={`flex h-10 w-full rounded-md border px-3 py-2 text-sm ${className}`} {...props} />
);

const Label = ({ children, className = '', htmlFor }) => (
  <label htmlFor={htmlFor} className={`text-sm font-medium leading-none ${className}`}>{children}</label>
);

const Textarea = ({ className = '', ...props }) => (
  <textarea className={`flex min-h-[80px] w-full rounded-md border px-3 py-2 text-sm ${className}`} {...props} />
);

// Icons (simplified)
const MessageSquare = ({ className }) => <div className={`w-6 h-6 ${className}`}>💬</div>;
const Trophy = ({ className }) => <div className={`w-6 h-6 ${className}`}>🏆</div>;
const Users = ({ className }) => <div className={`w-6 h-6 ${className}`}>👥</div>;
const Settings = ({ className }) => <div className={`w-6 h-6 ${className}`}>⚙️</div>;
const Crown = ({ className }) => <div className={`w-6 h-6 ${className}`}>👑</div>;
const LogOut = ({ className }) => <div className={`w-6 h-6 ${className}`}>🚪</div>;
const Check = ({ className }) => <div className={`w-6 h-6 ${className}`}>✅</div>;
const Building = ({ className }) => <div className={`w-6 h-6 ${className}`}>🏢</div>;
const BookOpen = ({ className }) => <div className={`w-6 h-6 ${className}`}>📖</div>;
const ShoppingCart = ({ className }) => <div className={`w-6 h-6 ${className}`}>🛒</div>;
const Briefcase = ({ className }) => <div className={`w-6 h-6 ${className}`}>💼</div>;
const Coins = ({ className }) => <div className={`w-6 h-6 ${className}`}>🪙</div>;
const Award = ({ className }) => <div className={`w-6 h-6 ${className}`}>🏅</div>;
const Star = ({ className }) => <div className={`w-6 h-6 ${className}`}>⭐</div>;

// 🔥🔥🔥 NUCLEAR OPTION - HARDCODED URL 🔥🔥🔥
const API = 'http://localhost:8030/api';

// 🚨 AGGRESSIVE DEBUGGING - LINHA 13 🚨
console.error('🔥🔥🔥 NUCLEAR DEBUG - APP.JS LINHA 13 🔥🔥🔥');
console.error('🔥 API URL HARDCODED:', API);
console.error('🔥 CONTAINS 8050?', API.includes('8050'));
console.error('🔥 CONTAINS 8001?', API.includes('8001'));
console.error('🔥 TIMESTAMP:', new Date().toISOString());
console.error('🔥 LOCATION:', window.location.href);

// 🚨 IMMEDIATE ALERT IF WRONG 🚨
if (API.includes('8050') || API.includes('8001')) {
  console.error('💥💥💥 WRONG PORT ERROR: API contains wrong port!');
  console.error('💥 API should be 8030, but is:', API);
  alert('💥 WRONG PORT ERROR: API=' + API + ' (should be 8030)');
  debugger; // Force break in debugger
  throw new Error('💥 API URL ERROR: ' + API);
} else {
  console.error('✅ SUCCESS: API is 8030');
}

// 🔥 OVERRIDE AXIOS DEFAULTS 🔥
axios.defaults.baseURL = 'http://localhost:8030/api';
console.error('🔥 AXIOS BASE URL SET TO:', axios.defaults.baseURL);

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      verifyToken(token);
    } else {
      setLoading(false);
    }
  }, []);

  const verifyToken = async (token) => {
    try {
      const response = await axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const response = await axios.post(`${API}/auth/login`, { email, password });
    localStorage.setItem('token', response.data.access_token);
    setUser(response.data.user);
    return response.data;
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Error Boundary
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-black flex items-center justify-center">
          <div className="text-center text-white">
            <h1 className="text-2xl font-bold mb-4">Algo deu errado!</h1>
            <p className="text-gray-400 mb-6">Recarregue a página para tentar novamente.</p>
            <Button onClick={() => window.location.reload()} className="bg-copper hover:bg-copper/90 text-black">
              Recarregar
            </Button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Navigation Component
const Navigation = () => {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-gray-900 border-b border-copper/20 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="text-2xl font-bold text-copper">
            Acode Lab
          </Link>
          
          <div className="hidden md:flex space-x-6">
            <Link to="/perguntas" className="text-gray-300 hover:text-copper transition-colors">
              Perguntas
            </Link>
            <Link to="/artigos" className="text-gray-300 hover:text-copper transition-colors">
              Artigos
            </Link>
            <Link to="/connect" className="text-gray-300 hover:text-copper transition-colors">
              Connect
            </Link>
            <Link to="/loja" className="text-gray-300 hover:text-copper transition-colors">
              Loja
            </Link>
            <Link to="/vagas" className="text-gray-300 hover:text-copper transition-colors">
              Vagas
            </Link>
          </div>

          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <Link to="/dashboard" className="text-gray-300 hover:text-copper transition-colors">
                  Dashboard
                </Link>
                <Link to="/perfil" className="text-gray-300 hover:text-copper transition-colors">
                  <Settings className="h-5 w-5" />
                </Link>
                {user.is_admin && (
                  <Link to="/admin" className="text-yellow-400 hover:text-yellow-300 transition-colors">
                    <Crown className="h-5 w-5" />
                  </Link>
                )}
                <Button
                  onClick={logout}
                  variant="outline"
                  size="sm"
                  className="border-copper/20 text-gray-300"
                >
                  <LogOut className="h-4 w-4" />
                </Button>
              </>
            ) : (
              <div className="space-x-2">
                <Link to="/login">
                  <Button variant="outline" size="sm" className="border-copper/20 text-gray-300">
                    Login
                  </Button>
                </Link>
                <Link to="/registro">
                  <Button size="sm" className="bg-copper hover:bg-copper/90 text-black">
                    Registrar
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

// Homepage Component
const Homepage = () => {
  return (
    <div className="min-h-screen bg-black">
      <Navigation />
      <div className="max-w-6xl mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-white mb-6">
            Bem-vindo ao <span className="text-copper">Acode Lab</span>
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            A plataforma global para desenvolvedores: resolva problemas técnicos, 
            desenvolva sua carreira e conecte-se com profissionais do mundo todo.
          </p>
          <div className="flex gap-4 justify-center">
            <Link to="/perguntas">
              <Button size="lg" className="bg-copper hover:bg-copper/90 text-black">
                Explorar Perguntas
              </Button>
            </Link>
            <Link to="/registro">
              <Button size="lg" variant="outline" className="border-copper text-copper hover:bg-copper/10">
                Criar Conta
              </Button>
            </Link>
          </div>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <Card className="bg-gray-900 border-copper/20">
            <CardContent className="p-6 text-center">
              <MessageSquare className="h-12 w-12 text-copper mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Q&A System</h3>
              <p className="text-gray-400">Faça perguntas técnicas e receba respostas de especialistas</p>
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-copper/20">
            <CardContent className="p-6 text-center">
              <Trophy className="h-12 w-12 text-copper mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Gamificação</h3>
              <p className="text-gray-400">Ganhe pontos PC e PCon, suba de rank e desbloqueie conquistas</p>
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-copper/20">
            <CardContent className="p-6 text-center">
              <Users className="h-12 w-12 text-copper mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Networking</h3>
              <p className="text-gray-400">Conecte-se com outros desenvolvedores e empresas</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

// Login Component  
const Login = () => {
  const { login } = useAuth();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      await login(formData.email, formData.password);
      window.location.href = '/dashboard';
    } catch (error) {
      setError('Email ou senha incorretos');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black">
      <Navigation />
      <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <Card className="w-full max-w-md bg-gray-900 border-copper/20">
          <CardHeader>
            <CardTitle className="text-2xl text-center text-white">Login</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="email" className="text-gray-300">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="bg-gray-800 border-gray-700 text-white"
                  required
                />
              </div>
              <div>
                <Label htmlFor="password" className="text-gray-300">Senha</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="bg-gray-800 border-gray-700 text-white"
                  required
                />
              </div>
              {error && (
                <div className="text-red-400 text-sm text-center">{error}</div>
              )}
              <Button
                type="submit"
                className="w-full bg-copper hover:bg-copper/90 text-black"
                disabled={loading}
              >
                {loading ? 'Entrando...' : 'Entrar'}
              </Button>
            </form>
            <div className="mt-4 text-center">
              <Link to="/registro" className="text-copper hover:underline">
                Não tem conta? Registre-se
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Register Component
const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    if (formData.password !== formData.confirmPassword) {
      setError('Senhas não coincidem');
      setLoading(false);
      return;
    }

    try {
      await axios.post(`${API}/auth/register`, {
        username: formData.username,
        email: formData.email,
        password: formData.password
      });
      
      setSuccess(true);
    } catch (error) {
      setError(error.response?.data?.detail || 'Erro ao criar conta');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-black">
        <Navigation />
        <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
          <Card className="w-full max-w-md bg-gray-900 border-green-500/20">
            <CardContent className="p-8 text-center">
              <Check className="h-12 w-12 text-green-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Conta criada!</h3>
              <p className="text-gray-400 mb-4">Sua conta foi criada com sucesso.</p>
              <Link to="/login">
                <Button className="bg-copper hover:bg-copper/90 text-black">
                  Fazer Login
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black">
      <Navigation />
      <div className="flex items-center justify-center min-h-[calc(100vh-4rem)]">
        <Card className="w-full max-w-md bg-gray-900 border-copper/20">
          <CardHeader>
            <CardTitle className="text-2xl text-center text-white">Criar Conta</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="username" className="text-gray-300">Nome de usuário</Label>
                <Input
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  className="bg-gray-800 border-gray-700 text-white"
                  required
                />
              </div>
              <div>
                <Label htmlFor="email" className="text-gray-300">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="bg-gray-800 border-gray-700 text-white"
                  required
                />
              </div>
              <div>
                <Label htmlFor="password" className="text-gray-300">Senha</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="bg-gray-800 border-gray-700 text-white"
                  required
                />
              </div>
              <div>
                <Label htmlFor="confirmPassword" className="text-gray-300">Confirmar Senha</Label>
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
                  className="bg-gray-800 border-gray-700 text-white"
                  required
                />
              </div>
              {error && (
                <div className="text-red-400 text-sm text-center">{error}</div>
              )}
              <Button
                type="submit"
                className="w-full bg-copper hover:bg-copper/90 text-black"
                disabled={loading}
              >
                {loading ? 'Criando...' : 'Criar Conta'}
              </Button>
            </form>
            <div className="mt-4 text-center">
              <Link to="/login" className="text-copper hover:underline">
                Já tem conta? Faça login
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Profile Settings Component
const ProfileSettings = () => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    bio: user?.bio || '',
    location: user?.location || '',
    website: user?.website || '',
    github: user?.github || '',
    linkedin: user?.linkedin || '',
    skills: user?.skills?.join(', ') || '',
    theme_color: user?.theme_color || '#D97745',
    custom_title: user?.custom_title || '',
    banner_image: user?.banner_image || ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    
    try {
      const token = localStorage.getItem('token');
      const updateData = {
        ...formData,
        skills: formData.skills.split(',').map(s => s.trim()).filter(s => s)
      };
      
      await axios.put(`${API}/users/profile`, updateData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setMessage('Perfil atualizado com sucesso!');
      setTimeout(() => window.location.reload(), 1500);
    } catch (error) {
      setMessage('Erro ao atualizar perfil: ' + (error.response?.data?.detail || 'Erro desconhecido'));
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-black">
      <Navigation />
      <div className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-white mb-8">Configurações do Perfil</h1>
        
        <Card className="bg-gray-900 border-copper/20">
          <CardHeader>
            <CardTitle className="text-white">Personalizar Perfil</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="username" className="text-gray-300">Nome de usuário</Label>
                  <Input
                    id="username"
                    name="username"
                    value={formData.username}
                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                    className="bg-gray-800 border-gray-700 text-white"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="email" className="text-gray-300">Email</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="bg-gray-800 border-gray-700 text-white"
                    required
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="custom_title" className="text-gray-300">Título Personalizado</Label>
                <Input
                  id="custom_title"
                  name="custom_title"
                  value={formData.custom_title}
                  onChange={(e) => setFormData({...formData, custom_title: e.target.value})}
                  className="bg-gray-800 border-gray-700 text-white"
                  placeholder="Ex: Desenvolvedor Full Stack"
                />
              </div>
              
              <div>
                <Label htmlFor="theme_color" className="text-gray-300">Cor do Tema</Label>
                <div className="flex gap-2 items-center">
                  <Input
                    id="theme_color"
                    name="theme_color"
                    type="color"
                    value={formData.theme_color}
                    onChange={(e) => setFormData({...formData, theme_color: e.target.value})}
                    className="w-20 h-10 bg-gray-800 border-gray-700"
                  />
                  <Input
                    name="theme_color"
                    value={formData.theme_color}
                    onChange={(e) => setFormData({...formData, theme_color: e.target.value})}
                    className="flex-1 bg-gray-800 border-gray-700 text-white"
                    placeholder="#D97745"
                  />
                </div>
              </div>
              
              <div>
                <Label htmlFor="bio" className="text-gray-300">Bio</Label>
                <Textarea
                  id="bio"
                  name="bio"
                  value={formData.bio}
                  onChange={(e) => setFormData({...formData, bio: e.target.value})}
                  className="bg-gray-800 border-gray-700 text-white"
                  placeholder="Conte sobre você..."
                  rows={3}
                />
              </div>
              
              <div>
                <Label htmlFor="skills" className="text-gray-300">Habilidades (separadas por vírgula)</Label>
                <Input
                  id="skills"
                  name="skills"
                  value={formData.skills}
                  onChange={(e) => setFormData({...formData, skills: e.target.value})}
                  className="bg-gray-800 border-gray-700 text-white"
                  placeholder="JavaScript, Python, React"
                />
              </div>
              
              {message && (
                <div className={`text-sm text-center ${message.includes('sucesso') ? 'text-green-400' : 'text-red-400'}`}>
                  {message}
                </div>
              )}
              
              <Button
                type="submit"
                className="w-full bg-copper hover:bg-copper/90 text-black"
                disabled={loading}
              >
                {loading ? 'Salvando...' : 'Salvar Configurações'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Placeholder components (simplified for now)
const CompanyRegister = () => (
  <div className="min-h-screen bg-black">
    <Navigation />
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-white mb-8">Registro de Empresa</h1>
      <Card className="bg-gray-900 border-copper/20">
        <CardContent className="p-8 text-center">
          <Building className="h-12 w-12 text-copper mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">Em Desenvolvimento</h3>
          <p className="text-gray-400">Registro de empresas em breve...</p>
        </CardContent>
      </Card>
    </div>
  </div>
);

const QuestionsList = () => (
  <div className="min-h-screen bg-black">
    <Navigation />
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-white mb-8">Perguntas</h1>
      <Card className="bg-gray-900 border-copper/20">
        <CardContent className="p-8 text-center">
          <MessageSquare className="h-12 w-12 text-copper mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">Sistema de Perguntas</h3>
          <p className="text-gray-400">Sistema completo em desenvolvimento...</p>
        </CardContent>
      </Card>
    </div>
  </div>
);

const QuestionDetail = () => (
  <div className="min-h-screen bg-black">
    <Navigation />
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-white mb-8">Detalhes da Pergunta</h1>
      <Card className="bg-gray-900 border-copper/20">
        <CardContent className="p-8 text-center">
          <MessageSquare className="h-12 w-12 text-copper mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">Pergunta Individual</h3>
          <p className="text-gray-400">Página de pergunta em desenvolvimento...</p>
        </CardContent>
      </Card>
    </div>
  </div>
);

const ArticlesList = () => (
  <div className="min-h-screen bg-black">
    <Navigation />
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-white mb-8">Artigos</h1>
      <Card className="bg-gray-900 border-copper/20">
        <CardContent className="p-8 text-center">
          <BookOpen className="h-12 w-12 text-copper mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">Sistema de Artigos</h3>
          <p className="text-gray-400">Apenas usuários Mestre e Guru podem escrever artigos...</p>
        </CardContent>
      </Card>
    </div>
  </div>
);

const Connect = () => (
  <div className="min-h-screen bg-black">
    <Navigation />
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-white mb-8">Acode Lab: Connect</h1>
      <Card className="bg-gray-900 border-copper/20">
        <CardContent className="p-8 text-center">
          <Users className="h-12 w-12 text-copper mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">Rede Social</h3>
          <p className="text-gray-400">Conecte-se com outros desenvolvedores...</p>
        </CardContent>
      </Card>
    </div>
  </div>
);

const Store = () => (
  <div className="min-h-screen bg-black">
    <Navigation />
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-white mb-8">Loja PCon</h1>
      <Card className="bg-gray-900 border-copper/20">
        <CardContent className="p-8 text-center">
          <ShoppingCart className="h-12 w-12 text-copper mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">Loja de Vantagens</h3>
          <p className="text-gray-400">Use seus PCon para comprar vantagens...</p>
        </CardContent>
      </Card>
    </div>
  </div>
);

const Jobs = () => (
  <div className="min-h-screen bg-black">
    <Navigation />
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-white mb-8">Vagas</h1>
      <Card className="bg-gray-900 border-copper/20">
        <CardContent className="p-8 text-center">
          <Briefcase className="h-12 w-12 text-copper mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">Portal de Vagas</h3>
          <p className="text-gray-400">Encontre oportunidades de trabalho...</p>
        </CardContent>
      </Card>
    </div>
  </div>
);

const Dashboard = () => {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-black">
      <Navigation />
      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-white mb-8">Dashboard</h1>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gray-900 border-copper/20">
            <CardContent className="p-6 text-center">
              <Trophy className="h-8 w-8 text-copper mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">{user.pc_points || 0}</div>
              <div className="text-sm text-gray-400">PC Points</div>
            </CardContent>
          </Card>
          
          <Card className="bg-gray-900 border-copper/20">
            <CardContent className="p-6 text-center">
              <Coins className="h-8 w-8 text-amber-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">{user.pcon_points || 0}</div>
              <div className="text-sm text-gray-400">PCon Points</div>
            </CardContent>
          </Card>
          
          <Card className="bg-gray-900 border-copper/20">
            <CardContent className="p-6 text-center">
              <Award className="h-8 w-8 text-purple-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">{user.rank || 'Iniciante'}</div>
              <div className="text-sm text-gray-400">Rank</div>
            </CardContent>
          </Card>
          
          <Card className="bg-gray-900 border-copper/20">
            <CardContent className="p-6 text-center">
              <Star className="h-8 w-8 text-yellow-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">{user.achievements?.length || 0}</div>
              <div className="text-sm text-gray-400">Conquistas</div>
            </CardContent>
          </Card>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <Card className="bg-gray-900 border-copper/20">
            <CardHeader>
              <CardTitle className="text-white">Perfil</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <p className="text-gray-300"><strong>Nome:</strong> {user.username}</p>
                <p className="text-gray-300"><strong>Email:</strong> {user.email}</p>
                <p className="text-gray-300"><strong>Localização:</strong> {user.location || 'Não informado'}</p>
                <p className="text-gray-300"><strong>Bio:</strong> {user.bio || 'Nenhuma bio ainda'}</p>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-copper/20">
            <CardHeader>
              <CardTitle className="text-white">Ações Rápidas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Link to="/perguntas" className="block">
                <Button className="w-full bg-copper hover:bg-copper/90 text-black">
                  <MessageSquare className="h-4 w-4 mr-2" />
                  Fazer Pergunta
                </Button>
              </Link>
              <Link to="/loja" className="block">
                <Button variant="outline" className="w-full border-copper/20 text-gray-300">
                  <ShoppingCart className="h-4 w-4 mr-2" />
                  Loja PCon
                </Button>
              </Link>
              <Link to="/connect" className="block">
                <Button variant="outline" className="w-full border-copper/20 text-gray-300">
                  <Users className="h-4 w-4 mr-2" />
                  Connect
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

const AdminPanel = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [botFormData, setBotFormData] = useState({
    username: '',
    email: '',
    bio: '',
    pc_points: 0,
    pcon_points: 0,
    rank: 'Iniciante',
    location: '',
    skills: []
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  if (!user || !user.is_admin) {
    return <Navigate to="/login" replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    
    try {
      console.error('🔥🔥🔥 WINDOWS DEBUG - ADMIN BOT SUBMIT 🔥🔥🔥');
      console.error('🔥 API URL:', API);
      console.error('🔥 RAW FORM DATA:', botFormData);
      
      // Clean and validate data
      const cleanData = {
        username: String(botFormData.username).trim(),
        email: String(botFormData.email).trim(),
        bio: String(botFormData.bio || '').trim(),
        pc_points: parseInt(botFormData.pc_points) || 0,
        pcon_points: parseInt(botFormData.pcon_points) || 0,
        rank: String(botFormData.rank || 'Iniciante').trim(),
        location: String(botFormData.location || '').trim(),
        skills: Array.isArray(botFormData.skills) ? botFormData.skills : []
      };
      
      console.error('🔥 CLEANED DATA:', cleanData);
      console.error('🔥 JSON STRINGIFY:', JSON.stringify(cleanData));
      
      const token = localStorage.getItem('token');
      console.error('🔥 TOKEN:', token ? 'EXISTS' : 'MISSING');
      
      const fullUrl = `${API}/admin/bots/`;
      console.error('🔥 FULL URL:', fullUrl);
      
      const headers = { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      };
      console.error('🔥 HEADERS:', headers);
      
      console.error('🔥 MAKING REQUEST...');
      const response = await axios.post(fullUrl, cleanData, { headers });
      
      console.error('🔥 SUCCESS RESPONSE:', response);
      console.error('🔥 SUCCESS DATA:', response.data);
      setMessage('Bot criado com sucesso!');
      setBotFormData({
        username: '',
        email: '',
        bio: '',
        pc_points: 0,
        pcon_points: 0,
        rank: 'Iniciante',
        location: '',
        skills: []
      });
    } catch (error) {
      console.error('🔥 ERROR OBJECT:', error);
      console.error('🔥 ERROR MESSAGE:', error.message);
      console.error('🔥 ERROR RESPONSE:', error.response);
      console.error('🔥 ERROR DATA:', error.response?.data);
      console.error('🔥 ERROR STATUS:', error.response?.status);
      console.error('🔥 ERROR HEADERS:', error.response?.headers);
      
      let errorMsg = 'Erro desconhecido';
      if (error.response?.data?.detail) {
        errorMsg = error.response.data.detail;
      } else if (error.response?.data?.message) {
        errorMsg = error.response.data.message;
      } else if (error.message) {
        errorMsg = error.message;
      }
      
      setMessage('Erro ao criar bot: ' + errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black">
      <Navigation />
      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-white mb-8">Painel de Administração</h1>
        
        <div className="mb-6">
          <div className="flex space-x-1 bg-gray-800 p-1 rounded-lg">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'dashboard' 
                  ? 'bg-copper text-black' 
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setActiveTab('bots')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'bots'
                  ? 'bg-copper text-black'
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              Gerenciar Bots
            </button>
          </div>
        </div>

        {activeTab === 'dashboard' && (
          <Card className="bg-gray-900 border-copper/20">
            <CardContent className="p-8 text-center">
              <Crown className="h-12 w-12 text-copper mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">Admin Dashboard</h3>
              <p className="text-gray-400">Estatísticas e visão geral do sistema...</p>
            </CardContent>
          </Card>
        )}

        {activeTab === 'bots' && (
          <Card className="bg-gray-900 border-copper/20">
            <CardHeader>
              <CardTitle className="text-white">Criar Novo Bot</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="username" className="block text-sm font-medium text-gray-300 mb-1">
                      Nome de usuário
                    </label>
                    <input
                      type="text"
                      id="username"
                      value={botFormData.username}
                      onChange={(e) => setBotFormData({...botFormData, username: e.target.value})}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-white"
                      required
                    />
                  </div>
                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-1">
                      Email
                    </label>
                    <input
                      type="email"
                      id="email"
                      value={botFormData.email}
                      onChange={(e) => setBotFormData({...botFormData, email: e.target.value})}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-white"
                      required
                    />
                  </div>
                </div>
                
                <div>
                  <label htmlFor="bio" className="block text-sm font-medium text-gray-300 mb-1">
                    Bio
                  </label>
                  <textarea
                    id="bio"
                    value={botFormData.bio}
                    onChange={(e) => setBotFormData({...botFormData, bio: e.target.value})}
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-white"
                    rows={3}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="pc_points" className="block text-sm font-medium text-gray-300 mb-1">
                      PC Points
                    </label>
                    <input
                      type="number"
                      id="pc_points"
                      value={botFormData.pc_points}
                      onChange={(e) => setBotFormData({...botFormData, pc_points: parseInt(e.target.value) || 0})}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-white"
                    />
                  </div>
                  <div>
                    <label htmlFor="pcon_points" className="block text-sm font-medium text-gray-300 mb-1">
                      PCon Points
                    </label>
                    <input
                      type="number"
                      id="pcon_points"
                      value={botFormData.pcon_points}
                      onChange={(e) => setBotFormData({...botFormData, pcon_points: parseInt(e.target.value) || 0})}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-white"
                    />
                  </div>
                </div>

                {message && (
                  <div className={`text-sm text-center p-2 rounded ${
                    message.includes('sucesso') ? 'text-green-400 bg-green-900/20' : 'text-red-400 bg-red-900/20'
                  }`}>
                    {message}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-copper hover:bg-copper/90 text-black font-medium py-2 px-4 rounded-md disabled:opacity-50"
                >
                  {loading ? 'Criando Bot...' : 'Criar Bot'}
                </button>
              </form>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <Router>
      <AuthProvider>
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<Homepage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/registro" element={<Register />} />
            <Route path="/registro-empresa" element={<CompanyRegister />} />
            <Route path="/perguntas" element={<QuestionsList />} />
            <Route path="/perguntas/:id" element={<QuestionDetail />} />
            <Route path="/artigos" element={<ArticlesList />} />
            <Route path="/connect" element={<Connect />} />
            <Route path="/loja" element={<Store />} />
            <Route path="/vagas" element={<Jobs />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/admin" element={<AdminPanel />} />
            <Route path="/perfil" element={<ProfileSettings />} />
          </Routes>
        </ErrorBoundary>
      </AuthProvider>
    </Router>
  );
}

export default App;