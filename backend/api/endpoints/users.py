# backend/api/endpoints/users.py
"""
مسارات API الخاصة بالمستخدمين
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.services.user_service import UserService
from backend.schemas import UserResponse, UpdateBalanceRequest
from backend.core.security import is_admin

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: int = Query(..., description="معرف المستخدم"),
    db: Session = Depends(get_db)
):
    """الحصول على بيانات المستخدم الحالي"""
    user = UserService.get_user(db, user_id)
    if not user:
        # إنشاء المستخدم إذا لم يكن موجوداً
        user = UserService.get_or_create_user(db, user_id)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    admin_id: int = Query(..., description="معرف المشرف"),
    db: Session = Depends(get_db)
):
    """الحصول على بيانات مستخدم (للمشرف فقط)"""
    if not is_admin(admin_id):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/balance")
async def update_balance(
    request: UpdateBalanceRequest,
    admin_id: int = Query(..., description="معرف المشرف"),
    db: Session = Depends(get_db)
):
    """تحديث رصيد المستخدم (للمشرف فقط)"""
    if not is_admin(admin_id):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    success = UserService.update_balance(
        db, 
        request.user_id,
        ton_amount=request.ton_amount,
        points_amount=request.points_amount
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update balance")
    
    return {"success": True, "message": "Balance updated"}


@router.get("/all/list")
async def get_all_users(
    admin_id: int = Query(..., description="معرف المشرف"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """جلب جميع المستخدمين (للمشرف فقط)"""
    if not is_admin(admin_id):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = UserService.get_all_users(db, limit, offset)
    total = UserService.get_total_count(db)
    
    return {
        "success": True,
        "total": total,
        "users": users
    }