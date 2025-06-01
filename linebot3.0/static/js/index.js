function getQueryParam(key) {
    const url = new URL(window.location.href);
    return url.searchParams.get(key);
}

// 1. 取得網址中的 userId
let CURRENT_UID = getQueryParam('uid');

const API_BASE_URL = 'https://c3d4-60-250-225-145.ngrok-free.app/api'; // 你的ngrok網址
let usersCache = {};
let eventTypeList = [];

function formatDateTime(dt) {
    if (!dt) return '';
    // 只針對 ISO 格式處理
    if (dt.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/)) {
        return dt.replace('T', ' ').replace(/-/g, '/');
    }
    return dt;
}

// 載入分類
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

// 載入活動類型
async function loadEventTypes() {
    const resp = await fetch(`${API_BASE_URL}/list_event_types`);
    const types = await resp.json();
    eventTypeList = types;
    renderEventTypeOptions();
}

// 依選擇的分類渲染活動類型選單
function renderEventTypeOptions(selectedCatId = "") {
    let eventTypeSel = document.getElementById('eventTypeFilter');
    let html = `<option value="">所有活動類型</option>`;
    let filtered = selectedCatId
        ? eventTypeList.filter(e => String(e.categories_id) === String(selectedCatId))
        : eventTypeList;
    filtered.forEach(e => {
        html += `<option value="${e.event_id}">${e.content}（${e.category_name}）</option>`;
    });
    eventTypeSel.innerHTML = html;
}

// 當類別選單改變，活動類型選單跟著變
document.getElementById('categoryFilter').addEventListener('change', function() {
    renderEventTypeOptions(this.value);
    document.getElementById('eventTypeFilter').value = "";
});

// 若直接選活動類型，類別自動切到該活動所屬
document.getElementById('eventTypeFilter').addEventListener('change', function() {
    let selectedEvent = eventTypeList.find(e => String(e.event_id) === String(this.value));
    if (selectedEvent) {
        document.getElementById('categoryFilter').value = selectedEvent.categories_id;
        renderEventTypeOptions(selectedEvent.categories_id);
        document.getElementById('eventTypeFilter').value = selectedEvent.event_id;
    }
});

// 發起活動表單的分類與活動類型
async function loadCreateCategories() {
    const resp = await fetch(`${API_BASE_URL}/list_categories?_t=${Date.now()}`);
    const cats = await resp.json();
    let html = `<option value="">請選擇類別</option>`;
    cats.forEach(c => html += `<option value="${c.categories_id}">${c.content}</option>`);
    document.getElementById('createCategory').innerHTML = html;
}
function renderCreateEventTypeOptions(selectedCatId = "") {
    let eventTypeSel = document.getElementById('createEventType');
    let html = `<option value="">請選擇活動類型</option>`;
    let filtered = selectedCatId
        ? eventTypeList.filter(e => String(e.categories_id) === String(selectedCatId))
        : eventTypeList;
    filtered.forEach(e => {
        html += `<option value="${e.event_id}">${e.content}（${e.category_name}）</option>`;
    });
    eventTypeSel.innerHTML = html;
}
document.getElementById('createCategory').addEventListener('change', function () {
    renderCreateEventTypeOptions(this.value);
    document.getElementById('createEventType').value = "";
});
document.getElementById('createEventType').addEventListener('change', function () {
    let selectedEvent = eventTypeList.find(e => String(e.event_id) === String(this.value));
    if (selectedEvent) {
        document.getElementById('createCategory').value = selectedEvent.categories_id;
        renderCreateEventTypeOptions(selectedEvent.categories_id);
        document.getElementById('createEventType').value = selectedEvent.event_id;
    }
});

// 載入用戶快取
async function loadUsers() {
    const resp = await fetch(`${API_BASE_URL}/list_users`);    
    const users = await resp.json();
    users.forEach(u => { usersCache[u.uid] = u; });
    document.getElementById('userBtn').textContent = usersCache[CURRENT_UID]?.name || usersCache[CURRENT_UID]?.username || "我的檔案";
}

// 自動結束活動
async function endEventAuto(orderid, bookerUid) {
    try {
        await fetch(`${API_BASE_URL}/end_event`, {
            method: 'POST',
            headers: {'Content-Type':'application/x-www-form-urlencoded'},
            body: `orderid=${orderid}&uid=${bookerUid || CURRENT_UID}`
        });
    } catch (e) {
        console.error('自動結束活動失敗', e);
    }
}

// 自動判斷所有活動（events）是否需要結束
async function autoEndEvents(events) {
    const now = new Date();
    let hasEnded = false;
    for (const event of events) {
        if (event.deadtime && new Date(event.deadtime) < now && event.state !== '已結束') {
            await endEventAuto(event.orderid, event.booker);
            hasEnded = true;
        }
    }
    return hasEnded;
}

