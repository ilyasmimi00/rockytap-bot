# backend/models/referral.py
"""
نموذج الإحالات
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, BigInteger
from datetime import datetime

from backend.models.base import Base


class Referral(Base):
    """جدول الإحالات"""
    __tablename__ = 'referrals'
    
    id = Column(Integer, primary_key=True)
    referrer_id = Column(BigInteger, nullable=False)
    referred_id = Column(BigInteger, unique=True, nullable=False)
    referred_username = Column(String(255))
    reward_points = Column(Float, default=0.0)
    reward_ton = Column(Float, default=0.0)
    reward_type = Column(String(20), default='both')
    is_reward_granted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)