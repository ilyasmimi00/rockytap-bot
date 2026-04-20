# backend/models/user.py
"""
نموذج المستخدم
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, BigInteger
from datetime import datetime

from backend.models.base import Base


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255))
    first_name = Column(String(255))
    balance_ton = Column(Float, default=0.0)
    balance_points = Column(Float, default=0.0)
    total_referrals = Column(Integer, default=0)
    join_date = Column(DateTime, default=datetime.now)
    last_active = Column(DateTime, default=datetime.now)
    is_blocked = Column(Boolean, default=False)
    first_withdrawal_completed = Column(Boolean, default=False)
    total_earned_ton = Column(Float, default=0.0)
    total_withdrawn_ton = Column(Float, default=0.0)
    total_points_earned = Column(Float, default=0.0)