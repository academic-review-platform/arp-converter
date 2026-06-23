import shutil
import tempfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import urlopen

from fastapi import FastAPI, HTTPException
from markitdown import MarkItDown
from pydantic import BaseModel, HttpUrl

from app.core.config import settings


markitdown = MarkItDown()


class ConvertRequest(BaseModel):
    download_url: HttpUrl


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        description=settings.description,
    )

    @app.post("/convert")
    def convert(payload: ConvertRequest) -> dict[str, object]:
        download_url = str(payload.download_url)
        suffix = Path(urlparse(download_url).path).suffix
        downloaded_file_path: str | None = None

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                downloaded_file_path = temp_file.name

                with urlopen(download_url) as response:
                    shutil.copyfileobj(response, temp_file)
        except HTTPError as error:
            raise HTTPException(
                status_code=error.code,
                detail="No se pudo descargar el archivo desde la URL proporcionada.",
            ) from error
        except (URLError, OSError) as error:
            raise HTTPException(
                status_code=400,
                detail="No se pudo descargar el archivo desde la URL proporcionada.",
            ) from error

        try:
            result = markitdown.convert(downloaded_file_path)
        except Exception as error:
            raise HTTPException(
                status_code=422,
                detail="No se pudo extraer la informacion del archivo proporcionado.",
            ) from error
        finally:
            if downloaded_file_path is not None:
                Path(downloaded_file_path).unlink(missing_ok=True)

        return {
            "success": True,
            "data": {
                "message": "informacion extraida de forma exitosa",
                "content": result.markdown,
            },
        }

    return app


app = create_app()
