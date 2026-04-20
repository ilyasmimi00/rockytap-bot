# backend/services/wheel_service.py
"""
خدمات عجلة الحظ
"""

from sqlalchemy.orm import Session
from datetime import date

from backend.models.wheel import WheelSpin  # سننشئ هذا لاحقاً


class WheelService:
    """خدمات إدارة عجلة الحظ"""
    
    @staticmethod
    def get_today_spins_count(db: Session, user_id: int) -> int:
        """عدد مرات اللعب اليوم"""
        today = date.today()
        # مؤقتاً نعيد 0
        return 0
    
    @staticmethod
    def add_spin(db: Session, user_id: int, reward_points: int):
        """تسجيل لعب"""
        # مؤقتاً نمرر
        pass