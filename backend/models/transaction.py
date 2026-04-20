# backend/models/transaction.py
"""
نموذج المعاملات والسحوبات
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger
from datetime import datetime

from backend.models.base import Base


class Withdrawal(Base):
    """جدول طلبات السحب"""
    __tablename__ = 'withdrawals'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    username = Column(String(255))
    amount = Column(Float, nullable=False)
    wallet_address = Column(String(255), nullable=False)
    status = Column(String(50), default='pending')
    rejection_reason = Column(String(500))
    requested_at = Column(DateTime, default=datetime.now)
    paid_at = Column(DateTime)
    processed_by = Column(BigInteger)