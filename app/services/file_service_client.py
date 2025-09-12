import httpx
from app.core.config import FILE_SERVICE_URL

class FileServiceClient:
    async def get_download_url(self, object_key: str) -> str | None:
        async with httpx.AsyncClient(
            http2=False, trust_env=False, timeout=10.0
        ) as client:
            try:
                response = await client.get(
                    f"{FILE_SERVICE_URL}/files/download-url",
                    params={"object_key": object_key}
                )
                response.raise_for_status()
                return response.json().get("download_url")
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                print(f"Error requesting download URL: {e}")
                return None

file_service_client = FileServiceClient()