// public/config.js
// إعدادات الواجهة الأمامية - مع Demo Mode ودوال الرصيد الموحد

// ==================== إعدادات التطبيق ====================

// تفعيل الوضع التجريبي (يعرض بيانات وهمية بدلاً من الاتصال بالخادم)
const DEMO_MODE = true;

// رابط API الخلفي (VPS) - يستخدم فقط عندما يكون DEMO_MODE = false
const API_URL = 'http://158.220.120.209:5000/api';

// رابط التطبيق على Cloudflare
const APP_URL = 'https://rockytap-bot.elias-guerbas.workers.dev';

// اسم البوت
const BOT_USERNAME = 'RockyTap_bot';

// ==================== دوال الرصيد الموحد ====================

// حفظ الرصيد في localStorage
function updateLocalBalance(userId, points, ton) {
    if (points !== undefined && points !== null) {
        localStorage.setItem(`points_${userId}`, points);
        console.log(`💾 Updated points: ${points}`);
    }
    if (ton !== undefined && ton !== null) {
        localStorage.setItem(`ton_${userId}`, ton);
        console.log(`💾 Updated TON: ${ton}`);
    }
}

// الحصول على الرصيد من localStorage
function getLocalBalance(userId) {
    return {
        points: parseInt(localStorage.getItem(`points_${userId}`)) || 0,
        ton: parseFloat(localStorage.getItem(`ton_${userId}`)) || 0
    };
}

// إضافة نقاط إلى الرصيد المحلي
function addLocalPoints(userId, points) {
    let current = getLocalBalance(userId);
    let newPoints = current.points + points;
    updateLocalBalance(userId, newPoints, null);
    
    // إرسال إشعار للصفحة الرئيسية إذا كانت مفتوحة
    if (window.opener && !window.opener.closed) {
        window.opener.postMessage({ 
            type: 'UPDATE_BALANCE', 
            points: newPoints,
            ton: current.ton
        }, '*');
    }
    
    // إرسال إشعار لأي نافذة أخرى في نفس التطبيق
    window.postMessage({ 
        type: 'UPDATE_BALANCE', 
        points: newPoints,
        ton: current.ton
    }, '*');
    
    return newPoints;
}

// إضافة تون إلى الرصيد المحلي
function addLocalTon(userId, ton) {
    let current = getLocalBalance(userId);
    let newTon = current.ton + ton;
    updateLocalBalance(userId, null, newTon);
    
    if (window.opener && !window.opener.closed) {
        window.opener.postMessage({ 
            type: 'UPDATE_BALANCE', 
            points: current.points,
            ton: newTon
        }, '*');
    }
    
    window.postMessage({ 
        type: 'UPDATE_BALANCE', 
        points: current.points,
        ton: newTon
    }, '*');
    
    return newTon;
}

// ==================== دوال API مع دعم Demo Mode ====================

