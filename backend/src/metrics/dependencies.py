from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.servers.exceptions import InvalidApiKeyException
from src.servers.models import Server
from src.servers.service import ServerService


async def authenticate_agent(
    x_agent_api_key: str = Header(..., alias="X-Agent-API-Key"),
    db: AsyncSession = Depends(get_db)
) -> Server:
    if not x_agent_api_key:
        raise InvalidApiKeyException("Missing X-Agent-API-Key header")
    server = await ServerService.authenticate_agent_key(db, x_agent_api_key)
    return server
