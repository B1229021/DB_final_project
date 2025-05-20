const urlParams = new URLSearchParams(window.location.search);
const u_id = urlParams.get('u_id');
const NGROK_URL = 'https://7244-61-218-122-234.ngrok-free.app'; // ← 替換成你自己的 ngrok URL

$(function () {
    // 載入教授資料
    $.ajax({
        type: 'GET',
        url: `${NGROK_URL}/action.php`,
        data: { act: 'professor' },
        dataType: 'json',
        success: function (result) {
            const deps = new Set(result.map(p => p.department));
            deps.forEach(dep => {
                $('#department').append(`<option value="${dep}">${dep}</option>`);
            });
        }
    });

    $('#department').change(function () {
        const dep = $(this).val();
        $('#title').empty().append('<option value="" hidden>請選擇職稱</option>');
        $('#name').empty().append('<option value="" hidden>請選擇教授</option>');
        if (!dep) return;

        $.get(`${NGROK_URL}/action.php`, { act: 'title', val: dep }, function (result) {
            result.forEach(item => {
                $('#title').append(`<option value="${item.id}">${item.title}</option>`);
            });
        }, 'json');
    });

    $('#title').change(function () {
        const title = $(this).val();
        $('#name').empty().append('<option value="" hidden>請選擇教授</option>');
        if (!title) return;

        $.get(`${NGROK_URL}/action.php`, { act: 'name', val: title }, function (result) {
            result.forEach(item => {
                $('#name').append(`<option value="${item.id}">${item.name}</option>`);
            });
        }, 'json');
    });

    // 顏色標記
    $('.time-slot').each(function () {
        const state = $(this).data('state');
        if (state === 'available') {
            $(this).css('background-color', '#c8e6c9'); // 綠
        } else if (state === 'reserved') {
            $(this).css('background-color', '#ffcdd2'); // 紅
        } else if (state === 'pending') {
            $(this).css('background-color', '#fff176'); // 黃
        } else {
            $(this).css('background-color', '#ffffff'); // 白
        }
    });

    // 公告功能（僅提示）
    $('#post-announcement').click(function () {
        const text = prompt("請輸入公告內容：");
        if (text) {
            alert(`公告已發佈：\n${text}`);
            // 可拓展：POST 到後端資料庫保存
        }
    });

    // 返回按鈕
    $('#back-to-schedule').click(function () {
        $('#chat-view').hide();
        $('#schedule-view').show();
    });

    // 點擊預約格子（僅模擬）
    $('.time-slot').click(function () {
        alert('此為教授頁面，無需預約。');
    });
});
