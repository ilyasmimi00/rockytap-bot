# api.py - النسخة الكاملة مع خدمة الملفات الثابتة

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import Database
from datetime import datetime
import random
import os

app = Flask(__name__, static_folder='static')
CORS(app)  # السماح بجميع الطلبات

# تهيئة قاعدة البيانات
db = Database()

# ==================== دوال مساعدة ====================

def success_response(data):
    return jsonify({'success': True, **data})

def error_response(message):
    return jsonify({'success': False, 'message': message})

# ==================== خدمة الملفات الثابتة ====================

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # التحقق من وجود الملف في مجلد static
    if os.path.exists(os.path.join('static', path)):
        return send_from_directory('static', path)
    return error_response('File not found'), 404

# ==================== واجهات API ====================

@app.route('/api/user', methods=['POST', 'GET'])
def get_user():
    """جلب بيانات المستخدم"""
    if request.method == 'POST':
        data = request.get_json()
        user_id = data.get('user_id')
    else:
        user_id = request.args.get('user_id')
    
    if not user_id:
        return error_response('user_id مطلوب')
    
    user = db.get_user(user_id)
    if not user:
        return error_response('المستخدم غير موجود')
    
    today_ads = db.get_today_ads_count(user_id)
    
    return success_response({
        'user_id': user['user_id'],
        'username': user['username'],
        'first_name': user['first_name'],
        'ton': user['balance_ton'],
        'points': user['balance_points'],
        'total_referrals': user['total_referrals'],
        'ads_watched': today_ads,
        'daily_ads_limit': 10,
        'min_withdraw': 0.02
    })

@app.route('/api/convert', methods=['POST'])
def convert_points():
    """تحويل النقاط إلى تون"""
    data = request.get_json()
    user_id = data.get('user_id')
    points = data.get('points', 0)
    
    if not user_id:
        return error_response('user_id مطلوب')
    
    success, msg = db.convert_points_to_ton(user_id, points)
    
    if success:
        user = db.get_user(user_id)
        return success_response({
            'message': msg,
            'new_ton': user['balance_ton'],
            'new_points': user['balance_points']
        })
    else:
        return error_response(msg)

@app.route('/api/watch_ad', methods=['POST'])
def watch_ad():
    """تسجيل مشاهدة إعلان"""
    data = request.get_json()
    user_id = data.get('user_id')
    company = data.get('company', '')
    reward = data.get('reward', 15)
    
    if not user_id:
        return error_response('user_id مطلوب')
    
    today_ads = db.get_today_ads_count(user_id)
    
    if today_ads >= 10:
        return error_response('لقد وصلت للحد اليومي للإعلانات!')
    
    db.update_user_balance(user_id, points_amount=reward, update_earned=True)
    db.add_ad_watch(user_id, reward)
    
    user = db.get_user(user_id)
    remaining = 10 - (today_ads + 1)
    
    return success_response({
        'message': f'✅ +{reward} نقطة!',
        'new_points': user['balance_points'],
        'remaining': remaining,
        'watched_today': today_ads + 1
    })

@app.route('/api/claim_ads', methods=['POST'])
def claim_ads():
    """المطالبة بمكافأة الإعلانات"""
    data = request.get_json()
    user_id = data.get('user_id')
    points = data.get('points', 0)
    
    if not user_id:
        return error_response('user_id مطلوب')
    
    success, msg = db.convert_points_to_ton(user_id, points)
    
    if success:
        user = db.get_user(user_id)
        return success_response({
            'message': f'🎉 تم تحويل {points} نقطة إلى {points/10:.4f} تون',
            'new_ton': user['balance_ton'],
            'new_points': user['balance_points']
        })
    else:
        return error_response(msg)

@app.route('/api/spin_wheel', methods=['POST'])
def spin_wheel():
    """تدوير عجلة الحظ"""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return error_response('user_id مطلوب')
    
    today_spins = db.get_today_wheel_spins(user_id)
    
    if today_spins >= 3:
        return error_response('لقد استنفدت جميع محاولاتك اليوم!')
    
    rewards = [5, 10, 15, 20, 25, 50, 75, 100]
    reward = random.choice(rewards)
    
    db.update_user_balance(user_id, points_amount=reward, update_earned=True)
    db.add_wheel_spin(user_id, reward)
    
    user = db.get_user(user_id)
    remaining = 3 - (today_spins + 1)
    
    return success_response({
        'message': f'🎉 مبروك! ربحت {reward} نقطة!',
        'reward': reward,
        'new_points': user['balance_points'],
        'remaining': remaining,
        'total_points': user['balance_points']
    })

