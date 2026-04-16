// ==================== config.js ====================
// إعدادات البوت والتطبيق - النسخة النهائية

// 🔴 إعدادات API
const API_URL = 'https://krista-arrhenotokous-superficially.ngrok-free.dev/api';
const BOT_USERNAME = 'Youlim5_bot';
const APP_URL = 'https://melodic-llama-b16158.netlify.app';

// ==================== دوال API الأساسية ====================

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
        console.log(`📡 API Call: ${method} ${url}`, data);
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
    return await apiCall(`user?user_id=${userId}`, null, 'GET');
}

async function getReferralStats(userId) {
    return await apiCall(`referral_stats?user_id=${userId}`, null, 'GET');
}

async function watchAd(userId, company = '', reward = 15) {
    return await apiCall('watch_ad', { user_id: userId, company: company, reward: reward }, 'POST');
}

async function spinWheel(userId) {
    return await apiCall('spin_wheel', { user_id: userId }, 'POST');
}

async function getWheelStatus(userId) {
    return await apiCall(`wheel_status?user_id=${userId}`, null, 'GET');
}

async function convertPoints(userId, points) {
    return await apiCall('convert', { user_id: userId, points: points }, 'POST');
}

async function requestWithdraw(userId, amount, wallet, username) {
    return await apiCall('request_withdraw', { user_id: userId, amount: amount, wallet: wallet, username: username }, 'POST');
}

async function getUserWithdrawals(userId) {
    return await apiCall(`withdrawals?user_id=${userId}`, null, 'GET');
}

async function getTasks(userId) {
    return await apiCall(`tasks?user_id=${userId}`, null, 'GET');
}

async function completeTask(userId, taskId, reward) {
    return await apiCall('complete_task', { user_id: userId, task_id: taskId, reward: reward }, 'POST');
}

async function redeemCode(userId, code) {
    return await apiCall('redeem_code', { user_id: userId, code: code }, 'POST');
}

async function getAds(userId) {
    return await apiCall(`ads?user_id=${userId}`, null, 'GET');
}

async function claimAds(userId, points) {
    return await apiCall('claim_ads', { user_id: userId, points: points }, 'POST');
}

// ==================== دوال WebApp ====================

let tg = null;
let currentUser = null;

function initWebApp() {
    if (window.Telegram && window.Telegram.WebApp) {
        tg = window.Telegram.WebApp;
        tg.expand();
        tg.ready();
        
        if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
            currentUser = tg.initDataUnsafe.user;
            window.currentUserId = currentUser.id;
            console.log('✅ Telegram user loaded:', currentUser.id);
        }
    }
    
    // للاختبار في المتصفح
    if (!currentUser) {
        const testId = localStorage.getItem('testUserId');
        if (testId) {
            currentUser = { id: parseInt(testId), username: 'TestUser', first_name: 'Test' };
        } else {
            currentUser = { id: 8268443100, username: 'Admin', first_name: 'Admin' };
        }
        window.currentUserId = currentUser.id;
        console.log('⚠️ Browser mode - using test user:', currentUser.id);
    }
    
    return tg;
}

function getUser() {
    return currentUser;
}

function showAlert(message) {
    if (tg && tg.showAlert) {
        tg.showAlert(message);
    } else {
        alert(message);
    }
}

function sendToBot(action, data) {
    const message = JSON.stringify({ action: action, ...data });
    if (tg && tg.sendData) {
        tg.sendData(message);
    }
    console.log('📤 Send to bot:', message);
}

// ==================== التنقل بين الصفحات ====================

