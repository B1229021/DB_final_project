function getQueryParam(key) {
    const url = new URL(window.location.href);
    return url.searchParams.get(key);
}

// 1. 取得網址中的 userId
let CURRENT_UID = getQueryParam('uid');

const API_BASE_URL = 'https://bda5-60-250-225-147.ngrok-free.app/api'; // 你的ngrok網址
let usersCache = {};
let eventTypeCache = {};


function formatDateTime(dt) {
    if (!dt) return '';
    // 若是數字型（timestamp），直接 new Date
    let d = typeof dt === 'number' ? new Date(dt) : new Date(dt.replace(' ', 'T'));
    if (isNaN(d)) {
        // 嘗試直接 new Date(dt)（給"Fri, 23 May 2025 ..."這種情境）
        d = new Date(dt);
        if (isNaN(d)) return dt; // 還是不行就原樣回傳
    }
    let y = d.getFullYear();
    let m = (d.getMonth() + 1).toString().padStart(2, '0');
    let day = d.getDate().toString().padStart(2, '0');
    let h = d.getHours().toString().padStart(2, '0');
    let min = d.getMinutes().toString().padStart(2, '0');
    return `${y}/${m}/${day} ${h}:${min}`;
}


// --------- 資料加載與快取 ---------
async function loadCategories(retry = 5) {
    try {
        const resp = await fetch(`${API_BASE_URL}/list_categories?_t=${Date.now()}`);
        const cats = await resp.json();
        let html = `<option value="">所有類別</option>`;
        cats.forEach(c => html += `<option value="${c.categories_id}">${c.content}</option>`);
        document.getElementById('categoryFilter').innerHTML = html;
    } catch (err) {
        if (retry > 0) {
            document.getElementById('categoryFilter').innerHTML = `<option value="">分類載入失敗，${retry} 秒後重新嘗試...</option>`;
            setTimeout(() => loadCategories(retry - 1), 3000);
        } else {
            document.getElementById('categoryFilter').innerHTML = `<option value="">分類載入失敗，請稍後再試！</option>`;
            console.error('讀取分類失敗：', err);
        }
    }
}

async function loadEventTypes() {
    const resp = await fetch(`${API_BASE_URL}/list_event_types`);
    const types = await resp.json();
    let html = `<option value="">請選擇</option>`;
    types.forEach(e => {
        html += `<option value="${e.event_id}">${e.content}（${e.category_name}）</option>`;
        eventTypeCache[e.event_id] = e;
    });
    document.getElementById('eventType').innerHTML = html;
}
async function loadUsers() {
    const resp = await fetch(`${API_BASE_URL}/list_users`);    
    const users = await resp.json();
    users.forEach(u => { usersCache[u.uid] = u; });
    document.getElementById('userBtn').textContent = usersCache[CURRENT_UID]?.name || usersCache[CURRENT_UID]?.username || "我的檔案";
}
async function loadEvents(catId = '', time = '') {
    document.getElementById('eventsList').innerHTML = '載入中...';
    let url = `${API_BASE_URL}/list_events`;
    let params = [];
    if (catId) params.push('cat='+encodeURIComponent(catId));
    if (time) params.push('time='+encodeURIComponent(time));
    if (params.length) url += '?' + params.join('&');
    const resp = await fetch(url);
    const events = await resp.json();
    renderEvents(events);
}

