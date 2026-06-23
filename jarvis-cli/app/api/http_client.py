"""
app/api/http_client.py — Modo "http": la versión que ya armamos antes.
"""

import json
import httpx
from typing import AsyncIterator

from app.api.base import JarvisClientBase


class HttpJarvisClient(JarvisClientBase):
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def enviar_mensaje_stream(
        self, mensaje: str, chat_id: str, user_id: str
    ) -> AsyncIterator[str]:
        payload = {"message": mensaje, "user_id": user_id}
        url = f"{self.base_url}/api/v2/chat/{chat_id}/stream"

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", url, json=payload) as response:
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    data = line.removeprefix("data:").strip()
                    if data == "[DONE]":
                        break
                    chunk = json.loads(data)
                    if chunk.get("type") == "token":
                        yield chunk["content"]