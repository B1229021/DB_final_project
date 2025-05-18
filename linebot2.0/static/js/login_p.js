const urlParams = new URLSearchParams(window.location.search);
const u_id = urlParams.get('u_id');

// 如果 URL 有帶 line_id，則自動填入隱藏欄位
// if (u_id) {
//     console.log("取得的 u_id:", u_id);
//     document.getElementById('u_id').value = u_id;
// } else {
//     alert("密碼錯誤，請重新登入");
// }

// // 表單提交監聽事件
// document.getElementById('loginForm').addEventListener('submit', function (e) {
//     if (!u_id) {
//         e.preventDefault();
//         alert("Line ID 遺失，無法提交資料");
//     }
// });