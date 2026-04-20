# backend/api/endpoints/wallet.py
"""
مسارات API الخاصة بالمحفظة والسحب والتحويل
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.services.user_service import UserService
from backend.services.wallet_service import WalletService
from backend.schemas import WithdrawRequest, ConvertRequest

router = APIRouter()


@router.post("/convert")
async def convert_points(
    request: ConvertRequest,
    db: Session = Depends(get_db)
):
    """تحويل النقاط إلى تون"""
    success, message = WalletService.convert_points(
        db, 
        request.user_id, 
        request.points
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    user = UserService.get_user(db, request.user_id)
    return {
        "success": True,
        "message": message,
        "ton": user.balance_ton,
        "points": user.balance_points
    }


@router.post("/withdraw")
async def request_withdraw(
    request: WithdrawRequest,
    db: Session = Depends(get_db)
):
    """طلب سحب"""
    success, result = WalletService.create_withdrawal(
        db,
        user_id=request.user_id,
        username=request.username,
        amount=request.amount,
        wallet_address=request.wallet_address
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=result)
    
    return {
        "success": True,
        "withdrawal_id": result,
        "message": "تم إرسال طلب السحب بنجاح"
    }


@router.get("/withdrawals")
async def get_withdrawals(
    user_id: int = Query(..., description="معرف المستخدم"),
    db: Session = Depends(get_db)
):
    """جلب سجل السحوبات للمستخدم"""
    withdrawals = WalletService.get_user_withdrawals(db, user_id)
    return {"success": True, "withdrawals": withdrawals}