// --------- 活動卡片渲染 ---------
function renderEvents(events) {
    const now = new Date();
    let displayEvents = events.filter(event => {
        // 只顯示還沒截止的活動(deadtime尚未過)
        return !event.deadtime || (new Date(event.deadtime) > now);
    });
    if (!displayEvents.length) {
        document.getElementById('eventsList').innerHTML = '<div>目前沒有活動</div>';
        return;
    }
    document.getElementById('eventsList').innerHTML = displayEvents.map(event => {
        // 取得發起人
        let booker = usersCache[event.booker] || {name:"未知", uid: event.booker};
        // 取得參加者名單（排除發起人）
        let participants = (event.participants_list || []).filter(uid => uid !== event.booker).map(uid => usersCache[uid] || {name:"未知", uid});
        // 評價資料格式: {uid: {good:數量, bad:數量}}
        let evaluation = event.evaluation || {};
        // 目前人數＝實際參加者數（不含發起人）
        let total = participants.length;
        let max = event.participants_limit ?? event.participants ?? 0;  
        // 狀態
        let state = event.state || '';
        // 按鈕
        let actionBtn = '';
        if (event.booker === CURRENT_UID) {
            if (state === '已結束') {
                actionBtn = `<span class="btn btn-secondary">活動已結束</span>`;
            } else {
                actionBtn = `
                    <button class="btn btn-danger" onclick="event.stopPropagation(); cancelEvent('${event.orderid}')">取消活動</button>
                    <button class="btn btn-secondary" onclick="event.stopPropagation(); endEvent('${event.orderid}')">結束活動</button>
                `;
            }
        } else if ((event.participants_list || []).includes(CURRENT_UID)) {
            actionBtn = `<button class="btn btn-secondary" onclick="event.stopPropagation(); leaveEvent('${event.orderid}')">取消參與</button>`;
        } else if (total >= max) {
            actionBtn = `<span class="btn btn-secondary">已滿</span>`;
        } else {
            actionBtn = `<button class="btn btn-primary" onclick="event.stopPropagation(); joinEvent('${event.orderid}')">加入 +1</button>`;
        }
        // 名單區
        let memberStr = `
            <span><b>發起人:</b>
                <button class="member-btn" onclick="event.stopPropagation(); gotoProfile('${booker.uid}')">${booker.name||booker.username||'未知'}</button>
                <span class="eval-area">
                    <span class="eval-good">👍${(evaluation[booker.uid]?.good)||0}</span>
                    <span class="eval-bad">👎${(evaluation[booker.uid]?.bad)||0}</span>
                </span>
            </span>
            <br>
            <span><b>參加者:</b>
                ${participants.length ? participants.map(u=>`
                    <button class="member-btn" onclick="event.stopPropagation(); gotoProfile('${u.uid}')">${u.name||u.username||'未知'}</button>
                    <span class="eval-area">
                        <span class="eval-good">👍${(evaluation[u.uid]?.good)||0}</span>
                        <span class="eval-bad">👎${(evaluation[u.uid]?.bad)||0}</span>
                    </span>
                `).join(' ') : '無'}
            </span>
        `;
        return `
        <div class="event-card" onclick="showEventDetail('${event.orderid}')">
            <div class="event-header">
                <span class="event-category">${event.category_name}</span>
                <span class="event-time">${event.deadtime ? event.deadtime.substr(5,11) : ''}</span>
            </div>
            <div class="event-details">
                <div class="event-detail-item"><span class="event-detail-label">活動:</span>
                    <span class="event-detail-value">${event.event_name||''}</span></div>
                <div class="event-detail-item"><span class="event-detail-label">地點:</span>
                    <span class="event-detail-value">${event.location}</span></div>
                <div class="event-detail-item"><span class="event-detail-label">活動開始時間:</span>
                    <span class="event-detail-value">${formatDateTime(event.starttime)}</span></div>
                <div class="event-detail-item"><span class="event-detail-label">表單截止時間:</span>
                    <span class="event-detail-value">${formatDateTime(event.deadtime)}</span></div>
                <div class="event-detail-item"><span class="event-detail-label">說明:</span>
                    <span class="event-detail-value">${event.annotation||''}</span></div>
                <div class="event-detail-item"><span class="event-detail-label">人數:</span>
                    <span class="event-detail-value">${total}/${max}</span></div>
            </div>
            <div style="margin-bottom:6px">${memberStr}</div>
            <div class="form-actions">${actionBtn}</div>
        </div>`;
    }).join('');
}