async function apiCall(endpoint, data = null, method = 'GET') {
    // ========== الوضع التجريبي: عرض بيانات وهمية ==========
    if (DEMO_MODE) {
        console.log(`📡 DEMO MODE: ${method} ${endpoint}`);
        
        // بيانات وهمية للمستخدم (تجلب من localStorage إذا وجدت)
        if (endpoint.includes('users/me')) {
            let localBalance = getLocalBalance(8268443100);
            return {
                success: true,
                user_id: 8268443100,
                username: 'مستخدم تجريبي',
                ton: localBalance.ton || 1.2345,
                points: localBalance.points || 567,
                total_referrals: 3,
                is_blocked: false
            };
        }
        
        // بيانات وهمية للمهام
        if (endpoint.includes('tasks/list')) {
            return {
                success: true,
                tasks: [
                    { 
                        id: 1, 
                        title: "قناة RockyTap", 
                        description: "اشترك في قناتنا الرسمية",
                        icon: "📺", 
                        channel_link: "https://t.me/RockyTap", 
                        channel_username: "@RockyTap",
                        reward_points: 100, 
                        reward_ton: 0, 
                        user_status: "available" 
                    },
                    { 
                        id: 2, 
                        title: "قناة الأخبار", 
                        description: "تابع آخر الأخبار",
                        icon: "📰", 
                        channel_link: "https://t.me/CryptoNews", 
                        channel_username: "@CryptoNews",
                        reward_points: 150, 
                        reward_ton: 0.01, 
                        user_status: "available" 
                    },
                    { 
                        id: 3, 
                        title: "مجموعة المناقشات", 
                        description: "انضم إلى مجموعتنا",
                        icon: "👥", 
                        channel_link: "https://t.me/RockyTapGroup", 
                        channel_username: "@RockyTapGroup",
                        reward_points: 200, 
                        reward_ton: 0, 
                        user_status: "available" 
                    }
                ]
            };
        }
        
        // إكمال مهمة
        if (endpoint.includes('tasks/complete')) {
            let reward = 100;
            let newPoints = addLocalPoints(8268443100, reward);
            return {
                success: true,
                message: `✅ +${reward} نقطة!`,
                new_points: newPoints
            };
        }
        
        // بيانات وهمية للإعلانات
        if (endpoint.includes('ads/list')) {
            let watchedToday = parseInt(localStorage.getItem(`ads_watched_${8268443100}`)) || 0;
            return {
                success: true,
                ads: [
                    { id: 1, name: "AdsGram", reward: 15, icon: "📺" },
                    { id: 2, name: "MontageWeb", reward: 15, icon: "🎬" },
                    { id: 3, name: "GigaBI Display", reward: 15, icon: "🖥️" },
                    { id: 4, name: "شركة 4", reward: 15, icon: "📱" }
                ],
                watched_today: watchedToday,
                daily_limit: 10
            };
        }
        
        // مشاهدة إعلان
        if (endpoint.includes('ads/watch')) {
            let reward = 15;
            let watchedToday = parseInt(localStorage.getItem(`ads_watched_${8268443100}`)) || 0;
            
            if (watchedToday >= 10) {
                return {
                    success: false,
                    message: '⚠️ لقد وصلت للحد اليومي للإعلانات!'
                };
            }
            
            let newPoints = addLocalPoints(8268443100, reward);
            localStorage.setItem(`ads_watched_${8268443100}`, watchedToday + 1);
            
            return {
                success: true,
                reward: reward,
                new_points: newPoints,
                remaining: 9 - watchedToday
            };
        }
        
        // ==================== دوال عجلة الحظ المصححة ====================
        
        // بيانات وهمية لعجلة الحظ (الحالة)
        if (endpoint.includes('wheel/status')) {
            let userId = 8268443100;
            let today = new Date().toDateString();
            let lastReset = localStorage.getItem(`wheel_last_reset_${userId}`);
            let todaySpins = parseInt(localStorage.getItem(`wheel_spins_${userId}`)) || 0;
            
            // إعادة تعيين المحاولات إذا كان يوم جديد
            if (lastReset !== today) {
                todaySpins = 0;
                localStorage.setItem(`wheel_last_reset_${userId}`, today);
                localStorage.setItem(`wheel_spins_${userId}`, 0);
            }
            
            let remaining = Math.max(0, 3 - todaySpins);
            return {
                success: true,
                remaining_spins: remaining,
                total_points: getLocalBalance(userId).points
            };
        }
        
        // لعب عجلة الحظ
        if (endpoint.includes('wheel/spin')) {
            let userId = 8268443100;
            let today = new Date().toDateString();
            let lastReset = localStorage.getItem(`wheel_last_reset_${userId}`);
            let todaySpins = parseInt(localStorage.getItem(`wheel_spins_${userId}`)) || 0;
            
            // إعادة تعيين المحاولات إذا كان يوم جديد
            if (lastReset !== today) {
                todaySpins = 0;
                localStorage.setItem(`wheel_last_reset_${userId}`, today);
                localStorage.setItem(`wheel_spins_${userId}`, 0);
            }
            
            if (todaySpins >= 3) {
                return {
                    success: false,
                    message: '⚠️ لقد استنفدت جميع محاولاتك اليوم!'
                };
            }
            
            // الجوائز المتاحة في العجلة
            const rewards = [5, 10, 15, 20, 25, 30, 50, 100];
            const reward = rewards[Math.floor(Math.random() * rewards.length)];
            
            // زيادة عدد المحاولات
            todaySpins++;
            localStorage.setItem(`wheel_spins_${userId}`, todaySpins);
            
            // إضافة النقاط
            let currentBalance = getLocalBalance(userId);
            let newPoints = currentBalance.points + reward;
            updateLocalBalance(userId, newPoints, null);
            
            // إرسال تحديث للصفحة الرئيسية
            if (window.opener && !window.opener.closed) {
                window.opener.postMessage({ 
                    type: 'UPDATE_BALANCE', 
                    points: newPoints,
                    ton: currentBalance.ton
                }, '*');
            }
            
            return {
                success: true,
                reward: reward,
                new_points: newPoints,
                remaining: 3 - todaySpins
            };
        }
        
        // تحويل النقاط
        if (endpoint.includes('wallet/convert')) {
            const points = data?.points || 0;
            const ton = points / 10;
            
            let current = getLocalBalance(8268443100);
            let newPoints = current.points - points;
            let newTon = current.ton + ton;
            
            updateLocalBalance(8268443100, newPoints, newTon);
            
            return {
                success: true,
                message: `تم تحويل ${points} نقطة إلى ${ton.toFixed(4)} تون`,
                ton: newTon,
                points: newPoints
            };
        }
        
        // طلب سحب
        if (endpoint.includes('wallet/withdraw')) {
            let userId = 8268443100;
            let current = getLocalBalance(userId);
            let amount = data?.amount || 0;
            let newTon = current.ton - amount;
            
            if (newTon < 0) {
                return {
                    success: false,
                    message: '⚠️ الرصيد غير كافٍ'
                };
            }
            
            updateLocalBalance(userId, null, newTon);
            
            // حفظ طلب السحب
            let withdrawals = JSON.parse(localStorage.getItem(`withdrawals_${userId}`) || '[]');
            withdrawals.unshift({
                id: Date.now(),
                amount: amount,
                wallet_address: data?.wallet_address,
                status: 'pending',
                requested_at: new Date().toLocaleDateString('ar-EG')
            });
            localStorage.setItem(`withdrawals_${userId}`, JSON.stringify(withdrawals));
            
            return {
                success: true,
                withdrawal_id: Date.now(),
                amount: amount,
                new_balance: newTon,
                message: '✅ تم إرسال طلب السحب بنجاح'
            };
        }
        
        // سجل السحوبات
        if (endpoint.includes('wallet/withdrawals')) {
            let userId = 8268443100;
            let withdrawals = JSON.parse(localStorage.getItem(`withdrawals_${userId}`) || '[]');
            return {
                success: true,
                withdrawals: withdrawals
            };
        }
        
        // تفعيل كود
        if (endpoint.includes('giftcode/redeem')) {
            let reward = 100;
            let newPoints = addLocalPoints(8268443100, reward);
            
            return {
                success: true,
                reward_points: reward,
                reward_ton: 0,
                new_points: newPoints,
                new_ton: getLocalBalance(8268443100).ton,
                message: '✅ تم تفعيل الكود بنجاح!'
            };
        }
        
        // إحصائيات الإحالات
        if (endpoint.includes('referrals/stats')) {
            return {
                success: true,
                total: 3,
                granted: 2,
                pending: 1,
                total_points_earned: 200,
                total_ton_earned: 0.02,
                referral_link: `https://t.me/${BOT_USERNAME}?start=ref_8268443100`,
                referrals: [
                    { username: "user1", date: "2024-01-10", status: "مكتمل", reward_points: 100, reward_ton: 0.01 },
                    { username: "user2", date: "2024-01-15", status: "مكتمل", reward_points: 100, reward_ton: 0.01 },
                    { username: "user3", date: "2024-01-20", status: "قيد الانتظار", reward_points: 100, reward_ton: 0.01 }
                ]
            };
        }
        
        // أي طلب آخر
        return { success: true, message: 'DEMO MODE: تم استلام الطلب' };
    }
    
    // ========== الوضع الحقيقي: الاتصال بالخادم ==========
    const url = `${API_URL}/${endpoint}`;
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }
    
    try {
        console.log(`📡 API Call: ${method} ${url}`);
        const response = await fetch(url, options);
        const result = await response.json();
        console.log(`📡 API Response:`, result);
        return result;
    } catch (error) {
        console.error('API Error:', error);
        return { success: false, message: 'خطأ في الاتصال بالخادم' };
    }
}

