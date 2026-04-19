# handlers/__init__.py
"""
معالجات البوت - RockyTap
هذا الملف يسهل استيراد جميع المعالجات من مكان واحد
"""

from .start import StartHandler
from .balance import BalanceHandler
from .withdraw import WithdrawHandler
from .referral import ReferralHandler
from .giftcode import GiftCodeHandler
from .tasks import TasksHandler
from .ads import AdsHandler
from .wheel import WheelHandler
from .admin import AdminHandler
from .ads_posting import AdsPostingHandler

# قائمة بجميع المعالجات لسهولة التصدير
__all__ = [
    'StartHandler',
    'BalanceHandler', 
    'WithdrawHandler',
    'ReferralHandler',
    'GiftCodeHandler',
    'TasksHandler',
    'AdsHandler',
    'WheelHandler',
    'AdminHandler',
    'AdsPostingHandler'
]

# معلومات عن الإصدار
__version__ = '1.0.0'
__author__ = 'RockyTap Team'