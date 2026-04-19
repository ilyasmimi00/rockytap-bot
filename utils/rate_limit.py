# utils/rate_limit.py
"""
نظام تحديد معدل الطلبات (Rate Limiting)
لحماية البوت من الاستخدام المفرط والهجمات
"""

from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps
import asyncio
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    نظام تحديد معدل الطلبات
    يحد من عدد الطلبات التي يمكن لمستخدم واحد إرسالها خلال فترة زمنية محددة
    """
    
    def __init__(self, max_requests: int = 30, time_window: int = 60):
        """
        تهيئة نظام تحديد المعدل
        
        Args:
            max_requests: الحد الأقصى لعدد الطلبات المسموح بها
            time_window: الفترة الزمنية بالثواني
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
        self.blocked_users = {}  # المستخدمين المحظورين مؤقتاً
        self.block_duration = 300  # مدة الحظر المؤقت بالثواني (5 دقائق)
    
    async def check(self, user_id: int) -> bool:
        """
        التحقق مما إذا كان المستخدم يمكنه إرسال طلب
        
        Args:
            user_id: معرف المستخدم
            
        Returns:
            bool: True إذا كان مسموحاً، False إذا تم تجاوز الحد
        """
        now = datetime.now()
        
        # التحقق من الحظر المؤقت
        if user_id in self.blocked_users:
            block_until = self.blocked_users[user_id]
            if now < block_until:
                logger.warning(f"User {user_id} is temporarily blocked until {block_until}")
                return False
            else:
                # إزالة الحظر بعد انتهاء الوقت
                del self.blocked_users[user_id]
        
        # تنظيف الطلبات القديمة
        window_start = now - timedelta(seconds=self.time_window)
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id] 
            if req_time > window_start
        ]
        
        # التحقق من الحد الأقصى
        if len(self.requests[user_id]) >= self.max_requests:
            # حظر المستخدم مؤقتاً إذا تجاوز الحد بشكل متكرر
            violation_count = getattr(self, f'violations_{user_id}', 0) + 1
            setattr(self, f'violations_{user_id}', violation_count)
            
            if violation_count >= 3:
                # حظر لمدة أطول
                self.blocked_users[user_id] = now + timedelta(seconds=self.block_duration * 2)
                logger.warning(f"User {user_id} blocked for {self.block_duration * 2}s due to repeated violations")
            elif violation_count >= 2:
                # حظر لمدة أقصر
                self.blocked_users[user_id] = now + timedelta(seconds=self.block_duration)
                logger.warning(f"User {user_id} blocked for {self.block_duration}s")
            
            return False
        
        # تسجيل الطلب
        self.requests[user_id].append(now)
        return True
    
    async def check_command(self, user_id: int, command: str) -> bool:
        """
        التحقق من أمر محدد (يمكن أن يكون له حدود مختلفة)
        
        Args:
            user_id: معرف المستخدم
            command: اسم الأمر
            
        Returns:
            bool: True إذا كان مسموحاً
        """
        # حدود مختلفة لأنواع مختلفة من الأوامر
        limits = {
            'spin_wheel': {'max': 5, 'window': 60},      # 5 لفات في الدقيقة
            'watch_ad': {'max': 10, 'window': 60},       # 10 إعلانات في الدقيقة
            'convert': {'max': 3, 'window': 300},        # 3 تحويلات في 5 دقائق
            'withdraw': {'max': 2, 'window': 3600},      # 2 طلبات سحب في الساعة
            'referral_share': {'max': 5, 'window': 300}, # 5 مشاركات في 5 دقائق
            'default': {'max': 30, 'window': 60}         # الإعداد الافتراضي
        }
        
        limit = limits.get(command, limits['default'])
        
        # استخدام نظام مؤقت للمعدل الخاص بالأمر
        key = f"{user_id}_{command}"
        now = datetime.now()
        
        # تخزين مؤقت للطلبات الخاصة بالأمر
        if not hasattr(self, 'command_requests'):
            self.command_requests = defaultdict(list)
        
        # تنظيف الطلبات القديمة
        window_start = now - timedelta(seconds=limit['window'])
        self.command_requests[key] = [
            req_time for req_time in self.command_requests[key]
            if req_time > window_start
        ]
        
        if len(self.command_requests[key]) >= limit['max']:
            logger.warning(f"User {user_id} exceeded rate limit for command {command}")
            return False
        
        self.command_requests[key].append(now)
        return True
    
    def reset_user(self, user_id: int):
        """إعادة تعيين جميع حدود المستخدم"""
        if user_id in self.requests:
            del self.requests[user_id]
        if user_id in self.blocked_users:
            del self.blocked_users[user_id]
        
        # تنظيف الطلبات الخاصة بالأوامر
        keys_to_delete = [k for k in getattr(self, 'command_requests', {}) if k.startswith(f"{user_id}_")]
        for key in keys_to_delete:
            if hasattr(self, 'command_requests'):
                del self.command_requests[key]
        
        # إعادة تعيين عدد المخالفات
        violation_attr = f'violations_{user_id}'
        if hasattr(self, violation_attr):
            delattr(self, violation_attr)
        
        logger.info(f"Rate limits reset for user {user_id}")
    
    def get_stats(self, user_id: int) -> dict:
        """الحصول على إحصائيات المستخدم"""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.time_window)
        
        recent_requests = [
            req_time for req_time in self.requests.get(user_id, [])
            if req_time > window_start
        ]
        
        is_blocked = user_id in self.blocked_users
        block_until = self.blocked_users.get(user_id)
        
        return {
            'recent_requests': len(recent_requests),
            'max_allowed': self.max_requests,
            'is_blocked': is_blocked,
            'block_until': block_until.isoformat() if block_until else None,
            'remaining': max(0, self.max_requests - len(recent_requests))
        }