// ==================== دوال المستخدم ====================

async function getUserData(userId) {
    return await apiCall(`users/me?user_id=${userId}`);
}

async function getReferralStats(userId) {
    return await apiCall(`referrals/stats?user_id=${userId}`);
}

async function getTasks(userId) {
    return await apiCall(`tasks/list?user_id=${userId}`);
}

async function completeTask(userId, taskId) {
    return await apiCall(`tasks/complete?user_id=${userId}&task_id=${taskId}`, null, 'POST');
}

async function getAds(userId) {
    return await apiCall(`ads/list?user_id=${userId}`);
}

async function watchAd(userId, reward = 15) {
    return await apiCall('ads/watch', { user_id: userId, reward: reward }, 'POST');
}

async function getWheelStatus(userId) {
    return await apiCall(`wheel/status?user_id=${userId}`);
}

async function spinWheel(userId) {
    return await apiCall('wheel/spin', { user_id: userId }, 'POST');
}

async function convertPoints(userId, points) {
    return await apiCall('wallet/convert', { user_id: userId, points: points }, 'POST');
}

async function requestWithdraw(userId, amount, wallet, username) {
    return await apiCall('wallet/withdraw', { user_id: userId, amount: amount, wallet_address: wallet, username: username }, 'POST');
}

async function getUserWithdrawals(userId) {
    return await apiCall(`wallet/withdrawals?user_id=${userId}`);
}

