from flask import Flask, render_template, redirect, url_for, request, abort, jsonify, session
from flask.logging import create_logger
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
# from linebot.models import MessageEvent, TextSendMessage
from linebot.models import MessageEvent, TextSendMessage, TemplateSendMessage, ButtonsTemplate, URIAction,FollowEvent, PostbackEvent,PostbackAction,FlexSendMessage
from linebot import LineBotApi, WebhookHandler
import requests
import pymysql
import json

#pip install line-bot-sdk
#pip install pymysql

with open('richmenu_id.json', 'r') as f:
    richmenu_ids = json.load(f)

STUDENT_RICH_MENU_ID = richmenu_ids['student']
PROFESSOR_RICH_MENU_ID = richmenu_ids['professor']

# 全域變數，修改ngrok抓的8000
NGROK_URL = 'https://33fb-211-72-73-194.ngrok-free.app'

# LOCALHOST_URL = 'http://localhost/linebot2.0'

# PHP_SCRIPT_URL = f'{NGROK_URL}/action.php?act=save_student'


#連接到linebot的部分
app = Flask(__name__)
LOG = create_logger(app)
app.secret_key = 'a_very_secret_and_random_string_1234567890'


def get_db():
    return pymysql.connect(host='localhost', user='root', passwd='123456', database='project', charset='utf8mb4')

line_bot_api = LineBotApi('5greXasUuMtXP4KYR526MH8jXiZrHYlVVlwMyFaam9Sad/zZlRPbovaRc9neqLJkhS7jLjYPdrGG1WYHzPWIdlZEdmohsWrmF5efXOKi2lp8Q3YUG7J/x2DeHGoou/72LwYl81b68pNqKBoxK/9lywdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('0e038b378e27bc8b84d22b0c97ba6c08')

# 頁面路由
# @app.route('/login')
# def login():
#     return redirect(url_for('student'))

# @app.route('/status', methods=['GET'])
# def status():
#     return "LINE Bot server running!"

# LINE Bot Webhook 路由
# @app.route("/callback", methods=['POST'])

#不重要
@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    LOG.info("Request body: " + body)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

#初次加入linebot選擇教授還是學生 
@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    print(f"新使用者加入: {user_id}")

    # 回應一個選擇身份的按鈕
    message = TemplateSendMessage(
        alt_text='請選擇您的身份',
        template=ButtonsTemplate(
            title='請選擇您的身份',
            text='您是學生還是教授？',
            actions=[
                PostbackAction(label='student', data='role=student'),
                PostbackAction(label='professor', data='role=professor')
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)

# 手動輸入預約系統
@handler.add(MessageEvent)
def handle_message(event):
    if event.message.type == 'text':
        stt = event.message.text

        if stt == '預約系統':
            u_id = event.source.user_id
            # 設定跳轉到 login 頁面的 URL
            url = f'{NGROK_URL}/login_s?u_id={u_id}'
            # 設定按鈕給使用者
            message = TemplateSendMessage(
                alt_text='前往登入頁面',
                template=ButtonsTemplate(
                    title='預約系統',
                    text='請點選下方按鈕登入，進行預約',
                    actions=[URIAction(label='前往登入頁面', uri=url)]
                )
            )

            # 發送訊息給使用者，顯示按鈕
            line_bot_api.reply_message(event.reply_token, message)

#選取身分後提供正確的richmenu，提供註冊連結
@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    user_id = event.source.user_id
    print(f"使用者選擇身份: {data}, user_id: {user_id}")
    print("Postback data:", data)

    if data == 'role=student':
        register_url = f'{NGROK_URL}/register_s?user_id={user_id}'
        login_url = f'{NGROK_URL}/login_s?user_id={user_id}'
        line_bot_api.link_rich_menu_to_user(user_id, STUDENT_RICH_MENU_ID)
    elif data == 'role=professor':
        register_url = f'{NGROK_URL}/register_p?user_id={user_id}'
        login_url = f'{NGROK_URL}/login_p?user_id={user_id}'
        line_bot_api.link_rich_menu_to_user(user_id, PROFESSOR_RICH_MENU_ID)
    else:
        # 如果收到其他不在預期的 data，可以回覆提示訊息，或直接 return
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='身份選擇錯誤，請重新選擇。'))
        return
    
    flex_message = FlexSendMessage(
        alt_text='請選擇動作',
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "身份確認成功",
                        "weight": "bold",
                        "size": "lg"
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "uri",
                            "label": "前往註冊頁面",
                            "uri": register_url
                        }
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "action": {
                            "type": "uri",
                            "label": "前往登入頁面",
                            "uri": login_url
                        }
                    }
                ]
            }
        }
    )
    line_bot_api.reply_message(event.reply_token, flex_message)

# 學生跳轉到註冊頁面，偷取LINE的user_id
@app.route('/register_s', methods=['GET'])
def register_page_s():
    u_id = request.args.get('user_id')
    return render_template('register_s.html', u_id=u_id)

# 教授跳轉到註冊頁面，偷取LINE的user_id
@app.route('/register_p', methods=['GET'])
def register_page_p():
    u_id = request.args.get('user_id')
    return render_template('register_p.html', u_id=u_id)

