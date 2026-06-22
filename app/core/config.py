from pydantic import BaseModel


class Settings(BaseModel):
    project_name: str = "ARP Converter API"
    description: str = "API base para convertir y procesar archivos ARP."
    version: str = "0.1.0"


settings = Settings()
