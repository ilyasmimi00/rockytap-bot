// public/config.js - نسخة مع Demo Mode
// إعدادات الواجهة الأمامية

// ==================== إعدادات التطبيق ====================

// وضع تجريبي (يعرض بيانات وهمية بدلاً من الاتصال بالخادم)
const DEMO_MODE = true;

// رابط API الخلفي (للاستخدام الحقيقي)
const API_URL = 'http://158.220.120.209:5000/api';

// رابط التطبيق على Cloudflare
const APP_URL = 'https://rockytap-bot.elias-guerbas.workers.dev';

// اسم البوت
const BOT_USERNAME = 'RockyTap_bot';

// ==================== بيانات تجريبية ====================

const DEMO_DATA = {
    user: {
        id: 8268443100,
        ton: 1.2345,
        points: 567,
        total_referrals: 3,
        is_blocked: false
    },
    tasks: [
        { id: 1, title: "قناة RockyTap", description: "اشترك في قناتنا الرسمية", icon: "📺", channel_link: "https://t.me/RockyTap", channel_username: "@RockyTap", reward_points: 100, reward_ton: 0, user_status: "available" },
        { id: 2, title: "قناة الأخبار", description: "تابع آخر الأخبار", icon: "📰", channel_link: "https://t.me/CryptoNews", channel_username: "@CryptoNews", reward_points: 150, reward_ton: 0.01, user_status: "available" },
        { id: 3, title: "مجموعة المناقشات", description: "انضم إلى مجموعتنا", icon: "👥", channel_link: "https://t.me/RockyTapGroup", channel_username: "@RockyTapGroup", reward_points: 200, reward_ton: 0, user_status: "available" }
    ],
    ads: [
        { id: 1, name: "AdsGram", reward: 15, icon: "📺" },
        { id: 2, name: "MontageWeb", reward: 15, icon: "🎬" },
        { id: 3, name: "GigaBI Display", reward: 15, icon: "🖥️" },
        { id: 4, name: "شركة 4", reward: 15, icon: "📱" }
    ],
    wheelRewards: [5, 10, 15, 20, 25, 50, 75, 100],
    dailyLimit: { ads: 10, wheelSpins: 3 },
    referralLink: `https://t.me/RockyTap_bot?start=ref_8268443100`
};

// ==================== دوال API مع دعم Demo Mode ====================

async function apiCall(endpoint, data = null, method = 'GET') {
    if (DEMO_MODE) {
        console.log(`📡 DEMO MODE: ${method} ${endpoint}`);
        return handleDemoResponse(endpoint, data);
    }
    
    const url = `${API_URL}/${endpoint}`;
    const options = {
        method: method,
        headers: { 'Content-Type': 'application/json' }
    };
    
    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return { success: false, message: 'خطأ في الاتصال بالخادم' };
    }
}

function handleDemoResponse(endpoint, data) {
    // مستخدم
    if (endpoint === 'users/me' || endpoint.startsWith('users/me?')) {
        return { success: true, ...DEMO_DATA.user };
    }
    
    // المهام
    if (endpoint === 'tasks/list') {
        return { success: true, tasks: DEMO_DATA.tasks };
    }
    
    if (endpoint === 'tasks/complete') {
        return { success: true, message: '✅ تم إكمال المهمة', new_points: DEMO_DATA.user.points + 100 };
    }
    
    // الإعلانات
    if (endpoint === 'ads/list') {
        return { 
            success: true, 
            ads: DEMO_DATA.ads, 
            watched_today: 3, 
            daily_limit: DEMO_DATA.dailyLimit.ads 
        };
    }
    
    if (endpoint === 'ads/watch') {
        return { success: true, reward: 15, new_points: DEMO_DATA.user.points + 15, remaining: 6 };
    }
    
    // عجلة الحظ
    if (endpoint === 'wheel/status') {
        return { success: true, remaining_spins: 3, total_points: DEMO_DATA.user.points };
    }
    
    if (endpoint === 'wheel/spin') {
        const reward = DEMO_DATA.wheelRewards[Math.floor(Math.random() * DEMO_DATA.wheelRewards.length)];
        return { success: true, reward: reward, new_points: DEMO_DATA.user.points + reward, remaining: 2 };
    }
    
    // تحويل النقاط
    if (endpoint === 'wallet/convert') {
        const points = data?.points || 0;
        const ton = points / 10;
        return { success: true, message: `تم تحويل ${points} نقطة إلى ${ton} تون`, ton: ton, points: DEMO_DATA.user.points - points };
    }
    
    // السحب
    if (endpoint === 'wallet/withdraw') {
        return { success: true, withdrawal_id: Date.now(), amount: data?.amount, new_balance: DEMO_DATA.user.ton - (data?.amount || 0) };
    }
    
    if (endpoint === 'wallet/withdrawals') {
        return { 
            success: true, 
            withdrawals: [
                { id: 1, amount: 0.05, wallet_address: "UQ...", status: "completed", requested_at: "2024-01-15" },
                { id: 2, amount: 0.10, wallet_address: "UQ...", status: "pending", requested_at: "2024-01-20" }
            ] 
        };
    }
    
    // الأكواد
    if (endpoint === 'giftcode/redeem') {
        return { success: true, reward_points: 100, reward_ton: 0.01, new_points: DEMO_DATA.user.points + 100, new_ton: DEMO_DATA.user.ton + 0.01 };
    }
    
    // الإحالات
    if (endpoint === 'referrals/stats') {
        return { 
            success: true, 
            total: 3, 
            granted: 2, 
            pending: 1, 
            total_points_earned: 200, 
            total_ton_earned: 0.02,
            referral_link: DEMO_DATA.referralLink,
            referrals: [
                { username: "user1", date: "2024-01-10", status: "مكتمل", reward_points: 100, reward_ton: 0.01 },
                { username: "user2", date: "2024-01-15", status: "مكتمل", reward_points: 100, reward_ton: 0.01 },
                { username: "user3", date: "2024-01-20", status: "قيد الانتظار", reward_points: 100, reward_ton: 0.01 }
            ]
        };
    }
    
    return { success: false, message: 'DEMO: Endpoint not implemented' };
}

// ==================== دوال API الرئيسية ====================

async function getUserData(userId) {
    return await apiCall(`users/me?user_id=${userId}`);
}

async function getTasks(userId) {
    return await apiCall(`tasks/list?user_id=${userId}`);
}

async function completeTask(userId, taskId) {
    return await apiCall('tasks/complete', { user_id: userId, task_id: taskId }, 'POST');
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

async function getReferralStats(userId) {
    return await apiCall(`referrals/stats?user_id=${userId}`);
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

// ==================== التهيئة ====================

document.addEventListener('DOMContentLoaded', function() {
    initTelegram();
    console.log('✅ Config.js loaded - DEMO MODE:', DEMO_MODE);
    console.log('📍 API_URL:', API_URL);
    console.log('📍 Current User:', currentUserId);
});

// تصدير الدوال
window.API_URL = API_URL;
window.DEMO_MODE = DEMO_MODE;
window.getUserData = getUserData;
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
window.getReferralStats = getReferralStats;
window.sendToBot = sendToBot;
window.showAlert = showAlert;
window.goTo = goTo;
window.initTelegram = initTelegram;