// --------- 活動詳情 Modal ---------
window.showEventDetail = async function(orderid) {
    const resp = await fetch(`${API_BASE_URL}/event_detail?orderid=${orderid}`);
    const event = await resp.json();
    let booker = usersCache[event.booker] || {name:"未知", uid: event.booker};
    // 只取參與者，不含發起人
    let participants = (event.participants_list || []).filter(uid => uid !== event.booker);
    let evaluation = event.evaluation || {};
    // 依據 usersCache 計算男女參加人數
    let male = participants.filter(uid => usersCache[uid]?.gender === 'M').length;
    let female = participants.filter(uid => usersCache[uid]?.gender === 'F').length;
    let state = event.state || '';
    let total = participants.length;
    let male_limit = event.male_limit || 0;
    let female_limit = event.female_limit || 0;
    let participants_limit = event.participants || (male_limit + female_limit);

    let actionBtn = '';
    if (event.booker === CURRENT_UID) {
        if (state === '已結束') {
            actionBtn = `<span class="btn btn-secondary">活動已結束</span>`;
        } else {
            actionBtn = `
                <button class="btn btn-danger" onclick="event.stopPropagation(); cancelEvent('${event.orderid}')">取消活動</button>
                <button class="btn btn-secondary" onclick="event.stopPropagation(); endEvent('${event.orderid}')">結束活動</button>
            `;
        }
    } else if ((event.participants_list || []).includes(CURRENT_UID)) {
        actionBtn = `<button class="btn btn-secondary" onclick="event.stopPropagation(); leaveEvent('${event.orderid}')">取消參與</button>`;
    } else if (total >= participants_limit) {
        actionBtn = `<span class="btn btn-secondary">已滿</span>`;
    } else {
        actionBtn = `<button class="btn btn-primary" onclick="event.stopPropagation(); joinEvent('${event.orderid}')">加入 +1</button>`;
    }
    let memberStr = `
        <span><b>發起人:</b>
            <button class="member-btn" onclick="gotoProfile('${booker.uid}')">${booker.name||booker.username||'未知'}</button>
            <span class="eval-area">
                <span class="eval-good">👍${(evaluation[booker.uid]?.good)||0}</span>
                <span class="eval-bad">👎${(evaluation[booker.uid]?.bad)||0}</span>
            </span>
        </span>
        <br>
        <span><b>參加者:</b>
            ${participants.length ? participants.map(uid=>{
                let u = usersCache[uid] || {name:"未知", uid};
                return `
                    <button class="member-btn" onclick="gotoProfile('${u.uid}')">${u.name||u.username||'未知'}</button>
                    <span class="eval-area">
                        <span class="eval-good">👍${(evaluation[u.uid]?.good)||0}</span>
                        <span class="eval-bad">👎${(evaluation[u.uid]?.bad)||0}</span>
                    </span>
                `;
            }).join(' ') : '無'}
        </span>
    `;
    document.getElementById('detailContent').innerHTML = `
        <div>
            <div class="event-detail-item"><span class="event-detail-label">活動:</span><span class="event-detail-value">${event.event_name||''}</span></div>
            <div class="event-detail-item"><span class="event-detail-label">地點:</span><span class="event-detail-value">${event.location}</span></div>
            <div class="event-detail-item"><span class="event-detail-label">說明:</span><span class="event-detail-value">${event.annotation||''}</span></div>
            <div class="event-detail-item"><span class="event-detail-label">活動開始時間:</span><span class="event-detail-value">${formatDateTime(event.starttime)}</span></div>
            <div class="event-detail-item"><span class="event-detail-label">表單截止時間:</span><span class="event-detail-value">${formatDateTime(event.deadtime)}</span></div>
            <div class="event-detail-item">
                <span class="event-detail-label">人數:</span>
                <span class="event-detail-value">
                    ${male}/${male_limit} 男，
                    ${female}/${female_limit} 女，
                    總數：${total}/${participants_limit}
                </span>
            </div>
            <div style="margin-bottom:6px">${memberStr}</div>
        </div>
        <div class="form-actions">${actionBtn}<button class="btn btn-secondary" onclick="document.getElementById('detailModal').style.display='none'">關閉</button></div>
    `;
    document.getElementById('detailModal').style.display = 'flex';
};
// --------- 活動參與/取消/結束/取消活動功能 ---------
async function joinEvent(orderid) {
    const resp = await fetch(`${API_BASE_URL}/join_event`, {
        method: 'POST',
        headers: {'Content-Type':'application/x-www-form-urlencoded'},
        body: `orderid=${orderid}&uid=${CURRENT_UID}`
    });
    const result = await resp.json();
    alert(result.message || "加入完成");
    await loadEvents();
}
async function leaveEvent(orderid) {
    const resp = await fetch(`${API_BASE_URL}/leave_event`, {
        method: 'POST',
        headers: {'Content-Type':'application/x-www-form-urlencoded'},
        body: `orderid=${orderid}&uid=${CURRENT_UID}`
    });
    const result = await resp.json();
    alert(result.message || "已取消參與");
    await loadEvents();
}
async function cancelEvent(orderid) {
    if (!confirm("確定要取消這個活動嗎？")) return;
    const resp = await fetch(`${API_BASE_URL}/cancel_event`, {
        method: 'POST',
        headers: {'Content-Type':'application/x-www-form-urlencoded'},
        body: `orderid=${orderid}&uid=${CURRENT_UID}`
    });
    const result = await resp.json();
    alert(result.message || "已取消活動");
    await loadEvents();
}
async function endEvent(orderid) {
    if (!confirm("確定要結束這個活動嗎？")) return;
    try {
        const resp = await fetch(`${API_BASE_URL}/end_event`, {
            method: 'POST',
            headers: {'Content-Type':'application/x-www-form-urlencoded'},
            body: `orderid=${orderid}&uid=${CURRENT_UID}`
        });
        const result = await resp.json();
        alert(result.message || "已結束活動");
        await loadEvents();
    } catch (e) {
        alert("發生錯誤，請稍後再試");
    }
}

