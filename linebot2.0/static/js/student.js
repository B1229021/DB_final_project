    var currentUrl = window.location.href; // 取得當前網址
    var url = new URL(currentUrl); // 進行 URL 解析
    var user_id = url.searchParams.get("user_id"); // 從 URL 的查詢參數中取得名稱為 "user_id" 的值
    $("#id").val(user_id); // 將取得的 "user_id" 值設定到元素 ID 為 "id" 的 input

    $(function() {
        // 1. 載入「科系」＋第一波 professors，從中取出不重複的 department
        $.ajax({
            type: 'GET',
            url: 'http://localhost/linebot2.0/action.php',
            data: { act: 'professors' },
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
            console.error('professors AJAX 錯誤：', msg);
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
            url: 'http://localhost/linebot2.0/action.php',
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
            url: 'http://localhost/linebot2.0/action.php',
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

        // 4. Chat 按鈕：把選好的教授加入左側聊天聯絡人
        $('#chat-btn').on('click', function() {
            const profId    = $('#name').val();
            const profName  = $('#name option:selected').text();
            const profTitle = $('#title option:selected').text();
            if (!profId) {
                alert('請先選擇完整科系、職稱與名稱！');
            return;
            }
            if ($('#chat-contacts').find(`.contact-item[data-id="${profId}"]`).length) {
                alert('此教授已在聯絡人清單中');
                return;
            }
            const $item = $(`
                <div class="contact-item" data-id="${profId}" data-name="${profName}" data-title="${profTitle}">
                    <div class="info">
                        <div class="name">${profName}</div>
                    </div>
                </div>
            `);

            $('#chat-contacts').append($item);
        });

        // 5. 點左側聯絡人：切換到聊天視圖並填入 header
        $('#chat-contacts').on('click', '.contact-item', function() {
            const $this     = $(this);
            const profName  = $this.data('name');

            const avatarPath = "http://localhost/linebot2.0/images/chat_head.png";


            $('#chat-contacts .contact-item').removeClass('active');
            $this.addClass('active');

            $('#schedule-view').hide();
            $('#chat-view').show();

            $('#chat-view .chat-header-name').text(profName);
            $('#chat-view .chat-header-avatar').html(`<img src="${avatarPath}" alt="${profName}" class="chat_head"> `);

            $('#chat-messages').empty();
        });

        $('#back-to-schedule').on('click', function() {
            $('#chat-view').hide();
            $('#schedule-view').show();
        });

        // 6. 送訊息範例
        $('#send-btn').on('click', function() {
            const txt = $('#chat-input').val().trim();
            if (!txt) return;
            $('#chat-messages').append(`
            <div class="message sent">
                <div class="message-bubble">${txt}</div>
            </div>
            `);
            $('#chat-input').val('').focus();

            // 自動回覆示例
            setTimeout(() => {
            $('#chat-messages').append(`
                <div class="message received">
                <div class="message-bubble">不要亂點好嗎?</div>
                </div>
            `);
            $('#chat-messages').scrollTop($('#chat-messages')[0].scrollHeight);
            }, 500);
        });
        $('#chat-input').on('keypress', function(e) {
            if (e.key === 'Enter') $('#send-btn').click();
        });

    });