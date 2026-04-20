# backend/api/router.py
"""
تجميع جميع مسارات API
"""

from fastapi import APIRouter

from backend.api.endpoints import users, wallet, ads, wheel, tasks, referrals

# إنشاء الـ router الرئيسي
api_router = APIRouter(prefix="/api")

# إضافة جميع الـ routers الفرعية
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(wallet.router, prefix="/wallet", tags=["wallet"])
api_router.include_router(ads.router, prefix="/ads", tags=["ads"])
api_router.include_router(wheel.router, prefix="/wheel", tags=["wheel"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(referrals.router, prefix="/referrals", tags=["referrals"])