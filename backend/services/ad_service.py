# backend/services/ad_service.py
"""
خدمات الإعلانات
"""

from sqlalchemy.orm import Session
from datetime import datetime, date

from backend.models.user import User
from backend.models.ad import AdWatch  # سننشئ هذا لاحقاً


class AdService:
    """خدمات إدارة الإعلانات"""
    
    @staticmethod
    def get_today_ads_count(db: Session, user_id: int) -> int:
        """عدد الإعلانات التي شاهدها المستخدم اليوم"""
        today = date.today()
        # مؤقتاً نعيد 0
        return 0
    
    @staticmethod
    def add_ad_watch(db: Session, user_id: int, points_earned: int):
        """تسجيل مشاهدة إعلان"""
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            return False, "المستخدم غير موجود"
        
        user.balance_points += points_earned
        user.total_points_earned += points_earned
        db.commit()
        
        return True, "تم تسجيل المشاهدة"