// --------- 跳轉個人頁 ---------
function gotoProfile(uid) {
    window.location.href = "profile.html?uid=" + encodeURIComponent(uid);
}

// --------- 歷史紀錄 Modal ---------
document.getElementById('historyBtn').onclick = async function() {
    // 從 API 取得歷史紀錄（僅顯示目前使用者為發起者的活動，含已結束/取消）
    // const resp = await fetch(`${API_BASE_URL}/list_my_events?uid=${CURRENT_UID}`);
    const resp = await fetch(`${API_BASE_URL}/list_my_events?uid=${CURRENT_UID}`);
    const events = await resp.json();
    // 渲染歷史紀錄
    document.getElementById('historyContent').innerHTML = events.length ? events.map(event => {
        let state = event.state || '';
        let actionBtn = '';
        if (state === '已結束') {
            actionBtn = `<span class="btn btn-secondary">活動已結束</span>`;
        } else {
            actionBtn = `
                <button class="btn btn-danger" onclick="endEvent('${event.orderid}')">結束活動</button>
                <button class="btn btn-secondary" onclick="cancelEvent('${event.orderid}')">取消活動</button>
            `;
        }
        return `
            <div class="event-card" style="margin-bottom:10px">
                <div class="event-header">
                    <span class="event-category">${event.category_name}</span>
                    <span class="event-time">${event.deadtime ? event.deadtime.substr(5,11) : ''}</span>
                    <span style="margin-left:20px;">狀態：${state || '進行中'}</span>
                </div>
                <div class="event-details">
                    <div class="event-detail-item"><span class="event-detail-label">活動:</span><span class="event-detail-value">${event.event_name||''}</span></div>
                    <div class="event-detail-item"><span class="event-detail-label">地點:</span><span class="event-detail-value">${event.location}</span></div>
                </div>
                <div class="form-actions">${actionBtn}</div>
            </div>
        `;
    }).join('') : '<div>尚無歷史紀錄</div>';
    document.getElementById('historyModal').style.display = 'flex';
};
document.getElementById('closeHistory').onclick = function() {
    document.getElementById('historyModal').style.display='none';
};

// --------- Modal顯示/隱藏 ---------
document.getElementById('createBtn').onclick = function() { document.getElementById('createModal').style.display='flex'; };
document.getElementById('closeCreate').onclick = function() { document.getElementById('createModal').style.display='none'; };
document.getElementById('cancelCreate').onclick = function() { document.getElementById('createModal').style.display='none'; };
document.getElementById('closeDetail').onclick = function() { document.getElementById('detailModal').style.display='none'; };

window.onclick = function(event) {
    if (event.target.classList.contains('modal')) event.target.style.display = 'none';
};

// --------- 發起活動表單 ---------
document.getElementById('createForm').onsubmit = async function(e) {
    e.preventDefault();
    let form = e.target;
    let participants = parseInt(form.participants.value, 10) || 0;
    let male_limit = parseInt(form.male_limit.value, 10) || 0;
    let female_limit = parseInt(form.female_limit.value, 10) || 0;

    if (participants <= 0) {
        alert("人數限制需大於0！");
        return;
    }
    if (male_limit < 0 || female_limit < 0) {
        alert("男生或女生上限不能為負數！");
        return;
    }
    if (male_limit + female_limit > participants) {
        alert("男生上限加女生上限不可超過人數限制！");
        return;
    }
    let data = new FormData(form);
    data.append('booker', CURRENT_UID);
    data.set('male_limit', male_limit); // 確保數字格式
    data.set('female_limit', female_limit);
    data.set('participants', participants); // 寫入總上限

    const resp = await fetch(`${API_BASE_URL}/create_event`, {
        method: 'POST',
        body: data
    });
    const result = await resp.json();
    alert(result.message || "已發起");
    document.getElementById('createModal').style.display='none';
    await loadEvents();
};

// --------- 篩選與載入 ---------
document.getElementById('filterBtn').onclick = function() {
    const cat = document.getElementById('categoryFilter').value;
    const time = document.getElementById('timeFilter').value;
    loadEvents(cat, time);
};
document.getElementById('refreshBtn').onclick = function() {
    loadEvents();
};
document.getElementById('adminBtn').onclick = function() {
    if (usersCache[CURRENT_UID]?.isadmin=='1') {
        window.location.href = 'admin?uid=' + encodeURIComponent(CURRENT_UID);
    } else {
        alert("您無管理員權限！");
    }
};
document.getElementById('userBtn').onclick = function() {
    gotoProfile(CURRENT_UID);
};

// --------- 頁面初始化 ---------
window.onload = async function() {
    await loadCategories();
    await loadEventTypes();
    await loadUsers();
    await loadEvents();
};