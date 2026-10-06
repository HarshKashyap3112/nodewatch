from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.database import get_db
from src.servers.exceptions import ServerNotFoundException
from src.servers.models import Server
from src.servers.service import ServerService


async def get_server_or_404(
    server_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Server:
    server = await ServerService.get_server_by_id(db, server_id)
    if not server:
        raise ServerNotFoundException()
    if current_user.role != "owner" and server.owner_id != current_user.id:
        raise ServerNotFoundException()
    return server
