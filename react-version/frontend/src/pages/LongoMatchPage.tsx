import { useState } from 'react'
import axios from 'axios'
import { Upload, FileJson, FileSpreadsheet, Loader2 } from 'lucide-react'

export const LongoMatchPage = () => {
    const [file, setFile] = useState<File | null>(null)
    const [loading, setLoading] = useState(false)
    const [data, setData] = useState<any>(null)

    const handleUpload = async () => {
        if (!file) return
        setLoading(true)
        const formData = new FormData()
        formData.append('file', file)

        try {
            const response = await axios.post('/api/tools/longomatch/convert', formData)
            setData(response.data)
        } catch (error) {
            console.error('Error uploading file', error)
            alert('Error al procesar el archivo')
        } finally {
            setLoading(false)
        }
    }

    const downloadFile = (type: 'json' | 'csv') => {
        if (!data) return
        const content = type === 'json'
            ? JSON.stringify(data.instances, null, 2)
            : convertToCSV(data.instances)

        const blob = new Blob([content], { type: type === 'json' ? 'application/json' : 'text/csv' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `longomatch_export.${type}`
        a.click()
    }

    const convertToCSV = (objArray: any[]) => {
        const array = typeof objArray !== 'object' ? JSON.parse(objArray) : objArray
        let str = ''
        const headers = Object.keys(array[0]).join(',') + '\r\n'
        str += headers

        for (let i = 0; i < array.length; i++) {
            let line = ''
            for (const index in array[i]) {
                if (line !== '') line += ','
                line += array[i][index]
            }
            str += line + '\r\n'
        }
        return str
    }

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <header>
                <h1 className="text-3xl font-bold mb-2">LongoMatch XML Converter</h1>
                <p className="text-gray-400">Sube tu archivo XML para convertirlo a JSON o CSV de manera instantánea.</p>
            </header>

            <div className="bg-[#161618] border border-white/5 rounded-3xl p-12 flex flex-col items-center justify-center border-dashed hover:border-blue-500/30 transition-colors group">
                <Upload className="w-12 h-12 text-gray-600 mb-4 group-hover:text-blue-500 duration-300" />
                <p className="text-gray-400 mb-6">Arrastra y suelta tu archivo XML aquí o haz clic para buscar</p>
                <input
                    type="file"
                    accept=".xml"
                    className="hidden"
                    id="file-upload"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                />
                <label
                    htmlFor="file-upload"
                    className="px-8 py-3 bg-white text-black rounded-xl font-bold cursor-pointer hover:bg-gray-200 transition-all active:scale-95"
                >
                    {file ? file.name : 'Seleccionar Archivo'}
                </label>
            </div>

            {file && !data && (
                <button
                    onClick={handleUpload}
                    disabled={loading}
                    className="w-full py-4 bg-blue-600 rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-blue-500 transition-all disabled:opacity-50"
                >
                    {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Procesar Archivo'}
                </button>
            )}

            {data && (
                <div className="bg-[#161618] border border-white/5 rounded-3xl p-8 animate-in slide-in-from-bottom-4 duration-500">
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h3 className="text-xl font-bold">Procesamiento Completado</h3>
                            <p className="text-gray-500 text-sm">Se han encontrado {data.count} instancias.</p>
                        </div>
                        <div className="flex gap-4">
                            <button
                                onClick={() => downloadFile('csv')}
                                className="flex items-center gap-2 px-5 py-2.5 bg-emerald-500/10 text-emerald-400 rounded-xl border border-emerald-500/20 hover:bg-emerald-500/20 transition-all"
                            >
                                <FileSpreadsheet className="w-4 h-4" />
                                Descargar CSV
                            </button>
                            <button
                                onClick={() => downloadFile('json')}
                                className="flex items-center gap-2 px-5 py-2.5 bg-blue-500/10 text-blue-400 rounded-xl border border-blue-500/20 hover:bg-blue-500/20 transition-all"
                            >
                                <FileJson className="w-4 h-4" />
                                Descargar JSON
                            </button>
                        </div>
                    </div>

                    <div className="overflow-x-auto rounded-xl border border-white/5">
                        <table className="w-full text-left text-sm">
                            <thead className="bg-white/5 text-gray-400 uppercase text-[10px] font-bold tracking-widest">
                                <tr>
                                    <th className="px-6 py-4">ID</th>
                                    <th className="px-6 py-4">Start</th>
                                    <th className="px-6 py-4">End</th>
                                    <th className="px-6 py-4">Code</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {data.instances.slice(0, 5).map((inst: any) => (
                                    <tr key={inst.ID} className="hover:bg-white/[0.02] transition-colors">
                                        <td className="px-6 py-4 font-mono text-blue-400">{inst.ID}</td>
                                        <td className="px-6 py-4">{inst.start}</td>
                                        <td className="px-6 py-4">{inst.end}</td>
                                        <td className="px-6 py-4">{inst.code}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {data.count > 5 && (
                            <div className="p-4 text-center text-gray-500 text-xs italic bg-white/[0.01]">
                                Mostrando las primeras 5 de {data.count} instancias...
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}
