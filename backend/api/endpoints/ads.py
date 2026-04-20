# backend/api/endpoints/ads.py
"""
مسارات API الخاصة بالإعلانات
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.services.user_service import UserService
from backend.services.ad_service import AdService
from backend.schemas import WatchAdRequest

router = APIRouter()


@router.get("/list")
async def get_ads(
    user_id: int = Query(..., description="معرف المستخدم"),
    db: Session = Depends(get_db)
):
    """جلب قائمة الإعلانات المتاحة"""
    today_ads = AdService.get_today_ads_count(db, user_id)
    daily_limit = 10  # من الإعدادات
    
    ads = [
        {"id": 1, "name": "AdsGram", "reward": 15, "icon": "📺"},
        {"id": 2, "name": "MontageWeb", "reward": 15, "icon": "🎬"},
        {"id": 3, "name": "GigaBI Display", "reward": 15, "icon": "🖥️"},
        {"id": 4, "name": "شركة 4", "reward": 15, "icon": "📱"}
    ]
    
    return {
        "success": True,
        "ads": ads,
        "watched_today": today_ads,
        "daily_limit": daily_limit
    }


@router.post("/watch")
async def watch_ad(
    request: WatchAdRequest,
    db: Session = Depends(get_db)
):
    """مشاهدة إعلان والحصول على مكافأة"""
    today_ads = AdService.get_today_ads_count(db, request.user_id)
    daily_limit = 10
    
    if today_ads >= daily_limit:
        raise HTTPException(status_code=400, detail="وصلت للحد اليومي للإعلانات")
    
    success, message = AdService.add_ad_watch(
        db, 
        request.user_id, 
        request.reward
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    user = UserService.get_user(db, request.user_id)
    remaining = daily_limit - (today_ads + 1)
    
    return {
        "success": True,
        "reward": request.reward,
        "new_points": user.balance_points,
        "remaining": remaining
    }