# models.py
"""
نماذج قاعدة البيانات - النسخة الكاملة مع نظام الإعلانات المتقدم
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, BigInteger, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """جدول المستخدمين"""
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


class AdWatch(Base):
    """جدول مشاهدة الإعلانات"""
    __tablename__ = 'ad_watches'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    date = Column(DateTime, default=datetime.now)
    points_earned = Column(Float, default=0.0)


class WheelSpin(Base):
    """جدول لعب عجلة الحظ"""
    __tablename__ = 'wheel_spins'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    date = Column(DateTime, default=datetime.now)
    reward_points = Column(Float, default=0.0)


class SystemSetting(Base):
    """جدول إعدادات النظام"""
    __tablename__ = 'system_settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AdminLog(Base):
    """جدول سجل إجراءات الأدمن"""
    __tablename__ = 'admin_logs'
    
    id = Column(Integer, primary_key=True)
    admin_id = Column(BigInteger, nullable=False)
    action = Column(String(255))
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)


class Task(Base):
    """جدول المهام"""
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500))
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