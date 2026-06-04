import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text
from pgvector.sqlalchemy import Vector

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Truck(Base):
    __tablename__ = "trucks"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    truck_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    driver_name: Mapped[str] = mapped_column(String)
    cargo: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    driver_phone_number: Mapped[str] = mapped_column(String)

class Warehouse(Base):
    __tablename__ = "warehouses"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    location_code: Mapped[str] = mapped_column(String, unique=True, index=True)
    hub_name: Mapped[str] = mapped_column(String)
    dock_number: Mapped[str] = mapped_column(String)
    eta_adjustment: Mapped[str] = mapped_column(String)
    real_address: Mapped[str] = mapped_column(String)
    maps_url: Mapped[str] = mapped_column(String)

class FAQKnowledgeBase(Base):
    __tablename__ = "faq_knowledge_base"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(String)
    answer: Mapped[str] = mapped_column(Text)
    embedding: Mapped[Vector] = mapped_column(Vector(1536))

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
