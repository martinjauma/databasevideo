from fastapi import APIRouter, UploadFile, File, HTTPException, Response
from fastapi.responses import StreamingResponse, FileResponse
from services import longomatch_service, youtube_service
import httpx
import os
from typing import Any
from pydantic import BaseModel

router = APIRouter(prefix="/api/tools", tags=["tools"])

@router.post("/longomatch/convert")
async def convert_longomatch(file: UploadFile = File(...)) -> Any:
    if not file.filename.endswith('.xml'):
        raise HTTPException(status_code=400, detail="File must be an XML")
    
    content = await file.read()
    try:
        instances = longomatch_service.convert_longomatch_xml_to_instances(content.decode("utf-8"))
        return {
            "count": len(instances),
            "instances": instances
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class YouTubeRequest(BaseModel):
    url: str

@router.post("/youtube/info")
async def get_youtube_info(request: YouTubeRequest):
    try:
        print(f"Recibida petición de info para URL: {request.url}")
        cleaned_url = youtube_service.clean_youtube_url(request.url)
        print(f"URL Limpia: {cleaned_url}")
        info = youtube_service.get_video_info(cleaned_url)
        return info
    except Exception as e:
        print(f"ERROR en get_youtube_info: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/youtube/download")
async def download_video(video_id: str, title: str = "video"):
    try:
        print(f"Iniciando descarga para: {title} (ID: {video_id})")

        # Construir la URL de YouTube desde el video_id
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"Descargando video desde: {youtube_url}")

        # Descargar el video al servidor con formato compatible con QuickTime
        downloaded_file = youtube_service.download_video(youtube_url)
        print(f"Video descargado en: {downloaded_file}")

        # Verificar que el archivo existe
        if not os.path.exists(downloaded_file):
            raise HTTPException(status_code=404, detail="Video descargado no encontrado")

        # Retornar el archivo con limpieza después de la descarga
        return FileResponse(
            path=downloaded_file,
            media_type="video/mp4",
            filename=f"{title}.mp4",
            headers={
                "Content-Disposition": f'attachment; filename="{title}.mp4"',
                "Access-Control-Expose-Headers": "Content-Disposition"
            },
            background=None  # El archivo se mantendrá disponible hasta que se complete la descarga
        )
    except Exception as e:
        print(f"Error en descarga: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al procesar la descarga: {str(e)}")

