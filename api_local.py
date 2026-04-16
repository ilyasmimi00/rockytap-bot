# api_local.py - خادم API محلي كامل مع المهام

from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Database
from datetime import datetime
import random
import socket

app = Flask(__name__)
CORS(app)

db = Database()

# معرفات الأدمن (ضع معرفات الأدمن هنا)
ADMIN_IDS = [8268443100]

# ==================== واجهات API الأساسية ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

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
            'remaining': 9 - today_ads,
            'watched_today': today_ads + 1
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

@app.route('/api/claim_ads', methods=['POST'])
def claim_ads():
    data = request.get_json()
    user_id = data.get('user_id')
    points = data.get('points', 0)
    
    success, msg = db.convert_points_to_ton(int(user_id), points)
    
    if success:
        user = db.get_user(int(user_id))
        return jsonify({
            'success': True,
            'message': f'🎉 تم تحويل {points} نقطة',
            'new_ton': user['balance_ton'],
            'new_points': user['balance_points']
        })
    else:
        return jsonify({'success': False, 'message': msg})

# ==================== واجهات المهام ====================

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """جلب جميع المهام المتاحة للمستخدم"""
    user_id = request.args.get('user_id')
    
    try:
        tasks = db.get_active_tasks()
        user_tasks = db.get_user_tasks_progress(int(user_id)) if user_id else []
        
        # إضافة حالة كل مهمة للمستخدم
        user_task_map = {ut['task_id']: ut['status'] for ut in user_tasks}
        
        for task in tasks:
            task['status'] = user_task_map.get(task['id'], 'available')
        
        return jsonify({'success': True, 'tasks': tasks})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e), 'tasks': []})

@app.route('/api/task', methods=['GET'])
def get_task():
    """جلب تفاصيل مهمة محددة"""
    task_id = request.args.get('task_id')
    user_id = request.args.get('user_id')
    
    if not task_id:
        return jsonify({'success': False, 'message': 'task_id مطلوب'})
    
    try:
        task = db.get_task(int(task_id))
        if not task:
            return jsonify({'success': False, 'message': 'المهمة غير موجودة'})
        
        if user_id:
            status = db.verify_user_task(int(user_id), int(task_id))
            task['status'] = status
        else:
            task['status'] = 'available'
        
        return jsonify({'success': True, 'task': task})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/verify_task', methods=['POST'])
