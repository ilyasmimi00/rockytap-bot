# backend/models/task.py
"""
نماذج المهام
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, BigInteger, ForeignKey, Text
from datetime import datetime

from backend.models.base import Base


class Task(Base):
    """جدول المهام"""
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    icon = Column(String(50), default='📺')
    channel_link = Column(String(255), nullable=False)
    channel_username = Column(String(255))
    reward_points = Column(Float, default=0.0)
    reward_ton = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_by = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.now)
    order_index = Column(Integer, default=0)


class UserTask(Base):
    """جدول تقدم المستخدم في المهام"""
    __tablename__ = 'user_tasks'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    status = Column(String(50), default='pending')
    completed_at = Column(DateTime)
    claimed_at = Column(DateTime)