async function redeemCode(userId, code) {
    return await apiCall('giftcode/redeem', { user_id: userId, code: code }, 'POST');
}

// ==================== دوال WebApp ====================

let tg = null;
let currentUserId = null;

function initTelegram() {
    if (window.Telegram && window.Telegram.WebApp) {
        tg = window.Telegram.WebApp;
        tg.expand();
        tg.ready();
        
        if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
            currentUserId = tg.initDataUnsafe.user.id;
            window.currentUserId = currentUserId;
        }
    }
    
    if (!currentUserId) {
        currentUserId = localStorage.getItem('testUserId') || 8268443100;
        localStorage.setItem('testUserId', currentUserId);
    }
    
    return tg;
}

function sendToBot(action, data) {
    if (tg && tg.sendData) {
        tg.sendData(JSON.stringify({ action: action, ...data }));
    }
    console.log('📤 Send to bot:', action, data);
}

// ==================== دوال التنبيه والإشعارات (معدلة للإصدارات القديمة) ====================

function showAlert(message) {
    // محاولة استخدام showAlert من Telegram إذا كانت موجودة
    if (tg && tg.showAlert) {
        try {
            tg.showAlert(message);
            return;
        } catch(e) {
            console.log('Telegram showAlert failed, using fallback');
        }
    }
    
    // طريقة بديلة: نافذة HTML مخصصة
    showCustomAlert(message);
}

