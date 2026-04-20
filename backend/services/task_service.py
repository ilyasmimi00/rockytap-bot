# backend/services/task_service.py
"""
خدمات المهام
"""

from sqlalchemy.orm import Session
from datetime import datetime

from backend.models.task import Task, UserTask  # سننشئ هذا لاحقاً


class TaskService:
    """خدمات إدارة المهام"""
    
    @staticmethod
    def get_active_tasks(db: Session):
        """جلب المهام النشطة"""
        # مؤقتاً نعيد مهام تجريبية
        return [
            {
                'id': 1,
                'title': 'قناة RockyTap',
                'description': 'اشترك في قناتنا',
                'icon': '📺',
                'channel_link': 'https://t.me/RockyTap',
                'channel_username': '@RockyTap',
                'reward_points': 100,
                'reward_ton': 0
            },
            {
                'id': 2,
                'title': 'قناة الأخبار',
                'description': 'تابع آخر الأخبار',
                'icon': '📰',
                'channel_link': 'https://t.me/CryptoNews',
                'channel_username': '@CryptoNews',
                'reward_points': 150,
                'reward_ton': 0.01
            }
        ]
    
    @staticmethod
    def get_task(db: Session, task_id: int):
        """جلب مهمة محددة"""
        tasks = TaskService.get_active_tasks(db)
        for task in tasks:
            if task['id'] == task_id:
                return task
        return None
    
    @staticmethod
    def get_user_task(db: Session, user_id: int, task_id: int):
        """جلب سجل مهمة المستخدم"""
        # مؤقتاً نعيد None
        return None
    
    @staticmethod
    def get_user_tasks_progress(db: Session, user_id: int):
        """جلب تقدم المستخدم في المهام"""
        return []
    
    @staticmethod
    def create_user_task(db: Session, user_id: int, task_id: int):
        """إنشاء سجل مهمة للمستخدم"""
        pass
    
    @staticmethod
    def complete_user_task(db: Session, user_id: int, task_id: int, task: dict):
        """إكمال مهمة المستخدم"""
        from backend.services.user_service import UserService
        
        # منح المكافأة
        UserService.update_balance(
            db, 
            user_id,
            ton_amount=task.get('reward_ton', 0),
            points_amount=task.get('reward_points', 0),
            update_earned=True
        )
        
        return True