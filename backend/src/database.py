import asyncio
import ssl
import sys
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.config import settings

# On Windows with Python 3.8+, use SelectorEventLoop for reliable SSL socket handling
if sys.platform == "win32":
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass

def normalize_database_url(url: str) -> str:
    url = url.strip()
    if url.startswith("mysql://"):
        url = "mysql+aiomysql://" + url[len("mysql://"):]
    elif url.startswith("mysql+pymysql://"):
        url = "mysql+aiomysql://" + url[len("mysql+pymysql://"):]
    elif url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]

    # TiDB Cloud: rewrite /sys to /test if accidentally specified (sys is reserved for system metrics)
    if "/sys?" in url:
        url = url.replace("/sys?", "/test?", 1)
    elif url.endswith("/sys"):
        url = url[:-4] + "/test"

    # Strip literal <CA_PATH> placeholders from connection strings
    if "<CA_PATH>" in url or "<ca_path>" in url.lower():
        url = url.split("?")[0]

    return url


db_url = normalize_database_url(settings.DATABASE_URL)

# Engine configuration handles MySQL (aiomysql) and SQLite fallback (aiosqlite)
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
elif "tidbcloud.com" in db_url or "ssl" in db_url.lower():
    connect_args["ssl"] = ssl.create_default_context()

engine = create_async_engine(
    db_url,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