// 活動列表加載
async function loadEvents(catId = '', time = '', eventTypeId = '') {
    document.getElementById('eventsList').innerHTML = '載入中...';
    let url = `${API_BASE_URL}/list_events`;
    let params = [];
    if (catId) params.push('cat=' + encodeURIComponent(catId));
    if (time) params.push('time=' + encodeURIComponent(time));
    if (params.length) url += '?' + params.join('&');
    const resp = await fetch(url);
    let events = await resp.json();

    // 先自動結束過期活動
    const hasEnded = await autoEndEvents(events);
    if (hasEnded) {
        // 有活動剛剛自動結束，再重抓一次
        return await loadEvents(catId, time, eventTypeId);
    }

    // 前端再依活動類型過濾
    if (eventTypeId) {
        events = events.filter(e => String(e.event_id) === String(eventTypeId));
    }


 /////////////////////////////////////////////////排序
    events.sort((a, b) => {
        if (!a.deadtime) return 1;
        if (!b.deadtime) return -1;
        return new Date(a.deadtime) - new Date(b.deadtime);
    });

    renderEvents(events);
}

// 主畫面篩選按鈕
document.getElementById('filterBtn').onclick = function () {
    const cat = document.getElementById('categoryFilter').value;
    const eventTypeId = document.getElementById('eventTypeFilter').value;
    const time = document.getElementById('timeFilter').value;
    loadEvents(cat, time, eventTypeId);
};
document.getElementById('refreshBtn').onclick = function () {
    loadEvents();
}

