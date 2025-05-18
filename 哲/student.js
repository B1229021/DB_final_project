var currentUrl = window.location.href; // 取得當前網址
var url = new URL(currentUrl); // 進行 URL 解析
var user_id = url.searchParams.get("user_id"); // 從 URL 的查詢參數中取得名稱為 "user_id" 的值
$("#id").val(user_id); // 將取得的 "user_id" 值設定到元素 ID 為 "id" 的 input

// 全域變數，修改ngrok抓的8000
NGROK_URL = 'https://33fb-211-72-73-194.ngrok-free.app'

$(function() {
    // 1. 載入「科系」＋第一波 professors，從中取出不重複的 department
    $.ajax({
        type: 'GET',
        url: `${NGROK_URL}/action.php`,
        data: { user_id: $('#id').val(), 
                act: 'professor' },
        dataType: 'json',
        success: function(result) {
        // 以 Set 去重
        const deps = new Set(result.map(p => p.department));
        deps.forEach(dep => {
            $('#department').append(
            `<option value="${dep}">${dep}</option>`
            );
        });
        },
        error: function(xhr, status, msg) {
        console.error('professor AJAX 錯誤：', msg);
        }
    });

    // 2. 當「科系」選擇時，載入職稱
    $('#department').change(function() {
        const dep = $(this).val();
        $('#title').empty().append('<option value="" selected hidden>請選擇職稱</option>');
        $('#name').empty().append('<option value="" selected hidden>請選擇教授</option>');
        if (!dep) return;

        $.ajax({
        type: 'GET',
        url: `${NGROK_URL}/action.php`,
        data: { act: 'title', val: dep },
        dataType: 'json',
        success: function(result) {
            result.forEach(item => {
            $('#title').append(
                `<option value="${item.id}">${item.title}</option>`
            );
            });
        },
        error: function(xhr, status, msg) {
            console.error('title AJAX 錯誤：', msg);
        }
        });
    });

    // 3. 當「職稱」選擇時，載入教授名稱
    $('#title').change(function() {
        const t = $(this).val();
        $('#name').empty().append('<option value="" selected hidden>請選擇教授</option>');
        if (!t) return;

        $.ajax({
        type: 'GET',
        url: `${NGROK_URL}/action.php`,
        data: { act: 'name', val: t },
        dataType: 'json',
        success: function(result) {
            result.forEach(item => {
            $('#name').append(
                `<option value="${item.id}">${item.name}</option>`
            );
            });
        },
        error: function(xhr, status, msg) {
            console.error('name AJAX 錯誤：', msg);
        }
        });
    });

    // 預設：顯示課表，隱藏聊天
    $('#schedule-view').show();
    $('#chat-view').hide();

    // 4. 客服中心按鈕：開啟客服聊天窗口
    $('#customer-service-btn').on('click', function() {
        // 隱藏課表視圖，顯示聊天視圖
        $('#schedule-view').hide();
        $('#chat-view').show();
        
        // 清空聊天記錄，每次開啟聊天時重置對話
        $('#chat-messages').empty();
        
        // 顯示歡迎訊息，500毫秒後顯示以模擬真人客服回應
        setTimeout(() => {
            // 添加一條客服的歡迎訊息到聊天視窗
            $('#chat-messages').append(`
                <div class="message received">
                    <div class="message-bubble">您好，我是客服中心，有什麼可以幫助您的嗎？</div>
                </div>
            `);
            // 滾動到聊天窗口的底部，確保新訊息可見
            $('#chat-messages').scrollTop($('#chat-messages')[0].scrollHeight);
        }, 500);
    });

    // 5. 點擊客服中心選項：開啟客服聊天窗口（與上面功能相同，但是從側邊欄觸發）
    $('#customer-service').on('click', function() {
        // 隱藏課表視圖，顯示聊天視圖
        $('#schedule-view').hide();
        $('#chat-view').show();
        
        // 清空聊天記錄，每次開啟聊天時重置對話
        $('#chat-messages').empty();
        
        // 顯示歡迎訊息，500毫秒後顯示以模擬真人客服回應
        setTimeout(() => {
            // 添加一條客服的歡迎訊息到聊天視窗
            $('#chat-messages').append(`
                <div class="message received">
                    <div class="message-bubble">您好，我是客服中心，有什麼可以幫助您的嗎？</div>
                </div>
            `);
            // 滾動到聊天窗口的底部，確保新訊息可見
            $('#chat-messages').scrollTop($('#chat-messages')[0].scrollHeight);
        }, 500);
    });

    // 6. 送訊息範例
    $('#send-btn').on('click', function() {
        // 獲取輸入框的文字並去除前後空格
        const txt = $('#chat-input').val().trim();
        // 如果沒有輸入任何文字，則直接返回不執行後續操作
        if (!txt) return;
        
        // 添加用戶發送的訊息到聊天視窗，使用sent類別表示這是用戶發出的訊息
        $('#chat-messages').append(`
        <div class="message sent">
            <div class="message-bubble">${txt}</div>
        </div>
        `);
        
        // 清空輸入框並重新聚焦，方便用戶繼續輸入
        $('#chat-input').val('').focus();

        // 模擬客服自動回覆
        setTimeout(() => {
            // 預設回覆訊息
            let response = "謝謝您的訊息，我們將盡快處理您的問題。";
            
            // 簡單的關鍵字匹配機制，根據用戶輸入的內容提供不同的回應
            if (txt.includes("課表") || txt.includes("時間")) {
                // 課表相關問題的回應
                response = "關於課表問題，您可以在主畫面查看您的課程時間表。如有特殊需求，請聯繫教務處。";
            } else if (txt.includes("預約") || txt.includes("appointment")) {
                // 預約相關問題的回應
                response = "若要預約，請在課表中點選綠色的時段，並填寫預約表單。";
            } else if (txt.includes("取消")) {
                // 取消預約相關問題的回應
                response = "如需取消預約，請在「我的預約」中找到該筆預約並點選取消按鈕。";
            } else if (txt.includes("問題") || txt.includes("help") || txt.includes("幫忙")) {
                // 尋求幫助的一般性問題回應
                response = "您好，請詳細說明您遇到的問題，我們將盡力協助您解決。";
            }
            
            // 添加客服回覆訊息到聊天視窗，使用received類別表示這是收到的訊息
            $('#chat-messages').append(`
                <div class="message received">
                    <div class="message-bubble">${response}</div>
                </div>
            `);
            
            // 滾動到聊天窗口的底部，確保新訊息可見
            $('#chat-messages').scrollTop($('#chat-messages')[0].scrollHeight);
        }, 800);
    });

        // 監聽聊天輸入框的按鍵事件，當按下Enter鍵時觸發發送按鈕的點擊事件
        $('#chat-input').on('keypress', function(e) {
            if (e.key === 'Enter') $('#send-btn').click();
        });
    
});
