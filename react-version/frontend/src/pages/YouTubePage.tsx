import { useState } from 'react'
import axios from 'axios'
import { Youtube, Link, Download, Loader2, Info } from 'lucide-react'

export const YouTubePage = () => {
    const [url, setUrl] = useState('')
    const [loading, setLoading] = useState(false)
    const [videoInfo, setVideoInfo] = useState<any>(null)

    const handleGetInfo = async () => {
        if (!url) return
        setLoading(true)
        setVideoInfo(null)

        try {
            const response = await axios.post('/api/tools/youtube/info', { url })
            setVideoInfo(response.data)
        } catch (error) {
            console.error('Error fetching video info', error)
            alert('Error al obtener información del video. Verifica la URL.')
        } finally {
            setLoading(false)
        }
    }

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text)
        alert('Copiado al portapapeles')
    }

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <header>
                <h1 className="text-3xl font-bold mb-2">YouTube Video Tools</h1>
                <p className="text-gray-400">Limpia URLs y obtén enlaces de descarga directa sin publicidad ni malware.</p>
            </header>

            <div className="bg-[#161618] border border-white/5 rounded-3xl p-8">
                <div className="flex flex-col md:flex-row gap-4">
                    <div className="flex-1 relative">
                        <Link className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 w-5 h-5" />
                        <input
                            type="text"
                            placeholder="Pega aquí la URL de YouTube..."
                            className="w-full bg-[#0a0a0b] border border-white/5 rounded-2xl py-4 pl-12 pr-4 focus:border-blue-500/50 outline-none transition-all text-white"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                        />
                    </div>
                    <button
                        onClick={handleGetInfo}
                        disabled={loading || !url}
                        className="md:w-48 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-bold py-4 rounded-2xl transition-all flex items-center justify-center gap-2"
                    >
                        {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : (
                            <>
                                <Youtube className="w-5 h-5" />
                                Obtener Info
                            </>
                        )}
                    </button>
                </div>
            </div>

            {videoInfo && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <div className="lg:col-span-2 space-y-6">
                        <div className="bg-[#161618] border border-white/5 rounded-3xl p-1 overflow-hidden">
                            <div className="relative aspect-video rounded-2xl overflow-hidden bg-black">
                                <img
                                    src={videoInfo.thumbnail}
                                    alt={videoInfo.title}
                                    className="w-full h-full object-cover opacity-70"
                                />
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center shadow-2xl">
                                        <Youtube className="w-8 h-8 text-white fill-current" />
                                    </div>
                                </div>
                            </div>
                            <div className="p-8">
                                <h2 className="text-2xl font-bold mb-4">{videoInfo.title}</h2>
                                <div className="flex flex-wrap gap-4 text-sm text-gray-400">
                                    <span className="flex items-center gap-2 bg-white/5 px-3 py-1 rounded-full border border-white/5">
                                        <Info className="w-4 h-4" />
                                        ID: {videoInfo.id}
                                    </span>
                                    <span className="flex items-center gap-2 bg-white/5 px-3 py-1 rounded-full border border-white/5">
                                        Duración: {Math.floor(videoInfo.duration / 60)}:{String(videoInfo.duration % 60).padStart(2, '0')}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="space-y-6">
                        <div className="bg-[#161618] border border-white/5 rounded-3xl p-8 space-y-6">
                            <h3 className="text-xl font-bold flex items-center gap-2">
                                <Download className="w-5 h-5 text-blue-500" />
                                Descargar
                            </h3>

                            <div className="space-y-4">
                                <div>
                                    <label className="text-xs text-gray-500 uppercase font-bold tracking-widest block mb-2">Nombre Sugerido</label>
                                    <div className="flex items-center gap-2 p-3 bg-[#0a0a0b] rounded-xl border border-white/5 group">
                                        <code className="text-sm text-blue-400 truncate flex-1">{videoInfo.title}.mp4</code>
                                        <button
                                            onClick={() => copyToClipboard(`${videoInfo.title}.mp4`)}
                                            className="text-gray-500 hover:text-white transition-colors"
                                        >
                                            <Link className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>

                                <div className="pt-4 space-y-3">
                                    <a
                                        href={`/api/tools/youtube/download?video_id=${encodeURIComponent(videoInfo.id)}&title=${encodeURIComponent(videoInfo.title)}`}
                                        className="w-full py-4 bg-white text-black rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-gray-200 transition-all active:scale-95"
                                    >
                                        <Download className="w-5 h-5" />
                                        Descargar Video
                                    </a>
                                    <p className="text-[10px] text-gray-500 text-center uppercase tracking-wider font-bold">
                                        La descarga puede tardar unos segundos mientras se procesa el video
                                    </p>
                                </div>
                            </div>

                            <div className="bg-blue-500/5 border border-blue-500/10 rounded-2xl p-4 flex gap-3">
                                <Info className="w-5 h-5 text-blue-400 shrink-0" />
                                <p className="text-xs text-blue-400/80 leading-relaxed">
                                    Para guardar el video con el nombre sugerido, haz clic derecho en el botón de descarga y selecciona "Guardar enlace como...".
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {!videoInfo && !loading && (
                <div className="flex flex-col items-center justify-center py-20 text-center opacity-30 select-none">
                    <Youtube className="w-20 h-20 mb-6" />
                    <p className="text-xl font-medium">Ingresa una URL para analizar el video</p>
                </div>
            )}
        </div>
    )
}
