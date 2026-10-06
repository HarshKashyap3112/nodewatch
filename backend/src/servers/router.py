from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.database import get_db
from src.servers.dependencies import get_server_or_404
from src.servers.models import Server
from src.servers.schemas import (
    ApiKeyCreatedOut,
    ApiKeyOut,
    ServerCreate,
    ServerOut,
    ServerUpdate,
    ServerWithKeyOut,
)
from src.servers.service import ServerService

router = APIRouter(prefix="/servers", tags=["Servers"])


@router.post("", response_model=ServerWithKeyOut, status_code=status.HTTP_201_CREATED)
async def create_server(
    payload: ServerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    server, raw_key, api_key = await ServerService.create_server(db, current_user.id, payload)
    return ServerWithKeyOut(
        server=ServerOut.model_validate(server),
        api_key=ApiKeyCreatedOut(
            id=api_key.id,
            server_id=api_key.server_id,
            name=api_key.name,
            is_revoked=api_key.is_revoked,
            last_used_at=api_key.last_used_at,
            created_at=api_key.created_at,
            raw_api_key=raw_key
        )
    )


@router.get("", response_model=List[ServerOut])
async def list_servers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    servers = await ServerService.list_servers(db, owner_id=current_user.id)
    return [ServerOut.model_validate(s) for s in servers]


@router.get("/{server_id}", response_model=ServerOut)
async def get_server(server: Server = Depends(get_server_or_404)):
    return ServerOut.model_validate(server)


@router.patch("/{server_id}", response_model=ServerOut)
async def update_server(
    payload: ServerUpdate,
    server: Server = Depends(get_server_or_404),
    db: AsyncSession = Depends(get_db)
):
    updated = await ServerService.update_server(db, server.id, payload)
    return ServerOut.model_validate(updated)


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(
    server: Server = Depends(get_server_or_404),
    db: AsyncSession = Depends(get_db)
):
    await ServerService.delete_server(db, server.id)


@router.post("/{server_id}/keys", response_model=ApiKeyCreatedOut, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    name: str = "custom",
    server: Server = Depends(get_server_or_404),
    db: AsyncSession = Depends(get_db)
):
    raw_key, api_key = await ServerService.generate_new_api_key(db, server.id, name=name)
    return ApiKeyCreatedOut(
        id=api_key.id,
        server_id=api_key.server_id,
        name=api_key.name,
        is_revoked=api_key.is_revoked,
        last_used_at=api_key.last_used_at,
        created_at=api_key.created_at,
        raw_api_key=raw_key
    )


@router.delete("/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await ServerService.revoke_api_key(db, key_id)