function goTo(page) {
    console.log('🔄 goTo called:', page);
    
    const pages = {
        'home': `${APP_URL}/index.html`,
        'tasks': `${APP_URL}/tasks.html`,
        'wheel': `${APP_URL}/wheel.html`,
        'ads': `${APP_URL}/ads.html`,
        'withdraw': `${APP_URL}/withdraw.html`,
        'referral': `${APP_URL}/referral.html`,
        'giftcode': `${APP_URL}/giftcode.html`,
        'admin': `${APP_URL}/admin.html`
    };
    
    if (pages[page]) {
        window.location.href = pages[page];
    } else {
        console.error('Page not found:', page);
        showAlert('الصفحة غير موجودة');
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

// ==================== تحديث واجهة المستخدم ====================

function updateUserUI(data) {
    if (data.ton !== undefined) {
        const tonEl = document.getElementById('tonBalance');
        if (tonEl) tonEl.innerText = data.ton.toFixed(4);
    }
    if (data.points !== undefined) {
        const pointsEl = document.getElementById('pointsBalance');
        if (pointsEl) pointsEl.innerText = Math.floor(data.points);
    }
    if (data.total_referrals !== undefined) {
        const refEl = document.getElementById('totalReferrals');
        if (refEl) refEl.innerText = data.total_referrals;
    }
    if (data.active_referrals !== undefined) {
        const activeEl = document.getElementById('activeReferrals');
        if (activeEl) activeEl.innerText = data.active_referrals;
    }
    if (data.ads_watched !== undefined) {
        const progress = (data.ads_watched / 10) * 100;
        const fillEl = document.getElementById('adsProgressFill');
        if (fillEl) fillEl.style.width = progress + '%';
        const watchedEl = document.getElementById('adsWatched');
        if (watchedEl) watchedEl.innerText = data.ads_watched;
        const remainingEl = document.getElementById('adsRemaining');
        if (remainingEl) remainingEl.innerText = 10 - data.ads_watched;
    }
}

// ==================== تحميل البيانات ====================

async function loadUserData(userId) {
    const result = await getUserData(userId);
    if (result.success) {
        updateUserUI(result);
    } else {
        console.error('Failed to load user data:', result.message);
    }
    return result;
}

// ==================== دوال اللغة ====================

let currentLanguage = localStorage.getItem('language') || 'ar';

const translations = {
    ar: {
        ton: 'TON',
        points: 'نقاط',
        convert: 'تحويل النقاط → تون',
        convertRate: '(1 تون = 10 نقاط)',
        progressTitle: 'تقدم مشاهدة الإعلانات',
        watched: 'تم المشاهدة',
        remaining: 'المتبقي',
        target: 'الهدف',
        totalReferrals: 'إجمالي الإحالات',
        activeReferrals: 'إحالات نشطة',
        giftcode: 'قيفت كود',
        referral: 'ريفيرال',
        tasks: 'المهام',
        wheel: 'عجلة الحظ',
        navHome: 'الرئيسية',
        navTasks: 'المهام',
        navWheel: 'عجلة',
        navAds: 'إعلانات',
        navAdmin: 'أدمن',
        langBtn: 'EN',
        withdraw: 'سحب',
        balance: 'الرصيد',
        history: 'التاريخ',
        copy: 'نسخ',
        share: 'مشاركة'
    },
    en: {
        ton: 'TON',
        points: 'Points',
        convert: 'Convert Points → TON',
        convertRate: '(1 TON = 10 Points)',
        progressTitle: 'Ads Progress',
        watched: 'Watched',
        remaining: 'Remaining',
        target: 'Target',
        totalReferrals: 'Total Referrals',
        activeReferrals: 'Active Referrals',
        giftcode: 'Gift Code',
        referral: 'Referral',
        tasks: 'Tasks',
        wheel: 'Wheel',
        navHome: 'Home',
        navTasks: 'Tasks',
        navWheel: 'Wheel',
        navAds: 'Ads',
        navAdmin: 'Admin',
        langBtn: 'عربي',
        withdraw: 'Withdraw',
        balance: 'Balance',
        history: 'History',
        copy: 'Copy',
        share: 'Share'
    }
};

function toggleLanguage() {
    currentLanguage = currentLanguage === 'ar' ? 'en' : 'ar';
    localStorage.setItem('language', currentLanguage);
    updateUILanguage();
}

function updateUILanguage() {
    const t = translations[currentLanguage];
    
    // تحديث زر اللغة
    const langBtn = document.querySelector('.lang-btn');
    if (langBtn) langBtn.innerHTML = `<i class="fas fa-globe"></i> ${t.langBtn}`;
    
    // تحديث النصوص حسب وجود العناصر في الصفحة
    const elements = {
        'tonLabel': t.ton,
        'pointsLabel': t.points,
        'convertText': t.convert,
        'convertRate': t.convertRate,
        'progressTitle': t.progressTitle,
        'watchedLabel': t.watched,
        'remainingLabel': t.remaining,
        'targetLabel': t.target,
        'totalReferralsLabel': t.totalReferrals,
        'activeReferralsLabel': t.activeReferrals,
        'giftcodeLabel': t.giftcode,
        'referralLabel': t.referral,
        'tasksLabel': t.tasks,
        'wheelLabel': t.wheel,
        'navHome': t.navHome,
        'navTasks': t.navTasks,
        'navWheel': t.navWheel,
        'navAds': t.navAds,
        'navAdmin': t.navAdmin
    };
    
    for (const [id, text] of Object.entries(elements)) {
        const el = document.getElementById(id);
        if (el) el.innerText = text;
    }
    
    // تغيير اتجاه الصفحة
    if (currentLanguage === 'ar') {
        document.body.dir = 'rtl';
        document.documentElement.lang = 'ar';
    } else {
        document.body.dir = 'ltr';
        document.documentElement.lang = 'en';
    }
}

// ==================== التهيئة ====================

// تهيئة WebApp عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    initWebApp();
    updateUILanguage();
    console.log('✅ Config.js loaded');
    console.log('📍 API_URL:', API_URL);
    console.log('📍 BOT_USERNAME:', BOT_USERNAME);
    console.log('📍 APP_URL:', APP_URL);
});

// تصدير الدوال للاستخدام العالمي
window.apiCall = apiCall;
window.getUserData = getUserData;
window.getReferralStats = getReferralStats;
window.watchAd = watchAd;
window.spinWheel = spinWheel;
window.getWheelStatus = getWheelStatus;
window.convertPoints = convertPoints;
window.requestWithdraw = requestWithdraw;
window.getUserWithdrawals = getUserWithdrawals;
window.getTasks = getTasks;
window.completeTask = completeTask;
window.redeemCode = redeemCode;
window.getAds = getAds;
window.claimAds = claimAds;
window.initWebApp = initWebApp;
window.getUser = getUser;
window.showAlert = showAlert;
window.sendToBot = sendToBot;
window.goTo = goTo;
window.goBack = goBack;
window.formatNumber = formatNumber;
window.formatDate = formatDate;
window.updateUserUI = updateUserUI;
window.loadUserData = loadUserData;
window.toggleLanguage = toggleLanguage;
window.updateUILanguage = updateUILanguage;

// متغيرات عامة
window.BOT_USERNAME = BOT_USERNAME;
window.APP_URL = APP_URL;
window.API_URL = API_URL;
window.currentLanguage = currentLanguage;