@app.route('/api/wheel_status', methods=['GET'])
def wheel_status():
    """الحصول على حالة عجلة الحظ"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return error_response('user_id مطلوب')
    
    today_spins = db.get_today_wheel_spins(user_id)
    user = db.get_user(user_id)
    
    return success_response({
        'remaining_spins': max(0, 3 - today_spins),
        'total_points': user['balance_points'] if user else 0
    })

@app.route('/api/referral_stats', methods=['GET', 'POST'])
def referral_stats():
    """الحصول على إحصائيات الإحالات"""
    if request.method == 'POST':
        data = request.get_json()
        user_id = data.get('user_id')
    else:
        user_id = request.args.get('user_id')
    
    if not user_id:
        return error_response('user_id مطلوب')
    
    stats = db.get_user_referrals_stats(user_id)
    
    # الحصول على رابط الإحالة
    bot_username = "Youlim5_bot"
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    return success_response({
        'total': stats['total'],
        'granted': stats['granted'],
        'pending': stats['pending'],
        'total_points_earned': stats['total_points_earned'],
        'total_ton_earned': stats['total_ton_earned'],
        'referral_link': referral_link,
        'referrals': stats['referrals']
    })

@app.route('/api/redeem_code', methods=['POST'])
def redeem_code():
    """تفعيل كود ترويجي"""
    data = request.get_json()
    user_id = data.get('user_id')
    code = data.get('code', '').upper()
    
    if not user_id:
        return error_response('user_id مطلوب')
    
    success, result = db.use_gift_code(user_id, code)
    
    if success:
        user = db.get_user(user_id)
        return success_response({
            'message': '✅ تم تفعيل الكود بنجاح!',
            'reward_points': result['reward_points'],
            'reward_ton': result['reward_ton'],
            'new_points': user['balance_points'],
            'new_ton': user['balance_ton']
        })
    else:
        return error_response(result)

@app.route('/api/request_withdraw', methods=['POST'])
def request_withdraw():
    """طلب سحب"""
    data = request.get_json()
    user_id = data.get('user_id')
    amount = data.get('amount', 0)
    wallet = data.get('wallet', '')
    username = data.get('username', '')
    
    if not user_id:
        return error_response('user_id مطلوب')
    
    success, result = db.create_withdrawal(user_id, username, amount, wallet)
    
    if success:
        return success_response({
            'message': f'✅ تم إرسال طلب السحب #{result} بنجاح!',
            'withdrawal_id': result
        })
    else:
        return error_response(result)

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """جلب المهام"""
    tasks = [
        {'id': 1, 'title': 'مهمة 1', 'reward': 50, 'icon': '📋', 'completed': False},
        {'id': 2, 'title': 'مهمة 2', 'reward': 100, 'icon': '📺', 'completed': False},
        {'id': 3, 'title': 'مهمة 3', 'reward': 75, 'icon': '👥', 'completed': False}
    ]
    
    return success_response({'tasks': tasks})

@app.route('/api/complete_task', methods=['POST'])
def complete_task():
    """إكمال مهمة"""
    data = request.get_json()
    user_id = data.get('user_id')
    task_id = data.get('task_id')
    reward = data.get('reward', 0)
    
    if not user_id:
        return error_response('user_id مطلوب')
    
    db.update_user_balance(user_id, points_amount=reward, update_earned=True)
    user = db.get_user(user_id)
    
    return success_response({
        'message': f'✅ تم إكمال المهمة! +{reward} نقطة',
        'new_points': user['balance_points']
    })

@app.route('/api/ads', methods=['GET'])
def get_ads():
    """جلب الإعلانات المتاحة"""
    user_id = request.args.get('user_id')
    
    today_ads = db.get_today_ads_count(user_id) if user_id else 0
    
    ads = [
        {'id': 1, 'name': 'AdsGram', 'reward': 15, 'icon': '📺'},
        {'id': 2, 'name': 'MontageWeb', 'reward': 15, 'icon': '🎬'},
        {'id': 3, 'name': 'GigaBI Display', 'reward': 15, 'icon': '🖥️'},
        {'id': 4, 'name': 'شركة 4', 'reward': 15, 'icon': '📱'}
    ]
    
    return success_response({
        'ads': ads,
        'watched_today': today_ads,
        'daily_limit': 10
    })

@app.route('/api/withdrawals', methods=['GET'])
def get_withdrawals():
    """جلب طلبات السحب للمستخدم"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return error_response('user_id مطلوب')
    
    withdrawals = db.get_user_withdrawals(user_id)
    
    return success_response({'withdrawals': withdrawals})

# ==================== تشغيل الخادم ====================

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 API Server is running...")
    print("📍 URL: http://localhost:5000")
    print("📋 Available endpoints:")
    print("   GET  /api/user")
    print("   POST /api/convert")
    print("   POST /api/watch_ad")
    print("   POST /api/claim_ads")
    print("   POST /api/spin_wheel")
    print("   GET  /api/wheel_status")
    print("   GET  /api/referral_stats")
    print("   POST /api/redeem_code")
    print("   POST /api/request_withdraw")
    print("   GET  /api/tasks")
    print("   GET  /api/ads")
    print("   GET  /api/withdrawals")
    print("=" * 50)
    print("🌐 Open in browser: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)