# api_local.py - خادم API محلي كامل لـ VPS

from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Database
from datetime import datetime
import random
import socket

app = Flask(__name__)
CORS(app)  # السماح بجميع الطلبات من أي مصدر

db = Database()

# معرفات الأدمن
ADMIN_IDS = [8268443100]

# ==================== واجهات API الأساسية ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/api/', methods=['GET'])
def api_root():
    return jsonify({'status': 'ok', 'message': 'API is running'})

@app.route('/api/user', methods=['GET'])
def get_user():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'user_id مطلوب'})
    
    try:
        user = db.get_user(int(user_id))
        if not user:
            return jsonify({'success': False, 'message': 'المستخدم غير موجود'})
        
        today_ads = db.get_today_ads_count(int(user_id))
        
        return jsonify({
            'success': True,
            'ton': user['balance_ton'],
            'points': user['balance_points'],
            'total_referrals': user['total_referrals'],
            'ads_watched': today_ads,
            'daily_limit': 10
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/user_ads', methods=['GET'])
def get_user_ads():
    """جلب إعلانات المستخدم"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'user_id مطلوب'})
    
    try:
        ads = db.get_user_ads(int(user_id))
        return jsonify({'success': True, 'ads': ads})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'ads': []})

@app.route('/api/create_ad', methods=['POST'])
def create_ad():
    """إنشاء إعلان جديد"""
    data = request.get_json()
    user_id = data.get('user_id')
    package_id = data.get('package_id')
    title = data.get('title')
    description = data.get('description', '')
    channel_link = data.get('channel_link')
    monitor_people = data.get('monitor_people', False)
    
    if not user_id or not package_id or not title or not channel_link:
        return jsonify({'success': False, 'message': 'بيانات ناقصة'})
    
    try:
        packages = db.get_ad_packages()
        package = next((p for p in packages if p['id'] == package_id), None)
        if not package:
            return jsonify({'success': False, 'message': 'الباقة غير موجودة'})
        
        user = db.get_user(int(user_id))
        if not user or user['balance_ton'] < package['price']:
            return jsonify({'success': False, 'message': f'رصيد غير كافٍ. تحتاج {package["price"]} تون'})
        
        db.update_user_balance(int(user_id), ton_amount=-package['price'])
        
        channel_username = channel_link
        if 't.me/' in channel_link:
            channel_username = '@' + channel_link.split('t.me/')[-1]
        
        success, ad_id = db.create_user_ad(
            user_id=int(user_id),
            title=title,
            description=description,
            channel_link=channel_link,
            channel_username=channel_username,
            channel_id=None,
            package_id=package_id
        )
        
        if success:
            return jsonify({'success': True, 'ad_id': ad_id, 'message': 'تم إنشاء الإعلان'})
        else:
            return jsonify({'success': False, 'message': 'حدث خطأ في إنشاء الإعلان'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/verify_ad_channel', methods=['POST'])
def verify_ad_channel():
    """التحقق من البوت في قناة المستخدم"""
    data = request.get_json()
    user_id = data.get('user_id')
    ad_id = data.get('ad_id')
    
    if not user_id or not ad_id:
        return jsonify({'success': False, 'message': 'بيانات ناقصة'})
    
    try:
        ad = db.get_ad_by_id(int(ad_id), int(user_id))
        if not ad:
            return jsonify({'success': False, 'message': 'الإعلان غير موجود'})
        
        success = db.verify_channel_bot(int(user_id), int(ad_id), "Youlim5_bot")
        
        if success:
            return jsonify({'success': True, 'message': 'تم التحقق بنجاح'})
        else:
            return jsonify({'success': False, 'message': 'فشل التحقق'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/referral_stats', methods=['GET'])
def get_referral_stats():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'user_id مطلوب'})
    
    try:
        stats = db.get_user_referrals_stats(int(user_id))
        bot_username = "Youlim5_bot"
        referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
        
        return jsonify({
            'success': True,
            'total': stats['total'],
            'granted': stats['granted'],
            'pending': stats['pending'],
            'total_points_earned': stats['total_points_earned'],
            'total_ton_earned': stats['total_ton_earned'],
            'referral_link': referral_link,
            'referrals': stats['referrals']
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/watch_ad', methods=['POST'])
def watch_ad():
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'message': 'user_id مطلوب'})
    
    try:
        today_ads = db.get_today_ads_count(int(user_id))
        
        if today_ads >= 10:
            return jsonify({'success': False, 'message': 'وصلت للحد اليومي'})
        
        reward = data.get('reward', 15)
        db.update_user_balance(int(user_id), points_amount=reward, update_earned=True)
        db.add_ad_watch(int(user_id), reward)
        
        user = db.get_user(int(user_id))
        
        return jsonify({
            'success': True,
            'reward': reward,
            'new_points': user['balance_points'],
            'remaining': 9 - today_ads
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/spin_wheel', methods=['POST'])
def spin_wheel():
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'message': 'user_id مطلوب'})
    
    try:
        today_spins = db.get_today_wheel_spins(int(user_id))
        
        if today_spins >= 3:
            return jsonify({'success': False, 'message': 'انتهت محاولاتك اليوم'})
        
        rewards = [5, 10, 15, 20, 25, 50, 75, 100]
        reward = random.choice(rewards)
        
        db.update_user_balance(int(user_id), points_amount=reward, update_earned=True)
        db.add_wheel_spin(int(user_id), reward)
        
        user = db.get_user(int(user_id))
        
        return jsonify({
            'success': True,
            'reward': reward,
            'new_points': user['balance_points'],
            'remaining': 2 - today_spins
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/wheel_status', methods=['GET'])
def wheel_status():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'user_id مطلوب'})
    
    try:
        today_spins = db.get_today_wheel_spins(int(user_id))
        user = db.get_user(int(user_id))
        
        return jsonify({
            'success': True,
            'remaining_spins': max(0, 3 - today_spins),
            'total_points': user['balance_points'] if user else 0
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/convert', methods=['POST'])
def convert_points():
    data = request.get_json()
    user_id = data.get('user_id')
    points = data.get('points', 0)
    
    success, msg = db.convert_points_to_ton(int(user_id), points)
    
    if success:
        user = db.get_user(int(user_id))
        return jsonify({
            'success': True,
            'ton': user['balance_ton'],
            'points': user['balance_points'],
            'message': msg
        })
    else:
        return jsonify({'success': False, 'message': msg})

@app.route('/api/request_withdraw', methods=['POST'])
def request_withdraw():
    data = request.get_json()
    user_id = data.get('user_id')
    amount = data.get('amount', 0)
    wallet = data.get('wallet', '')
    username = data.get('username', '')
    
    success, result = db.create_withdrawal(int(user_id), username, amount, wallet)
    
    return jsonify({
        'success': success,
        'message': 'تم إرسال طلب السحب' if success else result,
        'withdrawal_id': result if success else None
    })

@app.route('/api/withdrawals', methods=['GET'])
def get_withdrawals():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'user_id مطلوب'})
    
    withdrawals = db.get_user_withdrawals(int(user_id))
    return jsonify({'success': True, 'withdrawals': withdrawals})

@app.route('/api/redeem_code', methods=['POST'])
def redeem_code():
    data = request.get_json()
    user_id = data.get('user_id')
    code = data.get('code', '').upper()
    
    success, result = db.use_gift_code(int(user_id), code)
    
    if success:
        user = db.get_user(int(user_id))
        return jsonify({
            'success': True,
            'message': '✅ تم تفعيل الكود',
            'reward_points': result['reward_points'],
            'reward_ton': result['reward_ton'],
            'new_points': user['balance_points'],
            'new_ton': user['balance_ton']
        })
    else:
        return jsonify({'success': False, 'message': result})

@app.route('/api/ads', methods=['GET'])
def get_ads():
    user_id = request.args.get('user_id')
    today_ads = db.get_today_ads_count(int(user_id)) if user_id else 0
    
    ads = [
        {'id': 1, 'name': 'AdsGram', 'reward': 15, 'icon': '📺'},
        {'id': 2, 'name': 'MontageWeb', 'reward': 15, 'icon': '🎬'},
        {'id': 3, 'name': 'GigaBI Display', 'reward': 15, 'icon': '🖥️'},
        {'id': 4, 'name': 'شركة 4', 'reward': 15, 'icon': '📱'}
    ]
    
    return jsonify({
        'success': True,
        'ads': ads,
        'watched_today': today_ads,
        'daily_limit': 10
    })

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = [
        {'id': 1, 'title': 'قناة RockyTap', 'reward': 100, 'icon': '📺', 'channel_link': 'https://t.me/RockyTap', 'channel_username': '@RockyTap'},
        {'id': 2, 'title': 'قناة الأخبار', 'reward': 150, 'icon': '📰', 'channel_link': 'https://t.me/CryptoNews', 'channel_username': '@CryptoNews'},
        {'id': 3, 'title': 'مجموعة المناقشات', 'reward': 200, 'icon': '👥', 'channel_link': 'https://t.me/RockyTapGroup', 'channel_username': '@RockyTapGroup'}
    ]
    return jsonify({'success': True, 'tasks': tasks})

@app.route('/api/complete_task', methods=['POST'])
def complete_task():
    data = request.get_json()
    user_id = data.get('user_id')
    reward = data.get('reward', 0)
    
    db.update_user_balance(int(user_id), points_amount=reward, update_earned=True)
    user = db.get_user(int(user_id))
    
    return jsonify({
        'success': True,
        'message': f'✅ +{reward} نقطة',
        'new_points': user['balance_points']
    })

# ==================== تشغيل الخادم ====================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Local API Server is running!")
    print("=" * 60)
    print(f"📍 Local access: http://localhost:5000")
    print(f"📍 Network access: http://158.220.120.209:5000")
    print("=" * 60)
    print("✅ Available endpoints:")
    print("   GET  /api/health")
    print("   GET  /api/user")
    print("   GET  /api/user_ads")
    print("   POST /api/create_ad")
    print("   POST /api/verify_ad_channel")
    print("   GET  /api/tasks")
    print("   GET  /api/ads")
    print("   POST /api/watch_ad")
    print("   POST /api/spin_wheel")
    print("   POST /api/convert")
    print("   POST /api/request_withdraw")
    print("   POST /api/redeem_code")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)