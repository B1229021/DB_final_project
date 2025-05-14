from flask import Flask, render_template, redirect, url_for, request, abort, jsonify
from flask.logging import create_logger
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage

import pymysql

#pip install line-bot-sdk
#pip install pymysql

#連接到linebot的部分
app = Flask(__name__)
LOG = create_logger(app)

#連接到mysql
import re
def sql_connect(host, port, user, passwd, database):
    global db, cursor
    try:
        db = pymysql.connect(host=host, user=user,passwd='123456' , database=database, port=int(port))
        print("連線成功")
        cursor = db.cursor()  # 創建一個與資料庫連線的游標(cursor)對象
        return True
    except pymysql.Error as e:
        print("連線失敗:", str(e))
        return False

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

# 處理來自 LINE Bot 的消息
@handler.add(MessageEvent)
def handle_message(event):
    user_id = event.source.user_id
    print("user_id =", user_id)

    if event.message.type == 'text':
        stt = event.message.text
        if stt == '預約系統':
            login_url = 'http://localhost:8000/login'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(f'請點選以下連結進入登入頁面：\n{login_url}')
            )

#顯示登入頁面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if 'B' in user_id:  # 假設 'B' 開頭的是學生帳號
            return redirect(url_for('student'))
        else:
            return "帳號錯誤，請重新輸入。"
    return render_template('login.html')

@app.route('/student')
def student():
    return render_template('student.html')




#暫定從資料庫偷資料
@app.route('/get_contacts', methods=['GET'])
def get_contacts():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, department, title, name FROM contacts")
    contacts = cursor.fetchall()
    return jsonify(contacts)

@app.route('/get_professors', methods=['GET'])
def get_professors():
    # 確認已經連接到資料庫
    if db is None or cursor is None:
        return jsonify([])

    try:
        query = "SELECT department, title, name FROM professors"
        cursor.execute(query)
        results = cursor.fetchall()
        
        # 格式化資料
        professors = [{"department": row[0], "title": row[1], "name": row[2]} for row in results]
        
        return jsonify(professors)
    except Exception as e:
        print(f"查詢失敗: {e}")
        return jsonify([])


# 啟動 Flask
if __name__ == "__main__":
    app.run(port=8000, debug=True)