# backend/api/endpoints/tasks.py
"""
مسارات API الخاصة بالمهام
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.services.user_service import UserService
from backend.services.task_service import TaskService

router = APIRouter()


@router.get("/list")
async def get_tasks(
    user_id: int = Query(..., description="معرف المستخدم"),
    db: Session = Depends(get_db)
):
    """جلب قائمة المهام المتاحة"""
    tasks = TaskService.get_active_tasks(db)
    
    # جلب تقدم المستخدم
    user_tasks = TaskService.get_user_tasks_progress(db, user_id)
    user_task_dict = {ut['task_id']: ut['status'] for ut in user_tasks}
    
    # إضافة حالة المهمة للمستخدم
    for task in tasks:
        task['user_status'] = user_task_dict.get(task['id'], 'available')
    
    return {"success": True, "tasks": tasks}


@router.post("/complete")
async def complete_task(
    task_id: int = Query(..., description="معرف المهمة"),
    user_id: int = Query(..., description="معرف المستخدم"),
    db: Session = Depends(get_db)
):
    """إكمال مهمة والحصول على مكافأة"""
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="المهمة غير موجودة")
    
    # التحقق من أن المستخدم لم يكمل المهمة مسبقاً
    user_task = TaskService.get_user_task(db, user_id, task_id)
    if user_task and user_task['status'] == 'completed':
        raise HTTPException(status_code=400, detail="لقد أكملت هذه المهمة مسبقاً")
    
    # إنشاء سجل المهمة إذا لم يكن موجوداً
    if not user_task:
        TaskService.create_user_task(db, user_id, task_id)
    
    # منح المكافأة وإكمال المهمة
    success = TaskService.complete_user_task(db, user_id, task_id, task)
    
    if not success:
        raise HTTPException(status_code=400, detail="حدث خطأ في إكمال المهمة")
    
    user = UserService.get_user(db, user_id)
    
    reward_text = ""
    if task['reward_points'] > 0:
        reward_text += f"⭐ {task['reward_points']} نقطة"
    if task['reward_ton'] > 0:
        if reward_text:
            reward_text += " + "
        reward_text += f"💰 {task['reward_ton']} تون"
    
    return {
        "success": True,
        "message": f"✅ مبروك! حصلت على {reward_text}",
        "new_points": user.balance_points,
        "new_ton": user.balance_ton
    }