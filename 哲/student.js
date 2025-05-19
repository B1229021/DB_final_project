// 獲取用戶ID參數
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
        data: { 
            user_id: $('#id').val(), 
            act: 'professor' 
        },
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
        // 重置職稱和教授名稱下拉選單
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
        // 重置教授名稱下拉選單
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

    // 4. 當教授名稱被選擇時，載入該教授的課表時間狀態
    $('#name').change(function() {
        const professor_id = $(this).val();
        if (!professor_id) return;
        
        // 這裡需要增加載入教授可用時間的 AJAX 請求
        loadProfessorSchedule(professor_id);
        
        // 同時載入該教授的預約紀錄
        loadAppointmentRecords(professor_id);
    });

    // 5. 載入教授課表時間狀態的函數
    function loadProfessorSchedule(professor_id) {
        $.ajax({
            type: 'GET',
            url: `${NGROK_URL}/action.php`,
            data: { 
                act: 'schedule', 
                professor_id: professor_id,
                user_id: $('#id').val() 
            },
            dataType: 'json',
            success: function(result) {
                // 重置所有時間槽的狀態
                $('.time-slot').removeClass('available reserved pending').text('預約');
                
                // 根據返回的數據設置每個時間槽的狀態
                result.forEach(slot => {
                    // 找到對應的時間槽元素
                    const timeSlotElement = findTimeSlotElement(slot.day, slot.time);
                    
                    if (timeSlotElement) {
                        // 根據狀態設置不同的類別和文本
                        if (slot.status === 'available') {
                            timeSlotElement.addClass('available').text('可預約');
                        } else if (slot.status === 'reserved') {
                            timeSlotElement.addClass('reserved').text('已預約');
                        } else if (slot.status === 'pending') {
                            // 新增等待確認狀態 - 黃色
                            timeSlotElement.addClass('pending').text('等待確認');
                        }
                    }
                });
            },
            error: function(xhr, status, msg) {
                console.error('schedule AJAX 錯誤：', msg);
            }
        });
    }

    // 6. 根據星期和時間找到對應的時間槽元素
    function findTimeSlotElement(day, time) {
        // 星期對應到表格的列索引（從0開始）
        const dayIndex = {
            'Monday': 1,    // 星期一是第2列
            'Tuesday': 2,   // 星期二是第3列
            'Wednesday': 3, // 星期三是第4列
            'Thursday': 4,  // 星期四是第5列
            'Friday': 5     // 星期五是第6列
        }[day];
        
        // 時間對應到表格的行索引（從0開始）
        const timeIndex = {
            '08:10～09:00': 0, // 第1行
            '09:10～10:00': 1, // 第2行
            '10:10～11:00': 2, // 第3行
            '11:10～12:00': 3, // 第4行
            '13:10～14:00': 4, // 第5行
            '14:10～15:00': 5, // 第6行
            '15:10～16:00': 6  // 第7行
        }[time];
        
        if (dayIndex !== undefined && timeIndex !== undefined) {
            // 選擇表格中對應的單元格中的按鈕
            return $('.timetable tbody tr').eq(timeIndex).find('td').eq(dayIndex).find('.time-slot');
        }
        
        return null;
    }

    // 7. 載入學生的預約紀錄
    function loadAppointmentRecords(professor_id = null) {
        $.ajax({
            type: 'GET',
            url: `${NGROK_URL}/action.php`,
            data: { 
                act: 'appointments', 
                user_id: $('#id').val(),
                professor_id: professor_id
            },
            dataType: 'json',
            success: function(result) {
                // 清空預約紀錄容器
                $('#appointment-records').empty();
                
                // 如果沒有預約紀錄
                if (result.length === 0) {
                    $('#appointment-records').append('<div class="no-appointments">尚無預約紀錄</div>');
                    return;
                }
                
                // 依時間排序預約紀錄（最近的在前）
                result.sort((a, b) => new Date(b.time) - new Date(a.time));
                
                // 添加預約紀錄到容器
                result.forEach(record => {
                    // 根據狀態設置不同的類別
                    let statusClass = '';
                    if (record.status === 'pending') {
                        statusClass = 'status-pending';
                    } else if (record.status === 'confirmed') {
                        statusClass = 'status-confirmed';
                    }
                    
                    // 添加預約紀錄HTML
                    $('#appointment-records').append(`
                        <div class="appointment-record" data-id="${record.id}">
                            <div class="record-time">${record.date} ${record.time_slot}</div>
                            <div class="record-professor">${record.professor_name}</div>
                            <div class="record-purpose">${record.purpose.substring(0, 30)}${record.purpose.length > 30 ? '...' : ''}</div>
                            <div class="record-status ${statusClass}">
                                ${record.status === 'pending' ? '等待確認' : '已確認'}
                            </div>
                        </div>
                    `);
                });
                
                // 點擊預約紀錄時顯示詳細信息
                $('.appointment-record').on('click', function() {
                    const appointmentId = $(this).data('id');
                    showAppointmentDetails(appointmentId);
                });
            },
            error: function(xhr, status, msg) {
                console.error('appointments AJAX 錯誤：', msg);
            }
        });
    }

    // 8. 顯示預約詳細信息的函數
    function showAppointmentDetails(appointmentId) {
        $.ajax({
            type: 'GET',
            url: `${NGROK_URL}/action.php`,
            data: { 
                act: 'appointment_detail', 
                id: appointmentId 
            },
            dataType: 'json',
            success: function(result) {
                // 這裡可以使用模態框或其他方式顯示預約詳情
                alert(`
                    預約日期：${result.date}
                    預約時間：${result.time_slot}
                    教授：${result.professor_name}
                    預約目的：${result.purpose}
                    狀態：${result.status === 'pending' ? '等待確認' : '已確認'}
                `);
            },
            error: function(xhr, status, msg) {
                console.error('appointment_detail AJAX 錯誤：', msg);
            }
        });
    }

    // 9. 點擊時間槽預約
    $(document).on('click', '.time-slot.available', function() {
        // 獲取該時間槽對應的日期和時間
        const dayIndex = $(this).closest('td').index();
        const timeIndex = $(this).closest('tr').index();
        
        // 根據索引獲取星期和時間文本
        const day = ['', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][dayIndex];
        const time = [
            '08:10～09:00', '09:10～10:00', '10:10～11:00', '11:10～12:00',
            '13:10～14:00', '14:10～15:00', '15:10～16:00'
        ][timeIndex];
        
        // 保存當前選中的時間槽
        selectedTimeSlot = {
            day: day,
            time: time,
            professorId: $('#name').val()
        };
        
        // 顯示預約對話框
        $('#reservation-modal').show();
    });

    // 10. 取消預約
    $('#cancel-reservation').on('click', function() {
        // 隱藏預約對話框
        $('#reservation-modal').hide();
        // 清空預約目的輸入框
        $('#reservation-purpose').val('');
        // 清空選中的時間槽
        selectedTimeSlot = null;
    });

    // 11. 確認預約
    $('#confirm-reservation').on('click', function() {
        // 獲取預約目的
        const purpose = $('#reservation-purpose').val().trim();
        
        if (purpose === '') {
            alert('請輸入預約目的！');
            return;
        }
        
        if (selectedTimeSlot) {
            // 發送預約請求
            $.ajax({
                type: 'POST',
                url: `${NGROK_URL}/action.php`,
                data: { 
                    act: 'make_appointment', 
                    user_id: $('#id').val(),
                    professor_id: selectedTimeSlot.professorId,
                    day: selectedTimeSlot.day,
                    time: selectedTimeSlot.time,
                    purpose: purpose
                },
                dataType: 'json',
                success: function(result) {
                    if (result.success) {
                        alert('預約已提交，等待教授確認！');
                        // 隱藏預約對話框
                        $('#reservation-modal').hide();
                        // 清空預約目的
                        $('#reservation-purpose').val('');
                        // 重新載入課表和預約紀錄
                        loadProfessorSchedule(selectedTimeSlot.professorId);
                        loadAppointmentRecords(selectedTimeSlot.professorId);
                    } else {
                        alert('預約失敗：' + result.message);
                    }
                },
                error: function(xhr, status, msg) {
                    console.error('make_appointment AJAX 錯誤：', msg);
                    alert('預約請求發送失敗，請稍後再試！');
                }
            });
        }
    });

    // 預設：顯示課表，隱藏聊天
    $('#schedule-view').show();
    $('#chat-view').hide();

    // 12. 客服中心按鈕：開啟客服聊天窗口
    $('#customer-service').on('click', function() {
        // 設置聊天頭部信息
        $('.chat-header-avatar').text('客服');
        $('.chat-header-name').text('客服中心');
        $('.chat-header-title').text('線上支援');
        
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

    // 13. 返回課表按鈕
    $('#back-to-schedule').on('click', function() {
        // 顯示課表視圖，隱藏聊天視圖
        $('#schedule-view').show();
        $('#chat-view').hide();
    });

    // 14. 送訊息
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
                response = "若要預約，請在課表中點選綠色的時段，並填寫預約表單。您可以在左側預約紀錄區域查看您的預約狀態。";
            } else if (txt.includes("等待確認") || txt.includes("pending")) {
                // 等待確認預約相關問題的回應
                response = "黃色表示您已提交預約請求，但教授尚未確認。請耐心等待，或直接聯繫該教授以加快處理。";
            } else if (txt.includes("取消")) {
                // 取消預約相關問題的回應
                response = "如需取消預約，請在左側「預約紀錄」中找到該筆預約並點選取消按鈕。";
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

    // 15. 監聽聊天輸入框的按鍵事件，當按下Enter鍵時觸發發送按鈕的點擊事件
    $('#chat-input').on('keypress', function(e) {
        if (e.key === 'Enter') $('#send-btn').click();
    });

    // 全局變數：保存選中的時間槽信息
    let selectedTimeSlot = null;

    // 16. 初始載入預約紀錄
    loadAppointmentRecords();
    
    // 17. 根據用戶角色調整界面（學生/教授）
    // 這裡可以添加根據用戶角色調整界面的邏輯
});