// 活動卡片渲染
function renderEvents(events) {
    const now = new Date();
    let displayEvents = events.filter(event => {
        if (event.state === '已結束') return false;
        let total = (event.participants_list || []).length;
        let max = event.participants_limit ?? event.participants ?? 0;
        let isJoiner = (event.participants_list || []).includes(CURRENT_UID);
        let isOwner = (event.booker === CURRENT_UID);
        // 已滿而且我不是參與者、也不是發起人，就隱藏
        if (total >= max && !isJoiner && !isOwner) return false;
        return !event.deadtime || (new Date(event.deadtime) > now);
    });
    if (!displayEvents.length) {
        document.getElementById('eventsList').innerHTML = '<div>目前沒有活動</div>';
        return;
    }
    document.getElementById('eventsList').innerHTML = displayEvents.map(event => {
        let booker = usersCache[event.booker] || {name:"未知", uid: event.booker};
        let participants = (event.participants_list || []).filter(uid => uid !== event.booker).map(uid => usersCache[uid] || {name:"未知", uid});
        let total = participants.length;
        let max = event.participants_limit ?? event.participants ?? 0;
        let state = event.state || '';
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
        let memberStr = `
            <span><b>發起人:</b>
                <button class="member-btn" onclick="event.stopPropagation(); gotoProfile('${booker.uid}')">${booker.name||booker.username||'未知'}</button>
            </span>
            <br>
            <span><b>參加者:</b>
                ${participants.length ? participants.map(u=>`
                    <button class="member-btn" onclick="event.stopPropagation(); gotoProfile('${u.uid}')">${u.name||u.username||'未知'}</button>
                `).join(' ') : '無'}
            </span>
        `;
        return `
        <div class="event-card" onclick="showEventDetail('${event.orderid}')">
            <div class="event-header">
                <span class="event-category">${event.category_name || "無分類"}</span>
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
                    <span class="event-detail-value">${
                        String(event.gender_limit) === "1"
                        ? `${event.male_num||0}/${event.male_limit||0} 男，${event.female_num||0}/${event.female_limit||0} 女`
                        : `總數：${total}/${max}`
                    }</span>
                </div>
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
    let participants = (event.participants_list || []);
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
    // 名單區（移除評價顯示）
    let memberStr = `
        <span><b>發起人:</b>
            <button class="member-btn" onclick="gotoProfile('${booker.uid}')">${booker.name||booker.username||'未知'}</button>
        </span>
        <br>
        <span><b>參加者:</b>
            ${participants.length ? participants.map(uid=>{
                let u = usersCache[uid] || {name:"未知", uid};
                return `
                    <button class="member-btn" onclick="gotoProfile('${u.uid}')">${u.name||u.username||'未知'}</button>
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
                    ${
                    String(event.gender_limit) === "1"
                        ? `${male}/${male_limit} 男，${female}/${female_limit} 女`
                        : `總數：${total}/${participants_limit}`
                    }
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
function gotoProfile(targetUid) {
    const url = new URL(window.location.href);
    const myUid = url.searchParams.get("uid");
    if (!myUid) {
        alert("缺少 uid，請從首頁進入！");
        return;
    }
    if (myUid === targetUid) {
        window.location.href = "profile?uid=" + encodeURIComponent(myUid);
    } else {
        window.location.href = "profile?uid=" + encodeURIComponent(myUid) + "&other_uid=" + encodeURIComponent(targetUid);
    }
}

// --------- 歷史紀錄 Modal ---------
document.getElementById('historyBtn').onclick = async function() {
    const resp = await fetch(`${API_BASE_URL}/list_my_events?uid=${CURRENT_UID}`);
    const events = await resp.json();
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


// 取得欄位
const genderLimitSwitch = document.getElementById('genderLimitSwitch');
const participantsRow = document.getElementById('participantsRow');
const genderRows = document.getElementById('genderRows');
const maleLimitInput = document.getElementById('male_limit');
const femaleLimitInput = document.getElementById('female_limit');
const participantsInput = document.getElementById('participants');


// 性別限制切換時，顯示正確欄位並同步 participants
genderLimitSwitch.addEventListener('change', function() {
  if (this.checked) {
    genderRows.style.display = '';
    participantsRow.style.display = 'none';
    // 性別限制啟用，participants自動等於男+女
    participantsInput.value = Number(maleLimitInput.value) + Number(femaleLimitInput.value);
  } else {
    genderRows.style.display = 'none';
    participantsRow.style.display = '';
  }
});

// 男/女上限變動時同步 participants
function updateParticipants() {
  if (genderLimitSwitch.checked) {
    let m = Number(maleLimitInput.value) || 0;
    let f = Number(femaleLimitInput.value) || 0;
    participantsInput.value = m + f;
  }
}
maleLimitInput.addEventListener('input', updateParticipants);
femaleLimitInput.addEventListener('input', updateParticipants);


// --------- 發起活動表單 ---------
document.getElementById('createForm').onsubmit = async function(e) {
    e.preventDefault();
    let form = e.target;
    // 性別限制判斷
    let gender_limit = genderLimitSwitch.checked ? 1 : 0;
    let male_limit = gender_limit ? parseInt(maleLimitInput.value, 10) || 0 : 0;
    let female_limit = gender_limit ? parseInt(femaleLimitInput.value, 10) || 0 : 0;
    let participants = gender_limit
      ? male_limit + female_limit
      : parseInt(participantsInput.value, 10) || 0;

    // 驗證
    if (gender_limit) {
        if (male_limit < 0 || female_limit < 0) {
            alert("男生或女生上限不能為負數！");
            return;
        }
        if (participants < 1) {
            alert("男生上限+女生上限至少1人！");
            return;
        }
    } else {
        if (participants < 1) {
            alert("人數限制最少為 1！");
            return;
        }
    }
    let start_time = form.start_time.value;
    let deadtime = form.deadtime.value;
    if (deadtime && start_time && deadtime > start_time) {
        alert("表單截止時間不能大於活動開始時間！");
        return;
    }
    let categories_id = form.categories_id ? form.categories_id.value : document.getElementById('createCategory').value;
    let event_id = form.event_id ? form.event_id.value : document.getElementById('createEventType').value;
    if (!categories_id || !event_id) {
        alert('請選擇類別與活動類型');
        return;
    }

    // 準備資料送出
    let data = new FormData(form);
    data.append('booker', CURRENT_UID);
    data.set('categories_id', categories_id);
    data.set('event_id', event_id);
    data.set('gender_limit', gender_limit);
    data.set('male_limit', male_limit);
    data.set('female_limit', female_limit);
    data.set('participants', participants); // 後端必需用這欄

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
window.onload = async function () {
    await loadCategories();
    await loadEventTypes();
    await loadUsers();
    await loadEvents();
    await loadCreateCategories();
    renderCreateEventTypeOptions();

    document.getElementById('categoryFilter').addEventListener('change', function () {
        renderEventTypeOptions(this.value);
        document.getElementById('eventTypeFilter').value = "";
    });
    document.getElementById('eventTypeFilter').addEventListener('change', function () {
        let selectedEvent = eventTypeList.find(e => String(e.event_id) === String(this.value));
        if (selectedEvent) {
            document.getElementById('categoryFilter').value = selectedEvent.categories_id;
            renderEventTypeOptions(selectedEvent.categories_id);
            document.getElementById('eventTypeFilter').value = selectedEvent.event_id;
        }
    });
    document.getElementById('createCategory').addEventListener('change', function () {
        renderCreateEventTypeOptions(this.value);
        document.getElementById('createEventType').value = "";
    });
    document.getElementById('createEventType').addEventListener('change', function () {
        let selectedEvent = eventTypeList.find(e => String(e.event_id) === String(this.value));
        if (selectedEvent) {
            document.getElementById('createCategory').value = selectedEvent.categories_id;
            renderCreateEventTypeOptions(selectedEvent.categories_id);
            document.getElementById('createEventType').value = selectedEvent.event_id;
        }
    });
};