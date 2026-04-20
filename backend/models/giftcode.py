# backend/models/giftcode.py
"""
نماذج الأكواد الترويجية
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, BigInteger, ForeignKey
from datetime import datetime

from backend.models.base import Base


class GiftCode(Base):
    """جدول الأكواد الترويجية"""
    __tablename__ = 'gift_codes'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    reward_points = Column(Float, default=0.0)
    reward_ton = Column(Float, default=0.0)
    max_uses = Column(Integer, default=100)
    used_count = Column(Integer, default=0)
    created_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    is_admin_created = Column(Boolean, default=False)


class GiftCodeUsage(Base):
    """جدول استخدامات الأكواد"""
    __tablename__ = 'gift_code_usages'
    
    id = Column(Integer, primary_key=True)
    code_id = Column(Integer, ForeignKey('gift_codes.id'), nullable=False)
    user_id = Column(BigInteger, nullable=False)
    used_at = Column(DateTime, default=datetime.now)