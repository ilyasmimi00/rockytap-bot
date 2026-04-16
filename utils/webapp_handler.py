# utils/webapp_handler.py
"""
معالج البيانات الواردة من WebApp
"""

import json
import logging
from config import POINTS_TO_TON_RATE

logger = logging.getLogger(__name__)


async def handle_webapp_data(bot, update, context):
    """معالجة البيانات المرسلة من صفحات HTML"""
    try:
        data = json.loads(update.effective_message.web_app_data.data)
        user_id = update.effective_user.id
        action = data.get('action')
        
        logger.info(f"📱 WebApp data received: {action} from user {user_id}")
        
        # ========== معالجة السحب ==========
        if action == 'withdraw':
            amount = float(data.get('amount', 0))
            wallet_address = data.get('wallet_address', '')
            
            result, msg = bot.db.create_withdrawal(
                user_id=user_id,
                username=update.effective_user.username,
                amount=amount,
                wallet_address=wallet_address
            )
            
            await update.message.reply_text(
                f"✅ تم إرسال طلب السحب بنجاح!\n"
                f"💰 المبلغ: {amount:.4f} TON\n"
                f"📋 رقم الطلب: #{msg}\n\n"
                f"سيتم مراجعة طلبك من قبل الإدارة."
            )
        
        # ========== معالجة الإحالات ==========
        elif action == 'referral':
            # عرض رابط الإحالة
            bot_username = (await bot.application.bot.get_me()).username
            link = f"https://t.me/{bot_username}?start=ref_{user_id}"
            
            await update.message.reply_text(
                f"🔗 رابط الإحالة الخاص بك:\n"
                f"<code>{link}</code>\n\n"
                f"👥 عدد المدعوين: {len(bot.db.get_user_referrals(user_id))}\n\n"
                f"شارك الرابط مع أصدقائك لتحصل على مكافآت!"
            )
        
        # ========== معالجة الأكواد ==========
        elif action == 'redeem_code':
            code = data.get('code', '').upper()
            
            success, result = bot.db.use_gift_code(user_id, code)
            
            if success:
                await update.message.reply_text(
                    f"✅ تم تفعيل الكود بنجاح!\n"
                    f"🎁 حصلت على: {result['reward_points']} نقطة + {result['reward_ton']:.4f} تون"
                )
            else:
                await update.message.reply_text(f"❌ {result}")
        
        # ========== معالجة تحويل النقاط ==========
        elif action == 'convert_points':
            points = float(data.get('points', 0))
            
            success, msg = bot.db.convert_points_to_ton(user_id, points)
            
            if success:
                user = bot.db.get_user(user_id)
                await update.message.reply_text(
                    f"✅ {msg}\n"
                    f"💰 رصيد التون الحالي: {user['balance_ton']:.4f} TON\n"
                    f"⭐ رصيد النقاط الحالي: {user['balance_points']:.0f} نقطة"
                )
            else:
                await update.message.reply_text(f"❌ {msg}")
        
        # ========== معالجة غير معروفة ==========
        else:
            logger.warning(f"⚠️ Unknown action: {action}")
            await update.message.reply_text("⚠️ إجراء غير معروف")
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        await update.message.reply_text("❌ خطأ في قراءة البيانات")
    except Exception as e:
        logger.error(f"Error handling webapp data: {e}")
        await update.message.reply_text("❌ حدث خطأ")