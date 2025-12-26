import urllib.parse
import tempfile
import os
from yt_dlp import YoutubeDL
from typing import Dict, Any

def clean_youtube_url(url: str) -> str:
    """Limpia la URL de YouTube para quitar parámetros innecesarios."""
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    video_id = query.get("v", [None])[0]
    if not video_id and parsed.netloc == "youtu.be":
        video_id = parsed.path.strip("/")
    return f"https://www.youtube.com/watch?v={video_id}" if video_id else url

def get_video_info(video_url: str) -> Dict[str, Any]:
    """Obtiene la información y el enlace de descarga directo del video."""
    ydl_opts = {
        # Evita HLS/DASH y prioriza formatos progresivos con H.264 + AAC para QuickTime
        # El filtro [protocol!*=m3u8] evita HLS, [protocol!=http_dash_segments] evita DASH
        'format': (
            'bestvideo[ext=mp4][vcodec^=avc1][protocol^=https]+bestaudio[ext=m4a][protocol^=https]/'
            'best[ext=mp4][vcodec^=avc1][protocol^=https]/'
            'bestvideo[ext=mp4][protocol^=https]+bestaudio[ext=m4a][protocol^=https]/'
            'best[ext=mp4][protocol^=https]/'
            'best[protocol^=https]'
        ),
        'quiet': True,
        'merge_output_format': 'mp4',
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return {
            "title": info.get("title", "video"),
            "url": info.get("url"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "id": info.get("id"),
            "video_id": info.get("id")
        }

def download_video(video_url: str, output_path: str = None) -> str:
    """
    Descarga el video directamente al servidor en formato MP4 compatible con QuickTime.
    Retorna la ruta del archivo descargado.
    """
    if output_path is None:
        # Crear directorio temporal si no se especifica
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, 'youtube_downloads')
        os.makedirs(output_path, exist_ok=True)

    ydl_opts = {
        # Formato compatible con QuickTime: H.264 + AAC en MP4
        'format': (
            'bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/'
            'best[ext=mp4][vcodec^=avc1]/'
            'bestvideo[ext=mp4]+bestaudio[ext=m4a]/'
            'best[ext=mp4]/'
            'best'
        ),
        'outtmpl': os.path.join(output_path, '%(id)s.%(ext)s'),
        'merge_output_format': 'mp4',
        # Opciones de FFmpeg para optimizar para QuickTime
        'postprocessor_args': {
            'ffmpeg': [
                '-c:v', 'copy',          # Copia el video sin recodificar
                '-c:a', 'aac',           # Asegura codec de audio AAC
                '-movflags', '+faststart' # Optimiza para reproducción (mueve moov atom al inicio)
            ]
        },
        'prefer_ffmpeg': True,
        'quiet': False,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=True)
        video_id = info.get('id')
        # El archivo descargado tendrá el nombre del video_id
        downloaded_file = os.path.join(output_path, f"{video_id}.mp4")
        return downloaded_file
