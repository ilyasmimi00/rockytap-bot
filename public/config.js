// frontend/config.js
// إعدادات الواجهة الأمامية - متصلة بالـ API الجديد

// ==================== إعدادات التطبيق ====================

// رابط API الخلفي (VPS)
const API_URL = 'http://158.220.120.209:5000/api';

// رابط التطبيق على Cloudflare
const APP_URL = 'https://rockytap-bot.elias-guerbas.workers.dev';

// اسم البوت
const BOT_USERNAME = 'RockyTap_bot';

// ==================== دوال API ====================

async function apiCall(endpoint, data = null, method = 'GET') {
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

// ==================== التهيئة ====================

document.addEventListener('DOMContentLoaded', function() {
    initTelegram();
    console.log('✅ Config.js loaded');
    console.log('📍 API_URL:', API_URL);
    console.log('📍 Current User:', currentUserId);
});

// تصدير الدوال
window.API_URL = API_URL;
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
window.initTelegram = initTelegram;