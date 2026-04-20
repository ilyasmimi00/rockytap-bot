# backend/core/security.py
"""
التحقق من أمان البيانات القادمة من تليجرام
"""

import hashlib
import hmac
import json
from typing import Optional, Dict

from backend.config import BOT_TOKEN


def verify_telegram_auth(init_data: str) -> Optional[Dict]:
    """
    التحقق من صحة بيانات المصادقة القادمة من تليجرام WebApp
    
    Args:
        init_data: سلسلة query parameters من Telegram.WebApp.initData
        
    Returns:
        قاموس بيانات المستخدم إذا كانت صالحة، None إذا لم تكن صالحة
    """
    if not init_data:
        return None
    
    try:
        # تحويل السلسلة إلى قاموس
        params = dict(pair.split('=') for pair in init_data.split('&'))
        
        # استخراج hash
        received_hash = params.pop('hash', None)
        if not received_hash:
            return None
        
        # ترتيب المعاملات أبجدياً
        sorted_params = sorted(params.items())
        data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted_params)
        
        # إنشاء hash للتحقق
        secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
        computed_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # مقارنة
        if computed_hash == received_hash:
            # التحقق من صلاحية البيانات (آخر 24 ساعة)
            auth_date = int(params.get('auth_date', 0))
            from datetime import datetime
            if datetime.now().timestamp() - auth_date < 86400:
                # استخراج بيانات المستخدم
                user_data = json.loads(params.get('user', '{}'))
                return user_data
        
        return None
        
    except Exception:
        return None


def is_admin(user_id: int) -> bool:
    """التحقق مما إذا كان المستخدم مشرفاً"""
    from backend.config import ADMIN_IDS
    return user_id in ADMIN_IDS