# backend/api/endpoints/referrals.py
"""
مسارات API الخاصة بالإحالات
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.services.referral_service import ReferralService
from backend.config import BOT_NAME

router = APIRouter()


@router.get("/stats")
async def get_referral_stats(
    user_id: int = Query(..., description="معرف المستخدم"),
    db: Session = Depends(get_db)
):
    """الحصول على إحصائيات الإحالات للمستخدم"""
    stats = ReferralService.get_user_stats(db, user_id)
    
    # رابط الإحالة
    bot_username = BOT_NAME.lower().replace(' ', '')
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    return {
        "success": True,
        "total": stats['total'],
        "granted": stats['granted'],
        "pending": stats['pending'],
        "total_points_earned": stats['total_points_earned'],
        "total_ton_earned": stats['total_ton_earned'],
        "referral_link": referral_link,
        "referrals": stats['referrals']
    }


@router.post("/create")
async def create_referral(
    referrer_id: int = Query(..., description="معرف المحيل"),
    referred_id: int = Query(..., description="معرف المدعو"),
    referred_username: str = Query(None, description="اسم المستخدم المدعو"),
    db: Session = Depends(get_db)
):
    """إنشاء إحالة جديدة"""
    success, message = ReferralService.create_referral(
        db,
        referrer_id=referrer_id,
        referred_id=referred_id,
        referred_username=referred_username
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message}