from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.checks.models import CheckResult
from src.checks.schemas import CheckResultIn
from src.models import utc_now


class CheckService:
    @staticmethod
    async def record_check_results(db: AsyncSession, server_id: str, checks: List[CheckResultIn]) -> int:
        now = utc_now()
        check_objects = []
        for c in checks:
            ts = c.timestamp if c.timestamp else now
            check_objects.append(
                CheckResult(
                    server_id=server_id,
                    check_name=c.check_name,
                    check_type=c.check_type,
                    status=c.status,
                    message=c.message,
                    timestamp=ts
                )
            )
        if check_objects:
            db.add_all(check_objects)
            await db.commit()
        return len(check_objects)

    @staticmethod
    async def get_latest_checks(db: AsyncSession, server_id: str) -> List[CheckResult]:
        # Return latest check result for each check_name for a server
        stmt = (
            select(CheckResult)
            .where(CheckResult.server_id == server_id)
            .order_by(CheckResult.timestamp.desc())
            .limit(100)
        )
        result = await db.execute(stmt)
        rows = result.scalars().all()

        seen_names = set()
        latest_list = []
        for r in rows:
            if r.check_name not in seen_names:
                seen_names.add(r.check_name)
                latest_list.append(r)

        return latest_list
