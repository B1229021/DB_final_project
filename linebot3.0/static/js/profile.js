const apiBase = 'https://c3d4-60-250-225-145.ngrok-free.app/admin_api'; // 換成你 ngrok

function toggleEdit() {
    const view = document.getElementById('view-mode');
    const edit = document.getElementById('edit-mode');
    if (view && edit) {
        view.style.display = (view.style.display === 'none') ? 'block' : 'none';
        edit.style.display = (edit.style.display === 'none') ? 'block' : 'none';
    }
}

// 取得網址參數
function getQueryParam(key) {
    const url = new URL(window.location.href);
    return url.searchParams.get(key);
}

// 取得自己的 uid
let UID = getQueryParam('uid');
// 預覽的對象（被預覽的人），沒有就等於自己
let OTHER_UID = getQueryParam('other_uid') || UID;

// 組成目前 profile 頁面的網址
let link;
if (OTHER_UID === UID) {
    // 看自己
    link = `/profile?uid=${encodeURIComponent(UID)}`;
} else {
    // 預覽他人
    link = `/profile?uid=${encodeURIComponent(UID)}&other_uid=${encodeURIComponent(OTHER_UID)}`;
}

// 設定回首頁按鈕（帶自己的 uid）
let homeUrl = '/index';
if (UID) {
    homeUrl += '?uid=' + encodeURIComponent(UID);
}
const homeLink = document.getElementById('home-link');
if (homeLink) {
    homeLink.href = homeUrl;
}