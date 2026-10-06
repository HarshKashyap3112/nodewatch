from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.checks.schemas import CheckResultOut
from src.checks.service import CheckService
from src.database import get_db
from src.servers.dependencies import get_server_or_404

router = APIRouter(prefix="/checks", tags=["Checks"])


@router.get("/latest/{server_id}", response_model=List[CheckResultOut])
async def get_latest_checks(
    server_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_server_or_404(server_id, db, current_user)
    results = await CheckService.get_latest_checks(db, server_id)
    return [CheckResultOut.model_validate(r) for r in results]
