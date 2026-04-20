# backend/services/user_service.py
"""
خدمات المستخدم - منطق الأعمال
"""

from sqlalchemy.orm import Session
from datetime import datetime

from backend.models.user import User


class UserService:
    """خدمات إدارة المستخدمين"""
    
    @staticmethod
    def get_or_create_user(
        db: Session, 
        user_id: int, 
        username: str = None, 
        first_name: str = None
    ) -> User:
        """الحصول على مستخدم أو إنشائه"""
        user = db.query(User).filter_by(user_id=user_id).first()
        
        if not user:
            user = User(
                user_id=user_id,
                username=username,
                first_name=first_name,
                join_date=datetime.now(),
                last_active=datetime.now()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user.last_active = datetime.now()
            if username:
                user.username = username
            if first_name:
                user.first_name = first_name
            db.commit()
        
        return user
    
    @staticmethod
    def get_user(db: Session, user_id: int) -> User:
        """الحصول على مستخدم"""
        return db.query(User).filter_by(user_id=user_id).first()
    
    @staticmethod
    def update_balance(
        db: Session, 
        user_id: int, 
        ton_amount: float = 0, 
        points_amount: float = 0,
        update_earned: bool = False
    ) -> bool:
        """تحديث رصيد المستخدم"""
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            return False
        
        if ton_amount != 0:
            user.balance_ton += ton_amount
            if update_earned and ton_amount > 0:
                user.total_earned_ton += ton_amount
        
        if points_amount != 0:
            user.balance_points += points_amount
            if update_earned and points_amount > 0:
                user.total_points_earned += points_amount
        
        user.last_active = datetime.now()
        db.commit()
        return True
    
    @staticmethod
    def get_all_users(db: Session, limit: int = 100, offset: int = 0):
        """جلب جميع المستخدمين"""
        return db.query(User).order_by(User.id.desc()).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_total_count(db: Session) -> int:
        """عدد المستخدمين الكلي"""
        return db.query(User).count()