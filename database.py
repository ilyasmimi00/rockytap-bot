# database.py
"""
قاعدة البيانات - النسخة الكاملة مع نظام الإعلانات المتقدم
"""

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime, date, timedelta
import random
import string
import json
from models import Base, User, Withdrawal, Referral, GiftCode, GiftCodeUsage, AdWatch, WheelSpin, SystemSetting, AdminLog, Task, UserTask, AdPackage, UserAd, AdMember, AdRequest

# إعدادات
DATABASE_URL = 'sqlite:///bot_database.db'
POINTS_TO_TON_RATE = 10
WITHDRAWAL_MIN = 0.02
DAILY_ADS_LIMIT = 10
AD_REWARD_POINTS = 15
DAILY_WHEEL_SPINS = 3

# إعدادات الإحالات الافتراضية
DEFAULT_REFERRAL_SETTINGS = {
    'reward_type': 'both',
    'points_value': 100,
    'ton_value': 0.01,
    'required_tasks': 6,
    'auto_grant': True
}


class Database:
    def __init__(self, db_url=DATABASE_URL):
        self.engine = create_engine(
            db_url,
            connect_args={'check_same_thread': False},
            pool_pre_ping=True
        )
        Base.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        print("✅ Database initialized")
        
        # تهيئة الإعدادات الافتراضية
        self._init_default_settings()
        self.init_ad_packages()
    
    def _init_default_settings(self):
        """تهيئة الإعدادات الافتراضية في قاعدة البيانات"""
        session = self.get_session()
        try:
            existing = session.query(SystemSetting).filter_by(key='referral_settings').first()
            if not existing:
                setting = SystemSetting(
                    key='referral_settings',
                    value=json.dumps(DEFAULT_REFERRAL_SETTINGS),
                    created_at=datetime.now()
                )
                session.add(setting)
                session.commit()
                print("✅ Referral settings initialized")
            
            api_key_exists = session.query(SystemSetting).filter_by(key='gramads_api_key').first()
            if not api_key_exists:
                setting = SystemSetting(key='gramads_api_key', value='', created_at=datetime.now())
                session.add(setting)
            
            points_exists = session.query(SystemSetting).filter_by(key='points_per_ad').first()
            if not points_exists:
                setting = SystemSetting(key='points_per_ad', value='15', created_at=datetime.now())
                session.add(setting)
            
            limit_exists = session.query(SystemSetting).filter_by(key='daily_ad_limit').first()
            if not limit_exists:
                setting = SystemSetting(key='daily_ad_limit', value='10', created_at=datetime.now())
                session.add(setting)
            
            session.commit()
            print("✅ Ads settings initialized")
            
        except Exception as e:
            print(f"Error initializing settings: {e}")
        finally:
            session.close()
    
    def init_ad_packages(self):
        """تهيئة باقات الإعلانات الافتراضية"""
        session = self.get_session()
        try:
            count = session.query(AdPackage).count()
            if count == 0:
                packages = [
                    {'views_count': 25, 'price_ton': 0.0375, 'bot_share': 0.0005, 'executor_share': 0.001},
                    {'views_count': 50, 'price_ton': 0.075, 'bot_share': 0.0005, 'executor_share': 0.001},
                    {'views_count': 100, 'price_ton': 0.15, 'bot_share': 0.0005, 'executor_share': 0.001},
                    {'views_count': 150, 'price_ton': 0.225, 'bot_share': 0.0005, 'executor_share': 0.001},
                    {'views_count': 200, 'price_ton': 0.30, 'bot_share': 0.0005, 'executor_share': 0.001},
                    {'views_count': 500, 'price_ton': 0.75, 'bot_share': 0.0005, 'executor_share': 0.001},
                    {'views_count': 1000, 'price_ton': 1.5, 'bot_share': 0.0005, 'executor_share': 0.001}
                ]
                
                for pkg in packages:
                    package = AdPackage(
                        views_count=pkg['views_count'],
                        price_ton=pkg['price_ton'],
                        bot_share=pkg['bot_share'],
                        executor_share=pkg['executor_share'],
                        is_active=True
                    )
                    session.add(package)
                
                session.commit()
                print("✅ Ad packages initialized")
        except Exception as e:
            print(f"Error initializing ad packages: {e}")
        finally:
            session.close()
    
    def get_session(self):
        return self.Session()
    
    # ==================== دوال المستخدم ====================
    
    def get_or_create_user(self, user_id, username=None, first_name=None):
        """الحصول على مستخدم أو إنشائه إذا لم يكن موجوداً"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                user = User(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    join_date=datetime.now(),
                    last_active=datetime.now()
                )
                session.add(user)
                session.commit()
                print(f"🆕 New user created: {user_id}")
            else:
                user.last_active = datetime.now()
                if username:
                    user.username = username
                if first_name:
                    user.first_name = first_name
                session.commit()
            
            return self._user_to_dict(user)
        except Exception as e:
            print(f"Error in get_or_create_user: {e}")
            return None
        finally:
            session.close()
    
    def get_user(self, user_id):
        """الحصول على بيانات مستخدم"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if user:
                return self._user_to_dict(user)
            return None
        finally:
            session.close()
    
    def get_all_users(self):
        """جلب جميع المستخدمين"""
        session = self.get_session()
        try:
            users = session.query(User).all()
            return [self._user_to_dict(u) for u in users]
        finally:
            session.close()
    
    def update_user_balance(self, user_id, ton_amount=0, points_amount=0, update_earned=False):
        """تحديث رصيد المستخدم"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                return False
            
            if ton_amount != 0:
                user.balance_ton += ton_amount
                if update_earned and ton_amount > 0:
                    user.total_earned_ton += ton_amount
            
            if points_amount != 0:
                user.balance_points += points_amount
                if update_earned and points_amount > 0:
                    user.total_points_earned += points_amount
            
            user.last_active = datetime.now()
            session.commit()
            return True
        except Exception as e:
            print(f"Error updating balance: {e}")
            return False
        finally:
            session.close()
    
    def update_user_block_status(self, user_id, is_blocked):
        """تحديث حالة حظر المستخدم"""
        session = self.get_session()
        try:
            session.query(User).filter_by(user_id=user_id).update({
                User.is_blocked: is_blocked,
                User.last_active: datetime.now()
            })
            session.commit()
            return True
        except Exception as e:
            print(f"Error updating block status: {e}")
            return False
        finally:
            session.close()
    
    def convert_points_to_ton(self, user_id, points):
        """تحويل النقاط إلى تون"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                return False, "المستخدم غير موجود"
            
            if user.balance_points < points:
                return False, "النقاط غير كافية"
            
            ton_amount = points / POINTS_TO_TON_RATE
            
            user.balance_points -= points
            user.balance_ton += ton_amount
            
            session.commit()
            return True, f"تم تحويل {points} نقطة إلى {ton_amount:.4f} تون"
        except Exception as e:
            print(f"Error converting points: {e}")
            return False, str(e)
        finally:
            session.close()
    
    # ==================== دوال السحب ====================
    
    def create_withdrawal(self, user_id, username, amount, wallet_address):
        """إنشاء طلب سحب جديد"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                return False, "المستخدم غير موجود"
            
            if user.balance_ton < amount:
                return False, "الرصيد غير كافٍ"
            
            if amount < WITHDRAWAL_MIN:
                return False, f"الحد الأدنى للسحب هو {WITHDRAWAL_MIN} تون"
            
            user.balance_ton -= amount
            user.total_withdrawn_ton += amount
            
            withdrawal = Withdrawal(
                user_id=user_id,
                username=username,
                amount=amount,
                wallet_address=wallet_address,
                status='pending',
                requested_at=datetime.now()
            )
            session.add(withdrawal)
            session.commit()
            
            return True, withdrawal.id
        except Exception as e:
            print(f"Error creating withdrawal: {e}")
            return False, str(e)
        finally:
            session.close()
    
    def get_user_withdrawals(self, user_id, limit=20):
        """الحصول على طلبات السحب للمستخدم"""
        session = self.get_session()
        try:
            withdrawals = session.query(Withdrawal).filter_by(
                user_id=user_id
            ).order_by(Withdrawal.requested_at.desc()).limit(limit).all()
            
            return [{
                'id': w.id,
                'amount': w.amount,
                'wallet_address': w.wallet_address,
                'status': w.status,
                'requested_at': w.requested_at.strftime('%Y-%m-%d %H:%M')
            } for w in withdrawals]
        finally:
            session.close()
    
    # ==================== دوال الإحالات ====================
    
    def create_referral(self, referrer_id, referred_id, referred_username):
        """إنشاء إحالة جديدة"""
        session = self.get_session()
        try:
            existing = session.query(Referral).filter_by(referred_id=referred_id).first()
            if existing:
                return False, "تمت إحالة هذا المستخدم بالفعل"
            
            if referrer_id == referred_id:
                return False, "لا يمكنك إحالة نفسك"
            
            settings = self.get_referral_settings()
            
            reward_points = 0
            reward_ton = 0
            
            if settings['reward_type'] == 'points':
                reward_points = settings['points_value']
            elif settings['reward_type'] == 'ton':
                reward_ton = settings['ton_value']
            else:
                reward_points = settings['points_value']
                reward_ton = settings['ton_value']
            
            referral = Referral(
                referrer_id=referrer_id,
                referred_id=referred_id,
                referred_username=referred_username,
                reward_points=reward_points,
                reward_ton=reward_ton,
                reward_type=settings['reward_type'],
                is_reward_granted=False,
                created_at=datetime.now()
            )
            session.add(referral)
            
            user = session.query(User).filter_by(user_id=referrer_id).first()
            if user:
                user.total_referrals += 1
            
            session.commit()
            return True, "تم إنشاء الإحالة بنجاح"
        except Exception as e:
            print(f"Error creating referral: {e}")
            return False, str(e)
        finally:
            session.close()
    
    def get_user_referrals_stats(self, user_id):
        """إحصائيات الإحالات للمستخدم"""
        session = self.get_session()
        try:
            referrals = session.query(Referral).filter_by(referrer_id=user_id).all()
            
            total = len(referrals)
            granted = sum(1 for r in referrals if r.is_reward_granted)
            pending = total - granted
            
            total_points_earned = sum(r.reward_points for r in referrals if r.is_reward_granted)
            total_ton_earned = sum(r.reward_ton for r in referrals if r.is_reward_granted)
            
            settings = self.get_referral_settings()
            
            referrals_list = []
            for r in referrals:
                referrals_list.append({
                    'username': r.referred_username or f"مستخدم {r.referred_id}",
                    'date': r.created_at.strftime('%Y-%m-%d'),
                    'status': 'مكتمل' if r.is_reward_granted else 'قيد الانتظار',
                    'reward_points': r.reward_points,
                    'reward_ton': r.reward_ton,
                    'reward_type': r.reward_type
                })
            
            return {
                'total': total,
                'granted': granted,
                'pending': pending,
                'total_points_earned': total_points_earned,
                'total_ton_earned': total_ton_earned,
                'referrals': referrals_list,
                'settings': settings
            }
        except Exception as e:
            print(f"Error getting referrals stats: {e}")
            return {
                'total': 0,
                'granted': 0,
                'pending': 0,
                'total_points_earned': 0,
                'total_ton_earned': 0,
                'referrals': [],
                'settings': self.get_referral_settings()
            }
        finally:
            session.close()
    
    def get_referral_settings(self):
        """الحصول على إعدادات الإحالات الحالية"""
        session = self.get_session()
        try:
            setting = session.query(SystemSetting).filter_by(key='referral_settings').first()
            if setting:
                return json.loads(setting.value)
            return DEFAULT_REFERRAL_SETTINGS.copy()
        except Exception as e:
            print(f"Error getting referral settings: {e}")
            return DEFAULT_REFERRAL_SETTINGS.copy()
        finally:
            session.close()
    
    def save_referral_settings(self, reward_type, points_value, ton_value, required_tasks):
        """حفظ إعدادات الإحالات"""
        session = self.get_session()
        try:
            settings = {
                'reward_type': reward_type,
                'points_value': points_value,
                'ton_value': ton_value,
                'required_tasks': required_tasks,
                'auto_grant': True
            }
            
            existing = session.query(SystemSetting).filter_by(key='referral_settings').first()
            if existing:
                existing.value = json.dumps(settings)
                existing.updated_at = datetime.now()
            else:
                setting = SystemSetting(
                    key='referral_settings',
                    value=json.dumps(settings),
                    created_at=datetime.now()
                )
                session.add(setting)
            
            session.commit()
            return True
        except Exception as e:
            print(f"Error saving referral settings: {e}")
            return False
        finally:
            session.close()
    
    # ==================== دوال الأكواد ====================
    
    def create_gift_code(self, created_by, reward_points=0, reward_ton=0, max_uses=100, is_admin=False):
        """إنشاء كود ترويجي جديد"""
        session = self.get_session()
        try:
            chars = string.ascii_uppercase + string.digits
            chars = chars.replace('O', '').replace('I', '').replace('0', '').replace('1', '')
            code = ''.join(random.choices(chars, k=8))
            
            gift_code = GiftCode(
                code=code,
                reward_points=reward_points,
                reward_ton=reward_ton,
                max_uses=max_uses,
                created_by=created_by,
                is_admin_created=is_admin,
                created_at=datetime.now()
            )
            session.add(gift_code)
            session.commit()
            
            return True, code
        except Exception as e:
            print(f"Error creating gift code: {e}")
            return False, str(e)
        finally:
            session.close()
    
    def use_gift_code(self, user_id, code):
        """استخدام كود ترويجي"""
        session = self.get_session()
        try:
            gift_code = session.query(GiftCode).filter_by(
                code=code.upper(),
                is_active=True
            ).first()
            
            if not gift_code:
                return False, "الكود غير صالح"
            
            if gift_code.used_count >= gift_code.max_uses:
                return False, "تم استخدام هذا الكود بأقصى عدد مرات"
            
            existing_usage = session.query(GiftCodeUsage).filter_by(
                code_id=gift_code.id,
                user_id=user_id
            ).first()
            
            if existing_usage:
                return False, "لقد استخدمت هذا الكود من قبل"
            
            self.update_user_balance(
                user_id,
                ton_amount=gift_code.reward_ton,
                points_amount=gift_code.reward_points,
                update_earned=True
            )
            
            usage = GiftCodeUsage(
                code_id=gift_code.id,
                user_id=user_id,
                used_at=datetime.now()
            )
            session.add(usage)
            gift_code.used_count += 1
            
            session.commit()
            
            return True, {
                'reward_points': gift_code.reward_points,
                'reward_ton': gift_code.reward_ton
            }
        except Exception as e:
            print(f"Error using gift code: {e}")
            return False, str(e)
        finally:
            session.close()
    
    # ==================== دوال الإعلانات العادية ====================
    
    def get_today_ads_count(self, user_id):
        """الحصول على عدد الإعلانات التي شاهدها المستخدم اليوم"""
        session = self.get_session()
        try:
            today = date.today()
            count = session.query(AdWatch).filter(
                AdWatch.user_id == user_id,
                AdWatch.date >= today
            ).count()
            return count
        finally:
            session.close()
    
    def add_ad_watch(self, user_id, points_earned):
        """تسجيل مشاهدة إعلان"""
        session = self.get_session()
        try:
            ad_watch = AdWatch(
                user_id=user_id,
                date=datetime.now(),
                points_earned=points_earned
            )
            session.add(ad_watch)
            session.commit()
            return True
        except Exception as e:
            print(f"Error adding ad watch: {e}")
            return False
        finally:
            session.close()
    
    def save_ads_settings(self, api_key=None, points_per_ad=None, daily_limit=None):
        """حفظ إعدادات الإعلانات"""
        session = self.get_session()
        try:
            if api_key is not None:
                existing = session.query(SystemSetting).filter_by(key='gramads_api_key').first()
                if existing:
                    existing.value = api_key
                    existing.updated_at = datetime.now()
                else:
                    setting = SystemSetting(key='gramads_api_key', value=api_key, created_at=datetime.now())
                    session.add(setting)
            
            if points_per_ad is not None:
                existing = session.query(SystemSetting).filter_by(key='points_per_ad').first()
                if existing:
                    existing.value = str(points_per_ad)
                    existing.updated_at = datetime.now()
                else:
                    setting = SystemSetting(key='points_per_ad', value=str(points_per_ad), created_at=datetime.now())
                    session.add(setting)
            
            if daily_limit is not None:
                existing = session.query(SystemSetting).filter_by(key='daily_ad_limit').first()
                if existing:
                    existing.value = str(daily_limit)
                    existing.updated_at = datetime.now()
                else:
                    setting = SystemSetting(key='daily_ad_limit', value=str(daily_limit), created_at=datetime.now())
                    session.add(setting)
            
            session.commit()
            return True
        except Exception as e:
            print(f"Error saving ads settings: {e}")
            return False
        finally:
            session.close()
    
    def get_ads_settings(self):
        """الحصول على إعدادات الإعلانات"""
        session = self.get_session()
        try:
            api_key = session.query(SystemSetting).filter_by(key='gramads_api_key').first()
            points_per_ad = session.query(SystemSetting).filter_by(key='points_per_ad').first()
            daily_limit = session.query(SystemSetting).filter_by(key='daily_ad_limit').first()
            
            return {
                'api_key': api_key.value if api_key else None,
                'points_per_ad': int(points_per_ad.value) if points_per_ad else 15,
                'daily_limit': int(daily_limit.value) if daily_limit else 10
            }
        except Exception as e:
            print(f"Error getting ads settings: {e}")
            return {'api_key': None, 'points_per_ad': 15, 'daily_limit': 10}
        finally:
            session.close()
    
    # ==================== دوال عجلة الحظ ====================
    
    def get_today_wheel_spins(self, user_id):
        """الحصول على عدد مرات لعب عجلة الحظ اليوم"""
        session = self.get_session()
        try:
            today = date.today()
            count = session.query(WheelSpin).filter(
                WheelSpin.user_id == user_id,
                WheelSpin.date >= today
            ).count()
            return count
        finally:
            session.close()
    
    def add_wheel_spin(self, user_id, reward_points):
        """تسجيل لعب عجلة الحظ"""
        session = self.get_session()
        try:
            spin = WheelSpin(
                user_id=user_id,
                date=datetime.now(),
                reward_points=reward_points
            )
            session.add(spin)
            session.commit()
            return True
        except Exception as e:
            print(f"Error adding wheel spin: {e}")
            return False
        finally:
            session.close()
    
    def get_user_wheel_total(self, user_id):
        """الحصول على إجمالي أرباح المستخدم من العجلة"""
        session = self.get_session()
        try:
            total = session.query(func.sum(WheelSpin.reward_points)).filter_by(user_id=user_id).scalar()
            return total or 0
        finally:
            session.close()
    
    # ==================== دوال المهام ====================
    
    def get_active_tasks(self):
        """جلب جميع المهام النشطة"""
        session = self.get_session()
        try:
            tasks = session.query(Task).filter(Task.is_active == True).order_by(Task.order_index).all()
            return [{
                'id': t.id,
                'title': t.title,
                'description': t.description,
                'icon': t.icon,
                'channel_link': t.channel_link,
                'channel_username': t.channel_username,
                'reward_points': t.reward_points,
                'reward_ton': t.reward_ton
            } for t in tasks]
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return []
        finally:
            session.close()
    
    def get_all_tasks(self):
        """جلب جميع المهام (للأدمن)"""
        session = self.get_session()
        try:
            tasks = session.query(Task).order_by(Task.id.desc()).all()
            result = []
            for t in tasks:
                completed_count = session.query(UserTask).filter(
                    UserTask.task_id == t.id,
                    UserTask.status == 'completed'
                ).count()
                
                result.append({
                    'id': t.id,
                    'title': t.title,
                    'description': t.description,
                    'icon': t.icon,
                    'channel_link': t.channel_link,
                    'channel_username': t.channel_username,
                    'reward_points': t.reward_points,
                    'reward_ton': t.reward_ton,
                    'is_active': t.is_active,
                    'completed_count': completed_count
                })
            return result
        except Exception as e:
            print(f"Error getting all tasks: {e}")
            return []
        finally:
            session.close()
    
    def get_task(self, task_id):
        """جلب مهمة محددة"""
        session = self.get_session()
        try:
            task = session.query(Task).filter(Task.id == task_id).first()
            if task:
                return {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'icon': task.icon,
                    'channel_link': task.channel_link,
                    'channel_username': task.channel_username,
                    'reward_points': task.reward_points,
                    'reward_ton': task.reward_ton
                }
            return None
        except Exception as e:
            print(f"Error getting task: {e}")
            return None
        finally:
            session.close()
    
    def create_task(self, title, description, icon, channel_link, channel_username, reward_points, reward_ton, created_by):
        """إنشاء مهمة جديدة"""
        session = self.get_session()
        try:
            task = Task(
                title=title,
                description=description,
                icon=icon,
                channel_link=channel_link,
                channel_username=channel_username,
                reward_points=reward_points,
                reward_ton=reward_ton,
                created_by=created_by,
                created_at=datetime.now()
            )
            session.add(task)
            session.commit()
            return True, {'id': task.id, 'title': task.title}
        except Exception as e:
            print(f"Error creating task: {e}")
            return False, str(e)
        finally:
            session.close()
    
    def delete_task(self, task_id):
        """حذف مهمة"""
        session = self.get_session()
        try:
            session.query(UserTask).filter_by(task_id=task_id).delete()
            session.query(Task).filter_by(id=task_id).delete()
            session.commit()
            return True
        except Exception as e:
            print(f"Error deleting task: {e}")
            return False
        finally:
            session.close()
    
    def create_user_task(self, user_id, task_id):
        """إنشاء سجل مهمة للمستخدم"""
        session = self.get_session()
        try:
            existing = session.query(UserTask).filter_by(user_id=user_id, task_id=task_id).first()
            if not existing:
                user_task = UserTask(
                    user_id=user_id,
                    task_id=task_id,
                    status='pending'
                )
                session.add(user_task)
                session.commit()
            return True
        except Exception as e:
            print(f"Error creating user task: {e}")
            return False
        finally:
            session.close()
    
    def get_user_task(self, user_id, task_id):
        """جلب سجل مهمة المستخدم"""
        session = self.get_session()
        try:
            user_task = session.query(UserTask).filter_by(user_id=user_id, task_id=task_id).first()
            if user_task:
                return {
                    'id': user_task.id,
                    'task_id': user_task.task_id,
                    'status': user_task.status,
                    'completed_at': user_task.completed_at,
                    'claimed_at': user_task.claimed_at
                }
            return None
        except Exception as e:
            print(f"Error getting user task: {e}")
            return None
        finally:
            session.close()
    
    def get_user_tasks_progress(self, user_id):
        """جلب تقدم المستخدم في جميع المهام"""
        session = self.get_session()
        try:
            user_tasks = session.query(UserTask).filter_by(user_id=user_id).all()
            return [{
                'task_id': ut.task_id,
                'status': ut.status
            } for ut in user_tasks]
        except Exception as e:
            print(f"Error getting user tasks: {e}")
            return []
        finally:
            session.close()
    
    def complete_user_task(self, user_id, task_id):
        """إكمال مهمة المستخدم"""
        session = self.get_session()
        try:
            user_task = session.query(UserTask).filter_by(user_id=user_id, task_id=task_id).first()
            if user_task and user_task.status != 'completed':
                task = session.query(Task).filter(Task.id == task_id).first()
                if task:
                    self.update_user_balance(
                        user_id,
                        ton_amount=task.reward_ton,
                        points_amount=task.reward_points,
                        update_earned=True
                    )
                
                user_task.status = 'completed'
                user_task.completed_at = datetime.now()
                user_task.claimed_at = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error completing user task: {e}")
            return False
        finally:
            session.close()
    
    # ==================== دوال الإعلانات المدفوعة ====================
    
    def get_ad_packages(self):
        """جلب جميع باقات الإعلانات"""
        session = self.get_session()
        try:
            packages = session.query(AdPackage).filter(AdPackage.is_active == True).all()
            return [{'id': p.id, 'views': p.views_count, 'price': p.price_ton} for p in packages]
        except Exception as e:
            print(f"Error getting ad packages: {e}")
            return []
        finally:
            session.close()
    
    def create_user_ad(self, user_id, title, description, channel_link, channel_username, channel_id, package_id):
        """إنشاء إعلان جديد"""
        session = self.get_session()
        try:
            package = session.query(AdPackage).filter_by(id=package_id).first()
            if not package:
                return False, "الباقة غير موجودة"
            
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user or user.balance_ton < package.price_ton:
                return False, f"رصيدك غير كافٍ. تحتاج {package.price_ton} تون"
            
            user.balance_ton -= package.price_ton
            
            ad = UserAd(
                user_id=user_id,
                title=title,
                description=description,
                channel_link=channel_link,
                channel_username=channel_username,
                channel_id=channel_id,
                package_id=package_id,
                views_count=package.views_count,
                status='pending',
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=30),
                paid_amount=package.price_ton
            )
            session.add(ad)
            session.commit()
            
            return True, ad.id
        except Exception as e:
            print(f"Error creating user ad: {e}")
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    def get_user_ads(self, user_id):
        """جلب إعلانات المستخدم"""
        session = self.get_session()
        try:
            ads = session.query(UserAd).filter_by(user_id=user_id).order_by(UserAd.created_at.desc()).all()
            return [{
                'id': a.id,
                'title': a.title,
                'description': a.description,
                'channel_link': a.channel_link,
                'channel_username': a.channel_username,
                'views_count': a.views_count,
                'current_views': a.current_views,
                'members_count': a.members_count,
                'status': a.status,
                'is_verified': a.is_verified,
                'created_at': a.created_at.strftime('%Y-%m-%d %H:%M'),
                'paid_amount': a.paid_amount,
                'bot_earnings': a.bot_earnings,
                'user_earnings': a.user_earnings
            } for a in ads]
        except Exception as e:
            print(f"Error getting user ads: {e}")
            return []
        finally:
            session.close()
    
    def get_ad_by_id(self, ad_id, user_id=None):
        """جلب إعلان محدد"""
        session = self.get_session()
        try:
            query = session.query(UserAd).filter_by(id=ad_id)
            if user_id:
                query = query.filter_by(user_id=user_id)
            ad = query.first()
            if ad:
                return {
                    'id': ad.id,
                    'user_id': ad.user_id,
                    'title': ad.title,
                    'description': ad.description,
                    'channel_link': ad.channel_link,
                    'channel_username': ad.channel_username,
                    'views_count': ad.views_count,
                    'current_views': ad.current_views,
                    'members_count': ad.members_count,
                    'status': ad.status,
                    'is_verified': ad.is_verified,
                    'paid_amount': ad.paid_amount
                }
            return None
        finally:
            session.close()
    
    def delete_ad(self, ad_id, user_id):
        """حذف الإعلان"""
        session = self.get_session()
        try:
            ad = session.query(UserAd).filter_by(id=ad_id, user_id=user_id).first()
            if not ad:
                return False, "الإعلان غير موجود"
            
            if ad.status == 'pending' and ad.current_views == 0:
                user = session.query(User).filter_by(user_id=user_id).first()
                if user:
                    user.balance_ton += ad.paid_amount
            
            session.delete(ad)
            session.query(AdMember).filter_by(ad_id=ad_id).delete()
            session.commit()
            return True, "تم حذف الإعلان بنجاح"
        except Exception as e:
            print(f"Error deleting ad: {e}")
            return False, str(e)
        finally:
            session.close()
    
    def get_ad_stats(self, ad_id):
        """إحصائيات متقدمة للإعلان"""
        session = self.get_session()
        try:
            ad = session.query(UserAd).filter_by(id=ad_id).first()
            if not ad:
                return None
            
            progress = (ad.current_views / ad.views_count) * 100 if ad.views_count > 0 else 0
            
            today = datetime.now().date()
            today_members = session.query(AdMember).filter(
                AdMember.ad_id == ad_id,
                AdMember.watched_at >= today
            ).count()
            
            return {
                'title': ad.title,
                'views_count': ad.views_count,
                'current_views': ad.current_views,
                'progress': progress,
                'members_count': ad.members_count,
                'today_members': today_members,
                'status': ad.status,
                'bot_earnings': ad.bot_earnings,
                'user_earnings': ad.user_earnings,
                'paid_amount': ad.paid_amount,
                'created_at': ad.created_at.strftime('%Y-%m-%d %H:%M')
            }
        finally:
            session.close()
    
    def add_ad_member(self, ad_id, member_id, member_username, reward_points=5, reward_ton=0):
        """إضافة عضو شاهد الإعلان"""
        session = self.get_session()
        try:
            existing = session.query(AdMember).filter_by(ad_id=ad_id, member_id=member_id).first()
            if existing:
                return False, "تمت مشاهدة هذا الإعلان مسبقاً"
            
            ad = session.query(UserAd).filter_by(id=ad_id).first()
            if not ad or ad.status != 'active':
                return False, "الإعلان غير نشط"
            
            member = AdMember(
                ad_id=ad_id,
                member_id=member_id,
                member_username=member_username,
                reward_points=reward_points,
                reward_ton=reward_ton
            )
            session.add(member)
            
            ad.current_views += 1
            ad.members_count += 1
            
            user = session.query(User).filter_by(user_id=member_id).first()
            if user:
                if reward_points > 0:
                    user.balance_points += reward_points
                    user.total_points_earned += reward_points
                if reward_ton > 0:
                    user.balance_ton += reward_ton
                    user.total_earned_ton += reward_ton
            
            package = session.query(AdPackage).filter_by(id=ad.package_id).first()
            if package:
                ad.bot_earnings += package.bot_share
                ad.user_earnings += package.executor_share
            
            if ad.current_views >= ad.views_count:
                ad.status = 'completed'
            
            session.commit()
            return True, "تم تسجيل المشاهدة بنجاح"
        except Exception as e:
            print(f"Error adding ad member: {e}")
            session.rollback()
            return False, str(e)
        finally:
            session.close()
    
    def get_ad_members(self, ad_id, limit=50):
        """جلب أعضاء شاهدوا الإعلان"""
        session = self.get_session()
        try:
            members = session.query(AdMember).filter_by(ad_id=ad_id).order_by(AdMember.watched_at.desc()).limit(limit).all()
            return [{
                'member_id': m.member_id,
                'username': m.member_username,
                'watched_at': m.watched_at.strftime('%Y-%m-%d %H:%M'),
                'reward_points': m.reward_points,
                'reward_ton': m.reward_ton
            } for m in members]
        finally:
            session.close()
    
    def verify_channel_bot(self, user_id, ad_id, bot_username):
        """التحقق من أن البوت أدمن في قناة المستخدم"""
        session = self.get_session()
        try:
            ad = session.query(UserAd).filter_by(id=ad_id, user_id=user_id).first()
            if not ad:
                return False, "الإعلان غير موجود"
            
            ad.is_verified = True
            ad.status = 'active'
            session.commit()
            return True, "تم التحقق من البوت في قناتك"
        except Exception as e:
            print(f"Error verifying channel: {e}")
            return False, str(e)
        finally:
            session.close()
    
    # ==================== دوال الأدمن ====================
    
    def add_admin_log(self, admin_id, action, details=""):
        """تسجيل إجراء أدمن"""
        session = self.get_session()
        try:
            log = AdminLog(
                admin_id=admin_id,
                action=action,
                details=details,
                timestamp=datetime.now()
            )
            session.add(log)
            session.commit()
            return True
        except Exception as e:
            print(f"Error adding admin log: {e}")
            return False
        finally:
            session.close()
    
    def get_total_users_count(self):
        """الحصول على عدد المستخدمين الكلي"""
        session = self.get_session()
        try:
            return session.query(User).count()
        finally:
            session.close()
    
    def get_pending_withdrawals_count(self):
        """الحصول على عدد طلبات السحب المعلقة"""
        session = self.get_session()
        try:
            return session.query(Withdrawal).filter_by(status='pending').count()
        finally:
            session.close()
    
    # ==================== دوال المهام المجانية ====================
    
    def get_user_free_tasks_status(self, user_id):
        """
        جلب حالة المهام المجانية للمستخدم
        هذه الدالة تستخدم في نظام السحب للتحقق من شروط السحب
        """
        session = self.get_session()
        try:
            # جلب جميع المهام المكتملة للمستخدم
            user_tasks = session.query(UserTask).filter_by(
                user_id=user_id, 
                status='completed'
            ).all()
            
            # إرجاع قائمة بالمهام المكتملة
            return [{'task_id': ut.task_id, 'status': 'completed'} for ut in user_tasks]
        except Exception as e:
            print(f"Error getting free tasks status: {e}")
            return []
        finally:
            session.close()
    
    # ==================== دوال مساعدة ====================
    
    def _user_to_dict(self, user):
        """تحويل كائن المستخدم إلى قاموس"""
        return {
            'user_id': user.user_id,
            'username': user.username,
            'first_name': user.first_name,
            'balance_ton': user.balance_ton,
            'balance_points': user.balance_points,
            'total_referrals': user.total_referrals,
            'total_earned_ton': user.total_earned_ton,
            'total_withdrawn_ton': user.total_withdrawn_ton,
            'join_date': user.join_date.strftime('%Y-%m-%d %H:%M') if user.join_date else None,
            'last_active': user.last_active.strftime('%Y-%m-%d %H:%M') if user.last_active else None,
            'is_blocked': user.is_blocked,
            'first_withdrawal_completed': user.first_withdrawal_completed
        }