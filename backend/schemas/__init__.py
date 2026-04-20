# backend/schemas/__init__.py
"""
نماذج Pydantic للتحقق من صحة البيانات
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


# ==================== المستخدم (User) ====================

class UserResponse(BaseModel):
    """استجابة بيانات المستخدم"""
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    balance_ton: float
    balance_points: float
    total_referrals: int
    is_blocked: bool
    
    class Config:
        from_attributes = True


class UpdateBalanceRequest(BaseModel):
    """طلب تحديث الرصيد"""
    user_id: int
    ton_amount: float = 0
    points_amount: float = 0


class UserCreateRequest(BaseModel):
    """طلب إنشاء مستخدم"""
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None


# ==================== السحب (Withdrawal) ====================

class WithdrawRequest(BaseModel):
    """طلب سحب"""
    user_id: int
    amount: float = Field(ge=0.02, description="الحد الأدنى 0.02 تون")
    wallet_address: str = Field(min_length=10, description="عنوان المحفظة")
    username: Optional[str] = None


class WithdrawResponse(BaseModel):
    """استجابة طلب السحب"""
    success: bool
    withdrawal_id: Optional[int] = None
    message: str


class WithdrawalInfo(BaseModel):
    """معلومات طلب سحب"""
    id: int
    amount: float
    wallet_address: str
    status: str
    requested_at: str


# ==================== التحويل (Convert) ====================

class ConvertRequest(BaseModel):
    """طلب تحويل النقاط إلى تون"""
    user_id: int
    points: float = Field(ge=10, description="الحد الأدنى 10 نقاط")


class ConvertResponse(BaseModel):
    """استجابة تحويل النقاط"""
    success: bool
    message: str
    ton: Optional[float] = None
    points: Optional[float] = None


# ==================== الإعلانات العادية (Ads) ====================

class WatchAdRequest(BaseModel):
    """طلب مشاهدة إعلان"""
    user_id: int
    reward: int = Field(15, ge=1, le=100)


class AdInfo(BaseModel):
    """معلومات إعلان"""
    id: int
    name: str
    reward: int
    icon: str


class AdsListResponse(BaseModel):
    """استجابة قائمة الإعلانات"""
    success: bool
    ads: List[AdInfo]
    watched_today: int
    daily_limit: int


class WatchAdResponse(BaseModel):
    """استجابة مشاهدة إعلان"""
    success: bool
    reward: int
    new_points: float
    remaining: int
    message: Optional[str] = None


# ==================== عجلة الحظ (Wheel) ====================

class SpinWheelRequest(BaseModel):
    """طلب لعب عجلة الحظ"""
    user_id: int


class WheelStatusResponse(BaseModel):
    """استجابة حالة عجلة الحظ"""
    success: bool
    remaining_spins: int
    total_points: float


class SpinWheelResponse(BaseModel):
    """استجابة لعب عجلة الحظ"""
    success: bool
    reward: int
    new_points: float
    remaining: int
    message: Optional[str] = None


# ==================== المهام (Tasks) ====================

class TaskInfo(BaseModel):
    """معلومات مهمة"""
    id: int
    title: str
    description: Optional[str] = None
    icon: str
    channel_link: str
    channel_username: Optional[str] = None
    reward_points: float
    reward_ton: float
    user_status: str = "available"  # available, pending, completed


class TasksListResponse(BaseModel):
    """استجابة قائمة المهام"""
    success: bool
    tasks: List[TaskInfo]


class CompleteTaskRequest(BaseModel):
    """طلب إكمال مهمة"""
    user_id: int
    task_id: int


class CompleteTaskResponse(BaseModel):
    """استجابة إكمال مهمة"""
    success: bool
    message: str
    new_points: float
    new_ton: float


# ==================== الإحالات (Referrals) ====================

class ReferralInfo(BaseModel):
    """معلومات إحالة"""
    username: str
    date: str
    status: str
    reward_points: float
    reward_ton: float


class ReferralStatsResponse(BaseModel):
    """استجابة إحصائيات الإحالات"""
    success: bool
    total: int
    granted: int
    pending: int
    total_points_earned: float
    total_ton_earned: float
    referral_link: str
    referrals: List[ReferralInfo]


class CreateReferralRequest(BaseModel):
    """طلب إنشاء إحالة"""
    referrer_id: int
    referred_id: int
    referred_username: Optional[str] = None


# ==================== الأكواد الترويجية (Gift Codes) ====================

class RedeemCodeRequest(BaseModel):
    """طلب تفعيل كود"""
    user_id: int
    code: str = Field(min_length=4, max_length=20, description="الكود الترويجي")


class RedeemCodeResponse(BaseModel):
    """استجابة تفعيل كود"""
    success: bool
    message: str
    reward_points: Optional[float] = None
    reward_ton: Optional[float] = None
    new_points: Optional[float] = None
    new_ton: Optional[float] = None


class CreateCodeRequest(BaseModel):
    """طلب إنشاء كود (للمشرف)"""
    admin_id: int
    reward_points: float = 0
    reward_ton: float = 0
    max_uses: int = Field(100, ge=1, le=1000)


# ==================== الإعلانات المدفوعة (Paid Ads) ====================

class AdPackageInfo(BaseModel):
    """معلومات باقة إعلان"""
    id: int
    views: int
    price: float


class CreateUserAdRequest(BaseModel):
    """طلب إنشاء إعلان مدفوع"""
    user_id: int
    package_id: int
    title: str = Field(min_length=3, max_length=100)
    description: Optional[str] = None
    channel_link: str
    monitor_people: bool = False


class UserAdInfo(BaseModel):
    """معلومات إعلان المستخدم"""
    id: int
    title: str
    description: Optional[str]
    channel_link: str
    channel_username: Optional[str]
    views_count: int
    current_views: int
    members_count: int
    status: str  # pending, active, completed, rejected
    is_verified: bool
    created_at: str
    paid_amount: float


class VerifyAdChannelRequest(BaseModel):
    """طلب التحقق من البوت في القناة"""
    user_id: int
    ad_id: int


# ==================== الأدمن (Admin) ====================

class AdminActionResponse(BaseModel):
    """استجابة إجراء أدمن"""
    success: bool
    message: str


class UserBanRequest(BaseModel):
    """طلب حظر مستخدم"""
    admin_id: int
    user_id: int


class SystemSettingsResponse(BaseModel):
    """استجابة إعدادات النظام"""
    success: bool
    points_to_ton_rate: float
    withdrawal_min: float
    daily_ads_limit: int
    ad_reward_points: int
    daily_wheel_spins: int
    referral_settings: dict


class UpdateSystemSettingsRequest(BaseModel):
    """طلب تحديث إعدادات النظام"""
    admin_id: int
    points_to_ton_rate: Optional[float] = None
    withdrawal_min: Optional[float] = None
    daily_ads_limit: Optional[int] = None
    ad_reward_points: Optional[int] = None
    daily_wheel_spins: Optional[int] = None
    wheel_rewards: Optional[List[int]] = None
    referral_settings: Optional[dict] = None


# ==================== استجابات عامة ====================

class HealthResponse(BaseModel):
    """استجابة فحص الصحة"""
    status: str
    timestamp: str
    version: str = "2.0.0"


class ErrorResponse(BaseModel):
    """استجابة خطأ"""
    success: bool = False
    message: str
    detail: Optional[Any] = None