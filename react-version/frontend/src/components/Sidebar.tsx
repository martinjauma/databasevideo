import { Home, Youtube, FileCode, Settings, LogOut, Zap } from 'lucide-react'
import { useAuthStore } from '../store/authStore'

const navItems = [
    { name: 'Inicio', icon: Home, path: '/' },
    { name: 'YouTube', icon: Youtube, path: '/youtube' },
    { name: 'LongoMatch', icon: FileCode, path: '/longomatch' },
    { name: 'Ajustes', icon: Settings, path: '/settings' },
]

export const Sidebar = () => {
    const { user, logout } = useAuthStore()

    return (
        <div className="w-64 h-screen bg-[#111113] border-r border-white/5 flex flex-col p-4 fixed left-0 top-0">
            <div className="flex items-center gap-3 px-2 mb-10">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                    <Zap className="text-white w-5 h-5 fill-current" />
                </div>
                <span className="text-xl font-bold tracking-tight">Data App <span className="text-blue-500">v2</span></span>
            </div>

            <nav className="flex-1 space-y-2">
                {navItems.map((item) => (
                    <a
                        key={item.name}
                        href={item.path}
                        className="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5 transition-colors text-gray-400 hover:text-white group"
                    >
                        <item.icon className="w-5 h-5 group-hover:text-blue-400 duration-200" />
                        <span className="font-medium">{item.name}</span>
                    </a>
                ))}
            </nav>

            <div className="mt-auto pt-6 border-t border-white/5">
                {user && (
                    <div className="flex items-center gap-3 px-2 mb-6">
                        <img src={user.picture} alt={user.name} className="w-10 h-10 rounded-full border border-white/10" />
                        <div className="flex flex-col">
                            <span className="text-sm font-semibold truncate w-32">{user.name}</span>
                            <span className="text-[10px] text-gray-500 uppercase tracking-wider font-bold">
                                {user.subscription === 'active' ? '✨ Premium' : 'Free Plan'}
                            </span>
                        </div>
                    </div>
                )}
                <button
                    onClick={logout}
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-red-500/10 text-gray-400 hover:text-red-400 transition-all duration-200"
                >
                    <LogOut className="w-5 h-5" />
                    <span className="font-medium">Cerrar Sesión</span>
                </button>
            </div>
        </div>
    )
}