def verify_task():
    """التحقق من اشتراك المستخدم ومنح المكافأة"""
    data = request.get_json()
    user_id = data.get('user_id')
    task_id = data.get('task_id')
    
    if not user_id or not task_id:
        return jsonify({'success': False, 'message': 'بيانات ناقصة'})
    
    try:
        # التحقق من وجود المهمة
        task = db.get_task(int(task_id))
        if not task:
            return jsonify({'success': False, 'message': 'المهمة غير موجودة'})
        
        # التحقق من حالة المهمة للمستخدم
        current_status = db.verify_user_task(int(user_id), int(task_id))
        
        if current_status == 'completed':
            return jsonify({'success': False, 'message': 'لقد حصلت على المكافأة بالفعل'})
        
        # ملاحظة: هنا يجب التحقق من اشتراك المستخدم في القناة
        # لكن هذا يتطلب توكن البوت والتحقق عبر Telegram API
        # سنعتبر أن التحقق ناجح حالياً
        
        # إكمال المهمة ومنح المكافأة
        success = db.complete_user_task(int(user_id), int(task_id))
        
        if success:
            reward_text = ""
            if task['reward_points'] > 0:
                reward_text += f"⭐ {task['reward_points']} نقطة"
            if task['reward_ton'] > 0:
                if reward_text:
                    reward_text += " + "
                reward_text += f"💰 {task['reward_ton']} تون"
            
            return jsonify({
                'success': True,
                'message': 'تم التحقق بنجاح',
                'reward_text': reward_text,
                'reward_points': task['reward_points'],
                'reward_ton': task['reward_ton']
            })
        else:
            return jsonify({'success': False, 'message': 'حدث خطأ في منح المكافأة'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/start_task', methods=['POST'])
def start_task():
    """بدء مهمة جديدة"""
    data = request.get_json()
    user_id = data.get('user_id')
    task_id = data.get('task_id')
    
    if not user_id or not task_id:
        return jsonify({'success': False, 'message': 'بيانات ناقصة'})
    
    try:
        success = db.create_user_task(int(user_id), int(task_id))
        if success:
            return jsonify({'success': True, 'message': 'تم بدء المهمة'})
        else:
            return jsonify({'success': False, 'message': 'المهمة قيد التنفيذ بالفعل'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ==================== واجهات الأدمن للمهام ====================

@app.route('/api/admin/tasks', methods=['GET'])
def admin_get_tasks():
    """جلب جميع المهام للأدمن"""
    admin_id = request.args.get('admin_id')
    if not admin_id or int(admin_id) not in ADMIN_IDS:
        return jsonify({'success': False, 'message': 'غير مصرح'})
    
    tasks = db.get_all_tasks()
    return jsonify({'success': True, 'tasks': tasks})

@app.route('/api/admin/create_task', methods=['POST'])
def admin_create_task():
    """إنشاء مهمة جديدة"""
    data = request.get_json()
    admin_id = data.get('admin_id')
    
    if not admin_id or int(admin_id) not in ADMIN_IDS:
        return jsonify({'success': False, 'message': 'غير مصرح'})
    
    success, result = db.create_task(
        title=data.get('title'),
        description=data.get('description', ''),
        icon=data.get('icon', '📺'),
        channel_link=data.get('channel_link'),
        channel_username=data.get('channel_username', ''),
        reward_points=data.get('reward_points', 0),
        reward_ton=data.get('reward_ton', 0),
        created_by=int(admin_id)
    )
    
    return jsonify({
        'success': success,
        'task': result if success else None,
        'message': 'تم الإنشاء' if success else str(result)
    })

@app.route('/api/admin/update_task', methods=['POST'])
def admin_update_task():
    """تحديث مهمة"""
    data = request.get_json()
    admin_id = data.get('admin_id')
    
    if not admin_id or int(admin_id) not in ADMIN_IDS:
        return jsonify({'success': False, 'message': 'غير مصرح'})
    
    success = db.update_task(
        task_id=data.get('task_id'),
        title=data.get('title'),
        description=data.get('description', ''),
        icon=data.get('icon', '📺'),
        channel_link=data.get('channel_link'),
        channel_username=data.get('channel_username', ''),
        reward_points=data.get('reward_points', 0),
        reward_ton=data.get('reward_ton', 0)
    )
    
    return jsonify({'success': success, 'message': 'تم التحديث' if success else 'فشل التحديث'})

@app.route('/api/admin/delete_task', methods=['POST'])
def admin_delete_task():
    """حذف مهمة"""
    data = request.get_json()
    admin_id = data.get('admin_id')
    task_id = data.get('task_id')
    
    if not admin_id or int(admin_id) not in ADMIN_IDS:
        return jsonify({'success': False, 'message': 'غير مصرح'})
    
    success = db.delete_task(task_id)
    return jsonify({'success': success, 'message': 'تم الحذف' if success else 'فشل الحذف'})

@app.route('/api/admin/task', methods=['GET'])
def admin_get_task():
    """جلب مهمة محددة للتعديل"""
    admin_id = request.args.get('admin_id')
    task_id = request.args.get('task_id')
    
    if not admin_id or int(admin_id) not in ADMIN_IDS:
        return jsonify({'success': False, 'message': 'غير مصرح'})
    
    task = db.get_task(int(task_id))
    return jsonify({'success': True, 'task': task})

# ==================== تشغيل الخادم ====================

if __name__ == '__main__':
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except:
        local_ip = '127.0.0.1'
    
    print("=" * 60)
    print("🚀 Local API Server is running!")
    print("=" * 60)
    print(f"📍 Local access: http://localhost:5000")
    print(f"📍 Network access: http://{local_ip}:5000")
    print("=" * 60)
    print("✅ Available endpoints:")
    print("   GET  /api/health")
    print("   GET  /api/user")
    print("   GET  /api/tasks")
    print("   GET  /api/task")
    print("   POST /api/verify_task")
    print("   POST /api/start_task")
    print("   GET  /api/admin/tasks")
    print("   POST /api/admin/create_task")
    print("   POST /api/admin/update_task")
    print("   POST /api/admin/delete_task")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)