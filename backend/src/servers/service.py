from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.servers.constants import ServerStatus
from src.servers.exceptions import ApiKeyRevokedException, InvalidApiKeyException, ServerNotFoundException
from src.servers.models import AgentApiKey, Server
from src.servers.schemas import ServerCreate, ServerUpdate
from src.servers.utils import generate_agent_api_key, hash_api_key


class ServerService:
    @staticmethod
    async def create_server(db: AsyncSession, owner_id: str, payload: ServerCreate) -> Tuple[Server, str, AgentApiKey]:
        server = Server(
            name=payload.name,
            hostname=payload.hostname,
            ip_address=payload.ip_address,
            os_info=payload.os_info,
            status=ServerStatus.OFFLINE,
            owner_id=owner_id
        )
        db.add(server)
        await db.flush()

        raw_key, hashed_key = generate_agent_api_key()
        api_key = AgentApiKey(
            server_id=server.id,
            key_hash=hashed_key,
            name="default",
            is_revoked=False
        )
        db.add(api_key)
        await db.commit()
        await db.refresh(server)
        await db.refresh(api_key)

        return server, raw_key, api_key

    @staticmethod
    async def get_server_by_id(db: AsyncSession, server_id: str) -> Optional[Server]:
        stmt = select(Server).where(Server.id == server_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_servers(db: AsyncSession, owner_id: Optional[str] = None) -> List[Server]:
        stmt = select(Server)
        if owner_id:
            stmt = stmt.where(Server.owner_id == owner_id)
        stmt = stmt.order_by(Server.name)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def update_server(db: AsyncSession, server_id: str, payload: ServerUpdate) -> Server:
        server = await ServerService.get_server_by_id(db, server_id)
        if not server:
            raise ServerNotFoundException()

        if payload.name is not None:
            server.name = payload.name
        if payload.hostname is not None:
            server.hostname = payload.hostname
        if payload.ip_address is not None:
            server.ip_address = payload.ip_address
        if payload.os_info is not None:
            server.os_info = payload.os_info
        if payload.status is not None:
            server.status = payload.status

        await db.commit()
        await db.refresh(server)
        return server

    @staticmethod
    async def delete_server(db: AsyncSession, server_id: str) -> None:
        server = await ServerService.get_server_by_id(db, server_id)
        if not server:
            raise ServerNotFoundException()

        await db.delete(server)
        await db.commit()

    @staticmethod
    async def update_server_last_seen(
        db: AsyncSession,
        server_id: str,
        status: Optional[ServerStatus] = None,
        hostname: Optional[str] = None,
        ip_address: Optional[str] = None,
        os_info: Optional[str] = None
    ) -> None:
        now = datetime.now(timezone.utc)
        values = {"last_seen_at": now}
        if status:
            values["status"] = status
        if hostname:
            values["hostname"] = hostname
        if ip_address:
            values["ip_address"] = ip_address
        if os_info:
            values["os_info"] = os_info

        stmt = update(Server).where(Server.id == server_id).values(**values)
        await db.execute(stmt)
        await db.commit()

    @staticmethod
    async def generate_new_api_key(db: AsyncSession, server_id: str, name: str = "custom") -> Tuple[str, AgentApiKey]:
        server = await ServerService.get_server_by_id(db, server_id)
        if not server:
            raise ServerNotFoundException()

        raw_key, hashed_key = generate_agent_api_key()
        api_key = AgentApiKey(
            server_id=server.id,
            key_hash=hashed_key,
            name=name,
            is_revoked=False
        )
        db.add(api_key)
        await db.commit()
        await db.refresh(api_key)
        return raw_key, api_key

    @staticmethod
    async def revoke_api_key(db: AsyncSession, key_id: str) -> None:
        stmt = select(AgentApiKey).where(AgentApiKey.id == key_id)
        result = await db.execute(stmt)
        api_key = result.scalar_one_or_none()
        if not api_key:
            raise ServerNotFoundException("API key not found")

        api_key.is_revoked = True
        await db.commit()

    @staticmethod
    async def authenticate_agent_key(db: AsyncSession, raw_key: str) -> Server:
        hashed_key = hash_api_key(raw_key)
        stmt = select(AgentApiKey).where(AgentApiKey.key_hash == hashed_key)
        result = await db.execute(stmt)
        api_key = result.scalar_one_or_none()

        if not api_key:
            raise InvalidApiKeyException()
        if api_key.is_revoked:
            raise ApiKeyRevokedException()

        api_key.last_used_at = datetime.now(timezone.utc)
        server = await ServerService.get_server_by_id(db, api_key.server_id)
        if not server:
            raise ServerNotFoundException()

        await db.commit()
        return server
