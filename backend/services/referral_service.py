# backend/services/referral_service.py
"""
خدمات الإحالات
"""

from sqlalchemy.orm import Session
from datetime import datetime

from backend.models.user import User
from backend.models.referral import Referral  # سننشئ هذا لاحقاً


class ReferralService:
    """خدمات إدارة الإحالات"""
    
    @staticmethod
    def create_referral(db: Session, referrer_id: int, referred_id: int, referred_username: str = None):
        """إنشاء إحالة جديدة"""
        if referrer_id == referred_id:
            return False, "لا يمكنك إحالة نفسك"
        
        # التحقق من وجود إحالة مسبقة (مؤقتاً نمرر)
        
        # زيادة عدد الإحالات للمحيل
        referrer = db.query(User).filter_by(user_id=referrer_id).first()
        if referrer:
            referrer.total_referrals += 1
            db.commit()
        
        return True, "تم إنشاء الإحالة بنجاح"
    
    @staticmethod
    def get_user_stats(db: Session, user_id: int):
        """إحصائيات الإحالات للمستخدم"""
        # مؤقتاً نعيد إحصائيات فارغة
        return {
            'total': 0,
            'granted': 0,
            'pending': 0,
            'total_points_earned': 0,
            'total_ton_earned': 0,
            'referrals': []
        }