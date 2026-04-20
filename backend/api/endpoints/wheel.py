# backend/api/endpoints/wheel.py
"""
مسارات API الخاصة بعجلة الحظ
"""

import random
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.services.user_service import UserService
from backend.services.wheel_service import WheelService
from backend.schemas import SpinWheelRequest, WheelStatusResponse
from backend.config import DAILY_WHEEL_SPINS, WHEEL_REWARDS

router = APIRouter()


@router.get("/status")
async def get_wheel_status(
    user_id: int = Query(..., description="معرف المستخدم"),
    db: Session = Depends(get_db)
):
    """الحصول على حالة عجلة الحظ للمستخدم"""
    today_spins = WheelService.get_today_spins_count(db, user_id)
    remaining = max(0, DAILY_WHEEL_SPINS - today_spins)
    user = UserService.get_user(db, user_id)
    
    return {
        "success": True,
        "remaining_spins": remaining,
        "total_points": user.balance_points if user else 0
    }


@router.post("/spin")
async def spin_wheel(
    request: SpinWheelRequest,
    db: Session = Depends(get_db)
):
    """اللعب في عجلة الحظ"""
    today_spins = WheelService.get_today_spins_count(db, request.user_id)
    
    if today_spins >= DAILY_WHEEL_SPINS:
        raise HTTPException(status_code=400, detail="انتهت محاولاتك اليوم")
    
    # اختيار مكافأة عشوائية
    reward = random.choice(WHEEL_REWARDS)
    
    # منح المكافأة
    UserService.update_balance(db, request.user_id, points_amount=reward, update_earned=True)
    WheelService.add_spin(db, request.user_id, reward)
    
    user = UserService.get_user(db, request.user_id)
    remaining = DAILY_WHEEL_SPINS - (today_spins + 1)
    
    return {
        "success": True,
        "reward": reward,
        "new_points": user.balance_points,
        "remaining": remaining
    }