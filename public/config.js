// public/config.js
// إعدادات الواجهة الأمامية - وضع الاتصال الحقيقي بالخادم

// ==================== إعدادات التطبيق ====================

// تفعيل الوضع التجريبي (false = الاتصال بالخادم الحقيقي)
const DEMO_MODE = false;

// رابط API الخلفي (VPS)
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
    
    if (window.opener && !window.opener.closed) {
        window.opener.postMessage({ 
            type: 'UPDATE_BALANCE', 
            points: newPoints,
            ton: current.ton
        }, '*');
    }
    
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

// ==================== دوال المستخدم (مسارات متوافقة مع bot.py) ====================

async function getUserData(userId) {
    return await apiCall(`user?user_id=${userId}`);
}

async function getReferralStats(userId) {
    return await apiCall(`referral_stats?user_id=${userId}`);
}

async function getTasks(userId) {
    return await apiCall(`tasks?user_id=${userId}`);
}

async function completeTask(userId, taskId) {
    return await apiCall(`complete_task`, { user_id: userId, task_id: taskId }, 'POST');
}

async function getAds(userId) {
    return await apiCall(`ads?user_id=${userId}`);
}

async function watchAd(userId, reward = 15) {
    return await apiCall(`watch_ad`, { user_id: userId, reward: reward }, 'POST');
}

async function getWheelStatus(userId) {
    return await apiCall(`wheel_status?user_id=${userId}`);
}

async function spinWheel(userId) {
    return await apiCall(`spin_wheel`, { user_id: userId }, 'POST');
}

async function convertPoints(userId, points) {
    return await apiCall(`convert`, { user_id: userId, points: points }, 'POST');
}

async function requestWithdraw(userId, amount, wallet, username) {
    return await apiCall(`request_withdraw`, { user_id: userId, amount: amount, wallet_address: wallet, username: username }, 'POST');
}

async function getUserWithdrawals(userId) {
    return await apiCall(`withdrawals?user_id=${userId}`);
}

async function redeemCode(userId, code) {
    return await apiCall(`redeem_code`, { user_id: userId, code: code }, 'POST');
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

// ==================== دوال التنبيه والإشعارات ====================

function showAlert(message) {
    if (tg && tg.showAlert) {
        try {
            tg.showAlert(message);
            return;
        } catch(e) {
            console.log('Telegram showAlert failed, using fallback');
        }
    }
    
    showCustomAlert(message);
}

function showCustomAlert(message) {
    let existingAlert = document.getElementById('customAlert');
    if (existingAlert) {
        existingAlert.remove();
    }
    
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
                <div style="font-size: 32px; margin-bottom: 15px;">📢</div>
                <div style="color: white; margin-bottom: 20px; line-height: 1.5; font-size: 16px;">${message}</div>
                <button onclick="this.closest('#customAlert').remove()" style="
                    background: linear-gradient(135deg, #00BFFF, #0088aa);
                    border: none;
                    padding: 10px 25px;
                    border-radius: 50px;
                    color: white;
                    font-weight: bold;
                    cursor: pointer;
                    font-size: 14px;
                ">حسناً</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(alertDiv);
    
    alertDiv.addEventListener('click', function(e) {
        if (e.target === alertDiv) {
            alertDiv.remove();
        }
    });
}

function showConfirm(message, callback) {
    if (tg && tg.showConfirm) {
        try {
            tg.showConfirm(message, callback);
            return;
        } catch(e) {
            console.log('Telegram showConfirm failed, using fallback');
        }
    }
    
    showCustomConfirm(message, callback);
}

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
                <div style="font-size: 32px; margin-bottom: 15px;">❓</div>
                <div style="color: white; margin-bottom: 20px; line-height: 1.5; font-size: 16px;">${message}</div>
                <div style="display: flex; gap: 15px; justify-content: center;">
                    <button id="confirmYes" style="
                        background: linear-gradient(135deg, #2ecc71, #27ae60);
                        border: none;
                        padding: 8px 25px;
                        border-radius: 50px;
                        color: white;
                        font-weight: bold;
                        cursor: pointer;
                    ">نعم</button>
                    <button id="confirmNo" style="
                        background: linear-gradient(135deg, #e74c3c, #c0392b);
                        border: none;
                        padding: 8px 25px;
                        border-radius: 50px;
                        color: white;
                        font-weight: bold;
                        cursor: pointer;
                    ">لا</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(confirmDiv);
    
    document.getElementById('confirmYes').onclick = () => {
        confirmDiv.remove();
        callback(true);
    };
    document.getElementById('confirmNo').onclick = () => {
        confirmDiv.remove();
        callback(false);
    };
    
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
    
    window.addEventListener('message', function(event) {
        if (event.data && event.data.type === 'UPDATE_BALANCE') {
            console.log('📨 Received balance update:', event.data);
            if (event.data.points !== undefined) {
                localStorage.setItem(`points_${currentUserId}`, event.data.points);
            }
            if (event.data.ton !== undefined) {
                localStorage.setItem(`ton_${currentUserId}`, event.data.ton);
            }
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