# backend/services/wallet_service.py
"""
خدمات المحفظة والسحب
"""

from sqlalchemy.orm import Session
from datetime import datetime

from backend.models.user import User
from backend.models.transaction import Withdrawal
from backend.config import POINTS_TO_TON_RATE, WITHDRAWAL_MIN


class WalletService:
    """خدمات إدارة المحفظة"""
    
    @staticmethod
    def convert_points(db: Session, user_id: int, points: float):
        """تحويل النقاط إلى تون"""
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            return False, "المستخدم غير موجود"
        
        min_convert = 10
        if points < min_convert:
            return False, f"الحد الأدنى للتحويل هو {min_convert} نقاط"
        
        if user.balance_points < points:
            return False, "النقاط غير كافية"
        
        ton_amount = points / POINTS_TO_TON_RATE
        
        user.balance_points -= points
        user.balance_ton += ton_amount
        db.commit()
        
        return True, f"تم تحويل {points} نقطة إلى {ton_amount:.4f} تون"
    
    @staticmethod
    def create_withdrawal(db: Session, user_id: int, username: str, amount: float, wallet_address: str):
        """إنشاء طلب سحب"""
        user = db.query(User).filter_by(user_id=user_id).first()
        if not user:
            return False, "المستخدم غير موجود"
        
        if user.balance_ton < amount:
            return False, "الرصيد غير كافٍ"
        
        if amount < WITHDRAWAL_MIN:
            return False, f"الحد الأدنى للسحب هو {WITHDRAWAL_MIN} تون"
        
        # خصم الرصيد
        user.balance_ton -= amount
        user.total_withdrawn_ton += amount
        
        # إنشاء طلب السحب
        withdrawal = Withdrawal(
            user_id=user_id,
            username=username,
            amount=amount,
            wallet_address=wallet_address,
            status='pending',
            requested_at=datetime.now()
        )
        db.add(withdrawal)
        db.commit()
        db.refresh(withdrawal)
        
        return True, withdrawal.id
    
    @staticmethod
    def get_user_withdrawals(db: Session, user_id: int):
        """جلب سجل السحوبات"""
        withdrawals = db.query(Withdrawal).filter_by(user_id=user_id).order_by(
            Withdrawal.requested_at.desc()
        ).limit(20).all()
        
        return [{
            'id': w.id,
            'amount': w.amount,
            'wallet_address': w.wallet_address,
            'status': w.status,
            'requested_at': w.requested_at.strftime('%Y-%m-%d %H:%M')
        } for w in withdrawals]