// نافذة تنبيه مخصصة
function showCustomAlert(message) {
    // إزالة أي نافذة موجودة مسبقاً
    let existingAlert = document.getElementById('customAlert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
    // إنشاء نافذة التنبيه
    let alertDiv = document.createElement('div');
    alertDiv.id = 'customAlert';
    alertDiv.innerHTML = `
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.85);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            font-family: 'Cairo', sans-serif;
        ">
            <div style="
                background: #0A0F1A;
                border: 2px solid #00BFFF;
                border-radius: 20px;
                padding: 25px;
                width: 280px;
                text-align: center;
                box-shadow: 0 0 30px rgba(0,191,255,0.3);
            ">
                <div style="
                    font-size: 32px;
                    margin-bottom: 15px;
                ">📢</div>
                <div style="
                    color: white;
                    margin-bottom: 20px;
                    line-height: 1.5;
                    font-size: 16px;
                ">${message}</div>
                <button onclick="this.closest('#customAlert').remove()" style="
                    background: linear-gradient(135deg, #00BFFF, #0088aa);
                    border: none;
                    padding: 10px 25px;
                    border-radius: 50px;
                    color: white;
                    font-weight: bold;
                    cursor: pointer;
                    font-size: 14px;
                    transition: transform 0.2s;
                " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">حسناً</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(alertDiv);
    
    // إغلاق النافذة عند الضغط خارجها
    alertDiv.addEventListener('click', function(e) {
        if (e.target === alertDiv) {
            alertDiv.remove();
        }
    });
}

function showConfirm(message, callback) {
    // محاولة استخدام showConfirm من Telegram إذا كانت موجودة
    if (tg && tg.showConfirm) {
        try {
            tg.showConfirm(message, callback);
            return;
        } catch(e) {
            console.log('Telegram showConfirm failed, using fallback');
        }
    }
    
    // طريقة بديلة: نافذة تأكيد مخصصة
    showCustomConfirm(message, callback);
}

// نافذة تأكيد مخصصة
function showCustomConfirm(message, callback) {
    let existingConfirm = document.getElementById('customConfirm');
    if (existingConfirm) {
        existingConfirm.remove();
    }
    
    let confirmDiv = document.createElement('div');
    confirmDiv.id = 'customConfirm';
    confirmDiv.innerHTML = `
        <div style="
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.85);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            font-family: 'Cairo', sans-serif;
        ">
            <div style="
                background: #0A0F1A;
                border: 2px solid #00BFFF;
                border-radius: 20px;
                padding: 25px;
                width: 280px;
                text-align: center;
                box-shadow: 0 0 30px rgba(0,191,255,0.3);
            ">
                <div style="
                    font-size: 32px;
                    margin-bottom: 15px;
                ">❓</div>
                <div style="
                    color: white;
                    margin-bottom: 20px;
                    line-height: 1.5;
                    font-size: 16px;
                ">${message}</div>
                <div style="display: flex; gap: 15px; justify-content: center;">
                    <button id="confirmYes" style="
                        background: linear-gradient(135deg, #2ecc71, #27ae60);
                        border: none;
                        padding: 8px 25px;
                        border-radius: 50px;
                        color: white;
                        font-weight: bold;
                        cursor: pointer;
                        transition: transform 0.2s;
                    " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">نعم</button>
                    <button id="confirmNo" style="
                        background: linear-gradient(135deg, #e74c3c, #c0392b);
                        border: none;
                        padding: 8px 25px;
                        border-radius: 50px;
                        color: white;
                        font-weight: bold;
                        cursor: pointer;
                        transition: transform 0.2s;
                    " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">لا</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(confirmDiv);
    
    // ربط callback
    document.getElementById('confirmYes').onclick = () => {
        confirmDiv.remove();
        callback(true);
    };
    document.getElementById('confirmNo').onclick = () => {
        confirmDiv.remove();
        callback(false);
    };
    
    // إغلاق عند الضغط خارجها
    confirmDiv.addEventListener('click', function(e) {
        if (e.target === confirmDiv) {
            confirmDiv.remove();
            callback(false);
        }
    });
}

// ==================== دوال التنقل ====================

function goTo(page) {
    const pages = {
        'home': 'index.html',
        'tasks': 'tasks.html',
        'wheel': 'wheel.html',
        'ads': 'ads.html',
        'ads_posting': 'ads_posting.html',
        'withdraw': 'withdraw.html',
        'referral': 'referral.html',
        'giftcode': 'giftcode.html',
        'admin': 'admin.html'
    };
    
    if (pages[page]) {
        window.location.href = pages[page];
    }
}

function goBack() {
    window.history.back();
}

// ==================== دوال مساعدة ====================

function formatNumber(number, decimals = 4) {
    return parseFloat(number).toFixed(decimals);
}

function formatDate(date) {
    if (!date) return '';
    let d = new Date(date);
    return d.toLocaleDateString('ar-EG');
}

// ==================== التهيئة ====================

document.addEventListener('DOMContentLoaded', function() {
    initTelegram();
    console.log('✅ Config.js loaded');
    console.log('📍 DEMO_MODE:', DEMO_MODE);
    console.log('📍 API_URL:', API_URL);
    console.log('📍 Current User:', currentUserId);
    
    // استقبال رسائل تحديث الرصيد من الصفحات الأخرى
    window.addEventListener('message', function(event) {
        if (event.data && event.data.type === 'UPDATE_BALANCE') {
            console.log('📨 Received balance update:', event.data);
            if (event.data.points !== undefined) {
                localStorage.setItem(`points_${currentUserId}`, event.data.points);
            }
            if (event.data.ton !== undefined) {
                localStorage.setItem(`ton_${currentUserId}`, event.data.ton);
            }
            // تحديث الواجهة إذا كانت الدوال موجودة
            if (typeof updateBalanceDisplay === 'function') {
                updateBalanceDisplay(event.data.points, event.data.ton);
            }
        }
    });
});

// تصدير الدوال
window.API_URL = API_URL;
window.DEMO_MODE = DEMO_MODE;
window.getUserData = getUserData;
window.getReferralStats = getReferralStats;
window.getTasks = getTasks;
window.completeTask = completeTask;
window.getAds = getAds;
window.watchAd = watchAd;
window.getWheelStatus = getWheelStatus;
window.spinWheel = spinWheel;
window.convertPoints = convertPoints;
window.requestWithdraw = requestWithdraw;
window.getUserWithdrawals = getUserWithdrawals;
window.redeemCode = redeemCode;
window.sendToBot = sendToBot;
window.showAlert = showAlert;
window.showConfirm = showConfirm;
window.goTo = goTo;
window.goBack = goBack;
window.initTelegram = initTelegram;
window.formatNumber = formatNumber;
window.formatDate = formatDate;
window.updateLocalBalance = updateLocalBalance;
window.getLocalBalance = getLocalBalance;
window.addLocalPoints = addLocalPoints;
window.addLocalTon = addLocalTon;