import os
from datetime import datetime
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from contextlib import asynccontextmanager
from sqlalchemy.engine import result
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, false, select

DATABASE_URL = "sqlite+aiosqlite:///./c2_matrix.db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# Agent Registry Table
class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    hostname: Mapped[str] = mapped_column(String(100))
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# Encrypted Log Dump Table
class EncryptedTelemetry(Base):
    __tablename__ = "telemetry"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[str] = mapped_column(String(100), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    encrypted_data: Mapped[str] = mapped_column(Text)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# Dependency to yield database sessions to endpoints cleanly
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


class RegisterSchema(BaseModel):
    client_id: str
    hostname: str


class TelemetrySchema(BaseModel):
    client_id: str
    timestamp: datetime
    encrypted_data: str


class TelemetryResponse(BaseModel):
    id: int
    client_id: str
    timestamp: datetime
    encrypted_data: str
    received_at: datetime

    class Config:
        from_attributes = True


@asynccontextmanager
async def lifespan(app):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[c2 SERVER] Matrix engine initialized via lifespan. Async SQLite ready.")
    yield


app = FastAPI(title="Colossus Command & Control System", version="1.0.0")


# Agent Node Registration
@app.post("api/v1/agent/register", status_code=status.HTTP_201_CREATED)
async def register_agent(payload: RegisterSchema, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.client_id == payload.client_id))
    existing_agent = result.scalar_one_or_none()

    if existing_agent:
        return {
            "Status": "recognized",
            "message": "Agent already logged inside backend configuration matrix.",
        }

    new_agent = Agent(client_id=payload.client_id, hostname=payload.hostname)
    db.add(new_agent)
    await db.commit()
    return {"Status": "registered", "message": "New client agent validated and active."}


# Secure Inbound Data Ingestion
@app.post("api/v1/agent/telemetry", status_code=status.HTTP_202_ACCEPTED)
async def accept_telemetry(
    payload: TelemetrySchema, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Agent).where(Agent.client_id == payload.client_id))
    agent_exists = result.scalar_one_or_none()

    if not agent_exists:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access Denied: Unregistered entity signature rejected.",
        )

    telemetry_record = EncryptedTelemetry(
        client_id=payload.client_id,
        timestamp=payload.timestamp,
        encrypted_data=payload.encrypted_data,
    )
    db.add(telemetry_record)
    await db.commit()
    return {"Status": "absorbed", "bytes_written": len(payload.encrypted_data)}


# Operational Monitoring Dashboard Data Source
@app.get("api/v1/dashbaord/logs", response_model=List[TelemetryResponse])
async def get_dashboard_logs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EncryptedTelemetry).order_by(EncryptedTelemetry.received_at.desc())
    )
    logs = result.scalars().all()
    return logs
