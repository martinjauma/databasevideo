import { GoogleLogin } from '@react-oauth/google'
import { useAuthStore } from '../store/authStore'
import axios from 'axios'
import { Zap } from 'lucide-react'

export const LoginPage = () => {
    const setAuth = useAuthStore((state) => state.setAuth)

    const handleSuccess = async (credentialResponse: any) => {
        try {
            const response = await axios.post('/api/auth/verify', {
                token: credentialResponse.credential
            })
            const { user, access_token } = response.data
            setAuth(user, access_token)
        } catch (error) {
            console.error('Login failed', error)
            alert('Error al iniciar sesión. Por favor, intenta de nuevo.')
        }
    }

    return (
        <div className="min-h-screen bg-[#0a0a0b] text-white flex flex-col items-center justify-center p-4">
            <div className="w-full max-w-md bg-[#161618] border border-white/5 p-12 rounded-[40px] shadow-2xl flex flex-col items-center text-center">
                <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mb-8 shadow-lg shadow-blue-500/20">
                    <Zap className="text-white w-10 h-10 fill-current" />
                </div>

                <h1 className="text-3xl font-bold mb-3 tracking-tight">Bienvenido a Data App <span className="text-blue-500">v2</span></h1>
                <p className="text-gray-400 mb-10 text-lg leading-relaxed">
                    Accede a tus herramientas de análisis de video y datos deportivos.
                </p>

                <div className="w-full flex justify-center py-2">
                    <GoogleLogin
                        onSuccess={handleSuccess}
                        onError={() => console.log('Login Failed')}
                        useOneTap
                        theme="filled_blue"
                        shape="pill"
                        size="large"
                        text="signin_with"
                    />
                </div>

                <p className="mt-10 text-xs text-gray-500 max-w-[280px]">
                    Al continuar, aceptas nuestros términos de servicio y política de privacidad.
                </p>
            </div>

            <div className="mt-8 text-gray-600 text-[10px] uppercase tracking-[0.2em] font-bold">
                Powered by Advanced Agentic Coding
            </div>
        </div>
    )
}
