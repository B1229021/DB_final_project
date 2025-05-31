const apiBase = 'https://bda5-60-250-225-147.ngrok-free.app/admin_api'; // 換成你 ngrok

function getQueryParam(key) {
    const url = new URL(window.location.href);
    return url.searchParams.get(key);
}
let CURRENT_UID = getQueryParam('uid');
if (document.getElementById('home-link')) {
    document.getElementById('home-link').href = 'index?uid=' + encodeURIComponent(CURRENT_UID);
}

async function api(action, data = {}) {
    const method = ['add_', 'edit_', 'delete_'].some(p => action.startsWith(p)) ? 'POST' : 'GET';
    let fetchParams = {
        method,
        headers: {'Content-Type': 'application/json'},
    };
    let url = apiBase;
    if (method === 'POST') {
        fetchParams.body = JSON.stringify({action, ...data});
    } else {
        url += '?' + new URLSearchParams({action, ...data}).toString();
    }
    let res = await fetch(url, fetchParams);
    if (!res.ok) {
        alert('API error: ' + (await res.text()));
        throw new Error('API error');
    }
    return res.json();
}

// -------- 狀態記錄 --------
let categoryEditMode = false;
let eventEditMode = false;
let userEditMode = false;

// -------- 活動類別 --------
async function loadCategories() {
    const cats = await api('list_categories');
    const tbody = document.getElementById('categories-table-body');
    tbody.innerHTML = '';
    cats.forEach(cat => {
        tbody.innerHTML += `
            <tr data-id="${cat.categories_id}">
                <td>${cat.categories_id}</td>
                <td>
                    <input type="text" value="${cat.content}" 
                        onchange="editCategory(${cat.categories_id}, this.value)"
                        ${categoryEditMode ? '' : 'disabled'}>
                </td>
                <td class="category-action-cell" style="display: ${categoryEditMode ? 'table-cell' : 'none'};">
                    <button type="button" onclick="deleteCategory(${cat.categories_id})">🗑 刪除</button>
                </td>
            </tr>`;
    });
    // 下拉選單同步
    const select = document.getElementById('event-category-select');
    if (select) {
        select.innerHTML = `<option value="">選擇類別</option>` +
            cats.map(cat => `<option value="${cat.categories_id}">${cat.content}</option>`).join('');
    }
    // 控制新增按鈕啟用與否
    const addBtn = document.getElementById('add-category-btn');
    if (addBtn) addBtn.disabled = !categoryEditMode;
}
window.editCategory = async function(id, name) {
    if (!categoryEditMode) return;
    await api('edit_category', {id, name});
    loadCategories();
    loadEvents();
};
window.deleteCategory = async function(id) {
    if (!categoryEditMode) return;
    if (!confirm('確定刪除此類別？')) return;
    await api('delete_category', {id});
    loadCategories();
    loadEvents();
};
document.getElementById('add-category-form').onsubmit = async e => {
    e.preventDefault();
    if (!categoryEditMode) return;
    const name = e.target.new_category_name.value;
    await api('add_category', {name});
    e.target.reset();
    loadCategories();
    loadEvents();
};

// -------- 活動 --------
async function loadEvents() {
    const [cats, events] = await Promise.all([api('list_categories'), api('list_events')]);
    const catsMap = Object.fromEntries(cats.map(c => [c.categories_id, c.content]));
    const tbody = document.getElementById('events-table-body');
    tbody.innerHTML = '';
    events.forEach(ev => {
        tbody.innerHTML += `
            <tr data-id="${ev.event_id}">
                <td>${ev.event_id}</td>
                <td>
                    <select onchange="editEvent(${ev.event_id}, this.value, null)" ${eventEditMode ? '' : 'disabled'}>
                        ${cats.map(c =>
                            `<option value="${c.categories_id}" ${ev.categories_id===c.categories_id?'selected':''}>${c.content}</option>`).join('')}
                    </select>
                </td>
                <td>
                    <input type="text" value="${ev.content}" 
                        onchange="editEvent(${ev.event_id}, null, this.value)"
                        ${eventEditMode ? '' : 'disabled'}>
                </td>
                <td class="event-action-cell" style="display: ${eventEditMode ? 'table-cell' : 'none'};">
                    <button type="button" onclick="deleteEvent(${ev.event_id})">🗑 刪除</button>
                </td>
            </tr>`;
    });
    // 控制新增按鈕啟用與否
    const addBtn = document.getElementById('add-event-btn');
    if (addBtn) addBtn.disabled = !eventEditMode;
}
window.editEvent = async function(id, cat, name) {
    if (!eventEditMode) return;
    const tr = document.querySelector(`tr[data-id="${id}"]`);
    if (!cat) cat = tr.querySelector('select').value;
    if (!name) name = tr.querySelector('input[type=text]').value;
    await api('edit_event', {id, cat, name});
    loadEvents();
};
window.deleteEvent = async function(id) {
    if (!eventEditMode) return;
    if (!confirm('確定刪除此活動？')) return;
    await api('delete_event', {id});
    loadEvents();
};
document.getElementById('add-event-form').onsubmit = async e => {
    e.preventDefault();
    if (!eventEditMode) return;
    const cat = e.target.new_event_category.value;
    const name = e.target.new_event_name.value;
    await api('add_event', {cat, name});
    e.target.reset();
    loadEvents();
};

