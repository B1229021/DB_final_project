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


#使用者的rich_menu
USER_RICH_MENU_ID = richmenu_ids['user']


# 全域變數，修改ngrok抓的8000
NGROK_URL = 'https://33fb-211-72-73-194.ngrok-free.app'

# LOCALHOST_URL = 'http://localhost/linebot2.0'

# PHP_SCRIPT_URL = f'{NGROK_URL}/action.php?act=save_student'


#連接到linebot的部分
app = Flask(__name__)
LOG = create_logger(app)
# app.secret_key = 'a_very_secret_and_random_string_1234567890'


def get_db():
    return pymysql.connect(host='localhost', user='root', passwd='', database='project', charset='utf8mb4')

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

#修改完成
#初次加入linebot
@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    print(f"新使用者加入: {user_id}")

    line_bot_api.link_rich_menu_to_user(user_id, USER_RICH_MENU_ID)
    
    register_url=f'{NGROK_URL}/register?user_id={user_id}'
    flex_message = FlexSendMessage(
        alt_text='歡迎加入！請點擊以下按鈕進行註冊',
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "初次使用，請您進行註冊",
                        "wrap": True,
                        "weight": "bold",
                        "size": "md"
                    },
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                            "type": "uri",
                            "label": "前往註冊頁面",
                            "uri": register_url
                        }
                    }
                ]
            }
        }
    )
    
    line_bot_api.reply_message(event.reply_token, flex_message)

#修改完成
#使用者跳轉到註冊頁面，偷取LINE的user_id
@app.route('/register', methods=['GET'])
def register_page():
    u_id = request.args.get('user_id')
    return render_template('register.html', u_id=u_id)

#修改完成
#使用者註冊
@app.route('/register', methods=['POST'])
def register():
    uid = request.form.get('uid')
    account = request.form.get('account')
    gender = request.form.get('gender')
    name = request.form.get('name')
    password = request.form.get('password')

    conn = get_db()
    cursor = conn.cursor()
    
    # 檢查資料是否已存在
    cursor.execute("SELECT * FROM user WHERE account=%s", (account,))
    if cursor.fetchone():
        conn.close()
        return "該帳號已經被註冊"

    # 插入資料
    cursor.execute("INSERT INTO student (uid, account, gender, name, password) VALUES (%s, %s, %s, %s, %s)", 
                   (uid, account, gender, name, password))
    conn.commit()
    cursor.close()
    conn.close()

    # return redirect(url_for('login'))
    return redirect(f'{NGROK_URL}/login?uid={uid}')

#尚未完成 要判斷是否為管理者
# 顯示登入頁面
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("進到 /login")   # 這行用來測試
    if request.method == 'POST':
        account = request.form.get('account')
        # u_id = request.form.get('u_id')
        password = request.form.get('password')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT uid, password FROM user WHERE account=%s", (account,))
        user = cursor.fetchone()
        cursor.close() 
        conn.close()
        if user and user[1] == password:
            session['account'] = account
            session['uid'] = user[0]  # 資料庫裡拿到的 uid
            return redirect(f'{NGROK_URL}/index?u_id={user[0]}')
        else:
            return "帳號或密碼錯誤，請重新輸入"

    return render_template('login.html')

#使用者介面
@app.route('/user')
def user():
    uid = request.args.get('uid')
    
    # 如果 u_id 不存在，代表可能是非法訪問
    if not uid:
        return "找不到 uid，請重新登入", 400
    
    name = session.get('name')
    print(f"User Page - uid: {uid}, name: {name}")

    return render_template('index.html', uid=uid, name=name)

#管理者介面
@app.route('/admin')
def admin():
    uid = request.args.get('uid')
    
    # 如果 u_id 不存在，代表可能是非法訪問
    if not uid:
        return "找不到 u_id，請重新登入", 400
    
    name = session.get('name')
    print(f"Admin Page - u_id: {uid}, name: {name}")

    return render_template('admin.html', uid=uid, name=name)

# 啟動 Flask
if __name__ == "__main__":
    print(app.url_map)
    app.run(port=8000, debug=True)