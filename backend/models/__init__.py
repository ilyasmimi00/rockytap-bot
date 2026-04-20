# backend/models/__init__.py
"""
جميع نماذج قاعدة البيانات
"""

from backend.models.base import Base
from backend.models.user import User
from backend.models.transaction import Withdrawal
from backend.models.referral import Referral
from backend.models.giftcode import GiftCode, GiftCodeUsage
from backend.models.ad import AdWatch
from backend.models.wheel import WheelSpin
from backend.models.setting import SystemSetting
from backend.models.log import AdminLog
from backend.models.task import Task, UserTask
from backend.models.ad_package import AdPackage, UserAd, AdMember, AdRequest