// -------- 訂單 --------
async function loadOrders() {
    const orders = await api('list_orders');
    const tbody = document.getElementById('orders-table-body');
    tbody.innerHTML = '';
    orders.forEach(row => {
        tbody.innerHTML += `
            <tr>
                <td>${row.orderid}</td>
                <td>${row.username || row.booker}</td>
                <td>${row.location}</td>
                <td>${row.event_id}</td>
                <td>${row.state}</td>
            </tr>
        `;
    });
}

// -------- 評價 --------
async function loadEvals() {
    const evals = await api('list_evals');
    const tbody = document.getElementById('evals-table-body');
    tbody.innerHTML = '';
    evals.forEach(row => {
        tbody.innerHTML += `
            <tr>
                <td>${row.orderid}</td>
                <td>${row.username || row.uid}</td>
                <td>${row.eval_to_booker}</td>
                <td>${row.booker_eval}</td>
                <td>${row.evaluation}</td>
            </tr>
        `;
    });
}

// -------- 使用者 --------
async function loadUsers() {
    const users = await api('list_users');
    const tbody = document.getElementById('users-table-body');
    tbody.innerHTML = '';
    users.forEach(user => {
        tbody.innerHTML += `
            <tr>
                <td>${user.uid}</td>
                <td>${user.username}</td>
                <td>${user.name}</td>
                <td>${user.gender}</td>
                <td>${user.phone}</td>
                <td>${user.identify_ID}</td>
                <td class="user-actions" style="display: ${userEditMode ? 'table-cell' : 'none'};">
                    <button type="button" onclick="deleteUser('${user.uid}')">🗑 刪除</button>
                </td>
            </tr>
        `;
    });
}
window.deleteUser = async function(uid) {
    if (!userEditMode) return;
    if (!confirm('確定刪除此使用者？')) return;
    await api('delete_user', {uid});
    loadUsers();
};

// --------- 編輯欄顯示切換 ---------
window.toggleEditActions = function(sectionClassName, buttonId) {
    if(sectionClassName === 'user') {
        userEditMode = !userEditMode;
        loadUsers();
        // header & button
        const actionHeader = document.querySelector(`.${sectionClassName}-header`);
        const button = document.getElementById(buttonId);
        if (actionHeader) actionHeader.style.display = userEditMode ? 'table-cell' : 'none';
        if (button) button.textContent = userEditMode ? '✅ 完成' : '✏️ 編輯';
    }
};
window.toggleCategoryEdit = function() {
    categoryEditMode = !categoryEditMode;
    loadCategories();
    document.querySelectorAll('.category-action-header').forEach(el => {
        el.style.display = categoryEditMode ? 'table-cell' : 'none';
    });
    const form = document.getElementById('category-form');
    form.style.display = categoryEditMode ? 'block' : 'none';
    const btn = document.querySelector('#category button');
    if (btn) btn.textContent = categoryEditMode ? '✅ 完成' : '✏️ 編輯';
};
window.toggleEventEdit = function() {
    eventEditMode = !eventEditMode;
    loadEvents();
    document.querySelectorAll('.event-action-header').forEach(el => {
        el.style.display = eventEditMode ? 'table-cell' : 'none';
    });
    const form = document.getElementById('event-form');
    form.style.display = eventEditMode ? 'block' : 'none';
    const btn = document.getElementById('toggleEventBtn');
    if (btn) btn.textContent = eventEditMode ? '✅ 完成' : '✏️ 編輯';
};

// ------- 初始化 -------
window.onload = function() {
    loadCategories();
    loadEvents();
    loadOrders();
    loadEvals();
    loadUsers();
};