#學生註冊
@app.route('/register_s', methods=['POST'])
def register_s():
    u_id = request.form.get('u_id')
    department = request.form.get('department')
    s_id = request.form.get('s_id')
    name = request.form.get('name')
    password = request.form.get('password')

    conn = get_db()
    cursor = conn.cursor()
    
    # 檢查資料是否已存在
    cursor.execute("SELECT * FROM student WHERE s_id=%s", (s_id,))
    if cursor.fetchone():
        conn.close()
        return "該學號已經被註冊"

    # 插入資料
    cursor.execute("INSERT INTO student (u_id, s_id, department, name, password) VALUES (%s, %s, %s, %s, %s)", 
                   (u_id, s_id, department, name, password))
    conn.commit()
    cursor.close()
    conn.close()

    # return redirect(url_for('login_s'))
    return redirect(f'{NGROK_URL}/login_s?u_id={u_id}')

#教授註冊
@app.route('/register_p', methods=['POST'])
def register_p():
    u_id = request.form.get('u_id')
    department = request.form.get('department')
    p_id = request.form.get('p_id')
    position = request.form.get('position')
    name = request.form.get('name')
    password = request.form.get('password')

    conn = get_db()
    cursor = conn.cursor()
    
    # 檢查資料是否已存在
    cursor.execute("SELECT * FROM professor WHERE p_id=%s", (p_id,))
    if cursor.fetchone():
        conn.close()
        return "該帳號已經被註冊"

    # 插入資料
    cursor.execute("INSERT INTO professor (u_id, p_id, department, name, password, position) VALUES (%s, %s, %s, %s, %s, %s)", 
                   (u_id, p_id, department, name, password, position))
    conn.commit()
    cursor.close()
    conn.close()

    # return redirect(url_for('login_p'))
    return redirect(f'{NGROK_URL}/login_p?u_id={u_id}')

# 顯示登入頁面(學生)
@app.route('/login_s', methods=['GET', 'POST'])
def login_s():
    print("進到 /login_s")   # 這行用來測試
    if request.method == 'POST':
        s_id = request.form.get('s_id')
        # u_id = request.form.get('u_id')
        password = request.form.get('password')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT u_id, password FROM student WHERE s_id=%s", (s_id,))
        user = cursor.fetchone()
        cursor.close() 
        conn.close()
        if user and user[1] == password:  # 
            session['s_id'] = s_id
            session['u_id'] = user[0]  # 資料庫裡拿到的 u_id
            return redirect(f'{NGROK_URL}/student?u_id={user[0]}')
        else:
            return "帳號或密碼錯誤，請重新輸入"

    return render_template('login_s.html')

#學生介面
@app.route('/student')
def student():
    u_id = request.args.get('u_id')
    
    # 如果 u_id 不存在，代表可能是非法訪問
    if not u_id:
        return "找不到 u_id，請重新登入", 400
    
    name = session.get('name')
    print(f"Student Page - u_id: {u_id}, name: {name}")

    return render_template('student.html', u_id=u_id, name=name)

# 顯示登入頁面(教授)
@app.route('/login_p', methods=['GET', 'POST'])
def login_p():
    print("進到 /login_p")   # 測試用
    if request.method == 'POST':
        p_id = request.form.get('p_id')
        # u_id = request.form.get('u_id')
        password = request.form.get('password')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT u_id, password FROM professor WHERE p_id=%s", (p_id,))
        user = cursor.fetchone()
        cursor.close() 
        conn.close()
        if user and user[1] == password:  #
            session['p_id'] = p_id
            session['u_id'] = user[0]  # 資料庫裡拿到的 u_id
            return redirect(f'{NGROK_URL}/professor?u_id={user[0]}')
        else:
            return "帳號或密碼錯誤，請重新輸入"

    return render_template('login_p.html')

#教授介面
@app.route('/professor')
def professor():
    u_id = request.args.get('u_id')
    
    # 如果 u_id 不存在，代表可能是非法訪問
    if not u_id:
        return "找不到 u_id，請重新登入", 400
    
    name = session.get('name')
    print(f"Professor Page - u_id: {u_id}, name: {name}")

    return render_template('professor.html', u_id=u_id, name=name)

#暫定從資料庫偷資料
# @app.route('/get_contacts', methods=['GET'])
# def get_contacts():
#     cursor = db.cursor(dictionary=True)
#     cursor.execute("SELECT id, department, title, name FROM contacts")
#     contacts = cursor.fetchall()
#     return jsonify(contacts)

# @app.route('/get_professors', methods=['GET'])
# def get_professors():
#     # 確認已經連接到資料庫
#     if db is None or cursor is None:
#         return jsonify([])

#     try:
#         query = "SELECT department, title, name FROM professors"
#         cursor.execute(query)
#         results = cursor.fetchall()
        
#         # 格式化資料
#         professors = [{"department": row[0], "title": row[1], "name": row[2]} for row in results]
        
#         return jsonify(professors)
#     except Exception as e:
#         print(f"查詢失敗: {e}")
#         return jsonify([])


# 啟動 Flask
if __name__ == "__main__":
    print(app.url_map)
    app.run(port=8000, debug=True)