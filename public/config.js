// public/config.js
// إعدادات الواجهة الأمامية - مع Demo Mode

// ==================== إعدادات التطبيق ====================

// تفعيل الوضع التجريبي (يعرض بيانات وهمية بدلاً من الاتصال بالخادم)
const DEMO_MODE = true;

// رابط API الخلفي (VPS) - يستخدم فقط عندما يكون DEMO_MODE = false
const API_URL = 'http://158.220.120.209:5000/api';

// رابط التطبيق على Cloudflare
const APP_URL = 'https://rockytap-bot.elias-guerbas.workers.dev';

// اسم البوت
const BOT_USERNAME = 'RockyTap_bot';

// ==================== دوال API مع دعم Demo Mode ====================

async function apiCall(endpoint, data = null, method = 'GET') {
    // ========== الوضع التجريبي: عرض بيانات وهمية ==========
    if (DEMO_MODE) {
        console.log(`📡 DEMO MODE: ${method} ${endpoint}`);
        
        // بيانات وهمية للمستخدم
        if (endpoint.includes('users/me')) {
            return {
                success: true,
                user_id: 8268443100,
                username: 'مستخدم تجريبي',
                ton: 1.2345,
                points: 567,
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
            return {
                success: true,
                message: '✅ تم إكمال المهمة بنجاح!',
                new_points: 667
            };
        }
        
        // بيانات وهمية للإعلانات
        if (endpoint.includes('ads/list')) {
            return {
                success: true,
                ads: [
                    { id: 1, name: "AdsGram", reward: 15, icon: "📺" },
                    { id: 2, name: "MontageWeb", reward: 15, icon: "🎬" },
                    { id: 3, name: "GigaBI Display", reward: 15, icon: "🖥️" },
                    { id: 4, name: "شركة 4", reward: 15, icon: "📱" }
                ],
                watched_today: 3,
                daily_limit: 10
            };
        }
        
        // مشاهدة إعلان
        if (endpoint.includes('ads/watch')) {
            return {
                success: true,
                reward: 15,
                new_points: 582,
                remaining: 6
            };
        }
        
        // بيانات وهمية لعجلة الحظ
        if (endpoint.includes('wheel/status')) {
            return {
                success: true,
                remaining_spins: 3,
                total_points: 567
            };
        }
        
        // لعب عجلة الحظ
        if (endpoint.includes('wheel/spin')) {
            const rewards = [5, 10, 15, 20, 25, 50, 75, 100];
            const reward = rewards[Math.floor(Math.random() * rewards.length)];
            return {
                success: true,
                reward: reward,
                new_points: 567 + reward,
                remaining: 2
            };
        }
        
        // تحويل النقاط
        if (endpoint.includes('wallet/convert')) {
            const points = data?.points || 0;
            const ton = points / 10;
            return {
                success: true,
                message: `تم تحويل ${points} نقطة إلى ${ton.toFixed(4)} تون`,
                ton: 1.2345 + ton,
                points: 567 - points
            };
        }
        
        // طلب سحب
        if (endpoint.includes('wallet/withdraw')) {
            return {
                success: true,
                withdrawal_id: Date.now(),
                amount: data?.amount,
                new_balance: 1.2345 - (data?.amount || 0),
                message: '✅ تم إرسال طلب السحب بنجاح'
            };
        }
        
        // سجل السحوبات
        if (endpoint.includes('wallet/withdrawals')) {
            return {
                success: true,
                withdrawals: [
                    { id: 1, amount: 0.05, wallet_address: "UQ...", status: "completed", requested_at: "2024-01-15" },
                    { id: 2, amount: 0.10, wallet_address: "UQ...", status: "pending", requested_at: "2024-01-20" }
                ]
            };
        }
        
        // تفعيل كود
        if (endpoint.includes('giftcode/redeem')) {
            return {
                success: true,
                reward_points: 100,
                reward_ton: 0.01,
                new_points: 667,
                new_ton: 1.2445,
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

function showAlert(message) {
    if (tg && tg.showAlert) {
        tg.showAlert(message);
    } else {
        alert(message);
    }
}

function showConfirm(message, callback) {
    if (tg && tg.showConfirm) {
        tg.showConfirm(message, callback);
    } else {
        if (confirm(message)) callback(true);
        else callback(false);
    }
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