# إنشاء مثيل عام لنظام تحديد المعدل
rate_limiter = RateLimiter(max_requests=30, time_window=60)


def rate_limit(max_requests: int = None, time_window: int = None, command: str = None):
    """
    Decorator لتحديد معدل الطلبات للدوال
    
    Args:
        max_requests: الحد الأقصى للطلبات (يتجاوز الإعداد الافتراضي)
        time_window: الفترة الزمنية بالثواني
        command: اسم الأمر لتطبيق حدود خاصة
    
    الاستخدام:
        @rate_limit(max_requests=5, time_window=60)
        async def my_handler(update, context):
            ...
        
        @rate_limit(command='spin_wheel')
        async def spin_wheel(update, context):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, update, context, *args, **kwargs):
            user_id = None
            
            # استخراج معرف المستخدم من update
            if update.callback_query:
                user_id = update.callback_query.from_user.id
            elif update.effective_user:
                user_id = update.effective_user.id
            elif update.message:
                user_id = update.message.from_user.id
            
            if not user_id:
                # لا يمكن تحديد المستخدم، السماح بالطلب
                return await func(self, update, context, *args, **kwargs)
            
            # استخدام إعدادات مخصصة إذا تم توفيرها
            if max_requests and time_window:
                # إنشاء مثيل مؤقت للمعدل
                temp_limiter = RateLimiter(max_requests=max_requests, time_window=time_window)
                allowed = await temp_limiter.check(user_id)
            elif command:
                allowed = await rate_limiter.check_command(user_id, command)
            else:
                allowed = await rate_limiter.check(user_id)
            
            if not allowed:
                # إرسال رسالة تجاوز الحد
                msg = "⏳ عدد كبير من الطلبات! يرجى الانتظار قليلاً قبل المحاولة مرة أخرى."
                
                if update.callback_query:
                    await update.callback_query.answer(msg, show_alert=True)
                else:
                    await update.message.reply_text(msg)
                
                return None
            
            return await func(self, update, context, *args, **kwargs)
        return wrapper
    return decorator


def admin_rate_limit(func):
    """
    Decorator خاص للمشرفين - حدود أعلى
    """
    @wraps(func)
    async def wrapper(self, update, context, *args, **kwargs):
        user_id = None
        
        if update.callback_query:
            user_id = update.callback_query.from_user.id
        elif update.effective_user:
            user_id = update.effective_user.id
        elif update.message:
            user_id = update.message.from_user.id
        
        if not user_id:
            return await func(self, update, context, *args, **kwargs)
        
        # التحقق من صلاحيات المشرف
        admin_ids = getattr(self, 'admin_ids', [])
        is_admin = user_id in admin_ids
        
        if is_admin:
            # المشرفين لديهم حدود أعلى بكثير
            admin_limiter = RateLimiter(max_requests=200, time_window=60)
            allowed = await admin_limiter.check(user_id)
        else:
            allowed = await rate_limiter.check(user_id)
        
        if not allowed:
            msg = "⏳ عدد كبير من الطلبات! يرجى الانتظار قليلاً."
            
            if update.callback_query:
                await update.callback_query.answer(msg, show_alert=True)
            else:
                await update.message.reply_text(msg)
            
            return None
        
        return await func(self, update, context, *args, **kwargs)
    return wrapper


class RateLimitMiddleware:
    """
    وسيط لتطبيق تحديد المعدل على جميع الطلبات الواردة
    يمكن إضافته إلى التطبيق ككل
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.limiter = rate_limiter
    
    async def __call__(self, update, context):
        """تطبيق تحديد المعدل على الطلب"""
        user_id = None
        
        if update.callback_query:
            user_id = update.callback_query.from_user.id
        elif update.effective_user:
            user_id = update.effective_user.id
        elif update.message:
            user_id = update.message.from_user.id
        
        if user_id:
            # التحقق من صلاحيات المشرف
            admin_ids = getattr(self.bot, 'admin_ids', [])
            if user_id in admin_ids:
                # المشرفين مسموح لهم بدون حدود
                return True
            
            allowed = await self.limiter.check(user_id)
            
            if not allowed:
                if update.callback_query:
                    await update.callback_query.answer(
                        "⏳ عدد كبير من الطلبات! يرجى الانتظار قليلاً.",
                        show_alert=True
                    )
                else:
                    await update.message.reply_text(
                        "⏳ عدد كبير من الطلبات! يرجى الانتظار قليلاً قبل المحاولة مرة أخرى."
                    )
                return False
        
        return True