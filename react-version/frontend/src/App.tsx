import { Layout } from './components/Layout'
import { LongoMatchPage } from './pages/LongoMatchPage'
import { YouTubePage } from './pages/YouTubePage'
import { LoginPage } from './pages/LoginPage'
import { BrowserRouter, Routes, Route, useNavigate, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import { GoogleOAuthProvider } from '@react-oauth/google'

const Dashboard = () => {
    const navigate = useNavigate()

    return (
        <div className="animate-in fade-in duration-500">
            <header className="mb-12">
                <h1 className="text-4xl font-bold mb-2">Bienvenido de nuevo</h1>
                <p className="text-gray-400 text-lg">Selecciona una herramienta para comenzar a trabajar.</p>
            </header>

            <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div
                    onClick={() => navigate('/youtube')}
                    className="bg-[#161618] p-8 rounded-3xl border border-white/5 hover:border-blue-500/50 transition-all duration-300 cursor-pointer group flex flex-col h-full active:scale-[0.98]"
                >
                    <div className="w-12 h-12 bg-blue-500/10 rounded-2xl flex items-center justify-center mb-6 border border-blue-500/20 group-hover:bg-blue-500/20 duration-300">
                        <span className="text-2xl">🎬</span>
                    </div>
                    <h2 className="text-xl font-bold mb-2 group-hover:text-blue-400 transition-colors">YouTube Tools</h2>
                    <p className="text-gray-500 text-sm mb-6 flex-1">Extrae URLs, descarga playlists y gestiona tu base de datos de videos.</p>
                    <button className="w-full py-3 bg-[#232326] rounded-xl font-semibold text-sm hover:bg-blue-600 transition-all duration-300 border border-white/5">
                        Explorar
                    </button>
                </div>

                <div
                    onClick={() => navigate('/longomatch')}
                    className="bg-[#161618] p-8 rounded-3xl border border-white/5 hover:border-emerald-500/50 transition-all duration-300 cursor-pointer group flex flex-col h-full active:scale-[0.98]"
                >
                    <div className="w-12 h-12 bg-emerald-500/10 rounded-2xl flex items-center justify-center mb-6 border border-emerald-500/20 group-hover:bg-emerald-500/20 duration-300">
                        <span className="text-2xl">📈</span>
                    </div>
                    <h2 className="text-xl font-bold mb-2 group-hover:text-emerald-400 transition-colors">LongoMatch Converter</h2>
                    <p className="text-gray-500 text-sm mb-6 flex-1">Convierte tus archivos XML de LongoMatch a formatos CSV y JSON automáticamente.</p>
                    <button className="w-full py-3 bg-[#232326] rounded-xl font-semibold text-sm hover:bg-emerald-600 transition-all duration-300 border border-white/5">
                        Abrir Conversor
                    </button>
                </div>
            </section>
        </div>
    )
}

function App() {
    const { token, user } = useAuthStore()
    console.log('App Rendering - Auth State:', { token: !!token, user: !!user })

    const GOOGLE_CLIENT_ID ="477019567977-o1has81c30dh5k3q9f4fdlqcu8idc8a8.apps.googleusercontent.com";

    if (!token) {
        console.log('No token found, showing LoginPage')
        return (
            <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
                <LoginPage />
            </GoogleOAuthProvider>
        )
    }

    return (
        <BrowserRouter>
            <Layout>
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/longomatch" element={<LongoMatchPage />} />
                    <Route path="/youtube" element={<YouTubePage />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </Layout>
        </BrowserRouter>
    )
}

export default App
