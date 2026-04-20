# backend/models/ad_package.py
"""
نماذج الإعلانات المدفوعة
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, BigInteger, ForeignKey, Text
from datetime import datetime

from backend.models.base import Base


class AdPackage(Base):
    """جدول باقات الإعلانات"""
    __tablename__ = 'ad_packages'
    
    id = Column(Integer, primary_key=True)
    views_count = Column(Integer, nullable=False)
    price_ton = Column(Float, nullable=False)
    bot_share = Column(Float, default=0.0005)
    executor_share = Column(Float, default=0.001)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


class UserAd(Base):
    """جدول إعلانات المستخدمين"""
    __tablename__ = 'user_ads'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    channel_link = Column(String(255), nullable=False)
    channel_username = Column(String(255))
    channel_id = Column(BigInteger)
    package_id = Column(Integer, ForeignKey('ad_packages.id'))
    views_count = Column(Integer, default=0)
    current_views = Column(Integer, default=0)
    members_count = Column(Integer, default=0)
    status = Column(String(50), default='pending')
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    expires_at = Column(DateTime)
    paid_amount = Column(Float, default=0.0)
    bot_earnings = Column(Float, default=0.0)
    user_earnings = Column(Float, default=0.0)
    admin_note = Column(Text)


class AdMember(Base):
    """جدول أعضاء شاهدوا الإعلان"""
    __tablename__ = 'ad_members'
    
    id = Column(Integer, primary_key=True)
    ad_id = Column(Integer, ForeignKey('user_ads.id'))
    member_id = Column(BigInteger, nullable=False)
    member_username = Column(String(255))
    watched_at = Column(DateTime, default=datetime.now)
    reward_points = Column(Float, default=0.0)
    reward_ton = Column(Float, default=0.0)
    is_unique = Column(Boolean, default=True)


class AdRequest(Base):
    """جدول طلبات إضافة القنوات"""
    __tablename__ = 'ad_requests'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    user_username = Column(String(255))
    channel_link = Column(String(255), nullable=False)
    channel_username = Column(String(255))
    channel_name = Column(String(255))
    admin_note = Column(Text)
    status = Column(String(50), default='pending')
    reviewed_by = Column(BigInteger)
    reviewed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)