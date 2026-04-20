# backend/db.py
"""
إدارة اتصال قاعدة البيانات
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool

from backend.config import DATABASE_URL
from backend.models.base import Base

# إنشاء محرك قاعدة البيانات
engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False} if 'sqlite' in DATABASE_URL else {},
    poolclass=StaticPool if 'sqlite' in DATABASE_URL else None,
    echo=False
)

# إنشاء الجداول
Base.metadata.create_all(engine)

# إنشاء مصنع الجلسات
SessionLocal = sessionmaker(bind=engine)
Session = scoped_session(SessionLocal)

def get_db():
    """الحصول على جلسة قاعدة البيانات (للاستخدام في API)"""
    db = Session()
    try:
        yield db
    finally:
        db.close()