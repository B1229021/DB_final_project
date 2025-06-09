from flask import Flask, render_template, redirect, url_for, request, abort, jsonify, session, Blueprint, render_template, request, redirect, url_for, session, abort
from flask_cors import CORS
from flask.logging import create_logger
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage, TemplateSendMessage, ButtonsTemplate, URIAction,FollowEvent, PostbackEvent,PostbackAction,FlexSendMessage
from linebot import LineBotApi, WebhookHandler
import requests
import pymysql
import json
import pymysql.cursors
import datetime

from functools import wraps


#pip install line-bot-sdk
#pip install pymysql
#pip install Flask
#pip install flask-cors

with open('richmenu_id.json', 'r') as f:
    richmenu_ids = json.load(f)

profile_bp = Blueprint('profile', __name__)

#使用者的rich_menu
USER_RICH_MENU_ID = richmenu_ids['user']


# 全域變數，修改ngrok抓的8000
NGROK_URL = 'https://bd64-2407-4d00-7c07-8fd-328f-1eb5-1a9e-c49d.ngrok-free.app'

#連接到linebot的部分
app = Flask(__name__)
CORS(app)
LOG = create_logger(app)
app.secret_key = 'a_very_secret_and_random_string_1234567890'


def get_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        passwd='',
        database='project1',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)

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

def user_exists(uid):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM user WHERE uid=%s", (uid,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return exists

def require_registered_user(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        uid = request.args.get('uid')
        if not user_exists(uid):
            return redirect(url_for('register_page', uid=uid))
        return view_func(*args, **kwargs)
    return wrapper


#不重要
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    print("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

######################### linebot

#初次加入linebot
@handler.add(FollowEvent)
def handle_follow(event):
    uid = event.source.user_id
    print(f"新使用者加入: {uid}")

    line_bot_api.link_rich_menu_to_user(uid, USER_RICH_MENU_ID)
    
    register_url=f'{NGROK_URL}/register?uid={uid}'
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


#提醒被取消
def notify_event_cancelled(orderid):
    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    # 取得活動名稱、開始時間、地點、發起人
    cursor.execute("""
        SELECT event.content as event_name, order_detail.booker, order_detail.start_time, order_detail.location
        FROM order_detail 
        LEFT JOIN event ON order_detail.event_id = event.event_id 
        WHERE order_detail.orderid=%s
    """, (orderid,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return
    event_name = row.get('event_name', '您的活動')
    booker = row.get('booker')
    start_time = row.get('start_time')
    location = row.get('location', '未設定')

    # 抓發起人匿名（假設 user.username 是匿名）
    cursor.execute("SELECT username FROM user WHERE uid=%s", (booker,))
    user_row = cursor.fetchone()
    booker_name = user_row['username'] if user_row and user_row.get('username') else "匿名"

    # 格式化開始時間
    if start_time:
        try:
            if isinstance(start_time, (datetime.datetime, datetime.date)):
                start_time_str = start_time.strftime('%Y-%m-%d %H:%M')
            else:
                start_time_str = str(start_time)[:16].replace('T', ' ')
        except Exception:
            start_time_str = str(start_time)
    else:
        start_time_str = "未設定"

    # 取得所有參加者
    cursor.execute("SELECT uid FROM involvement WHERE orderid=%s", (orderid,))
    uids = [r['uid'] for r in cursor.fetchall()]
    if booker and booker not in uids:
        uids.append(booker)
    uids = list(set(uids))
    conn.close()

    message = (
        f"您參與的活動《{event_name}》已被發起人（{booker_name}）取消。\n"
        f"活動開始時間：{start_time_str}\n"
        f"地點：{location}\n"
        "造成不便敬請見諒。"
    )
    for uid in uids:
        try:
            line_bot_api.push_message(uid, TextSendMessage(text=message))
        except Exception as e:
            print(f"推播失敗: {uid}", e)

def notify_event_not_full(orderid):
    print(f"notify_event_not_full 被呼叫，orderid={orderid}")
    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    # 取得活動資料
    cursor.execute("""
        SELECT event.content as event_name, order_detail.booker, order_detail.start_time, order_detail.location, 
               order_detail.participants
        FROM order_detail 
        LEFT JOIN event ON order_detail.event_id = event.event_id 
        WHERE order_detail.orderid=%s
    """, (orderid,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return
    event_name = row.get('event_name', '您的活動')
    booker = row.get('booker')
    start_time = row.get('start_time')
    location = row.get('location', '未設定')
    participants_limit = row.get('participants', 0)

    # 格式化開始時間
    if start_time:
        try:
            if isinstance(start_time, (datetime.datetime, datetime.date)):
                start_time_str = start_time.strftime('%Y-%m-%d %H:%M')
            else:
                start_time_str = str(start_time)[:16].replace('T', ' ')
        except Exception:
            start_time_str = str(start_time)
    else:
        start_time_str = "未設定"

    # 目前參加人數
    cursor.execute("SELECT COUNT(*) as cnt FROM involvement WHERE orderid=%s", (orderid,))
    curr = cursor.fetchone()
    current_num = curr['cnt'] if curr and 'cnt' in curr else 0

    conn.close()
    message = TemplateSendMessage(
        alt_text="活動人數未滿，請決定是否繼續",
        template=ButtonsTemplate(
            title='活動人數未滿',
            text=f"您的活動人數未滿，是否要繼續舉辦？",
            actions=[
                PostbackAction(
                    label='繼續發起',
                    display_text='我要繼續發起活動',
                    data=f'action=continue_event&orderid={orderid}'
                ),
                PostbackAction(
                    label='取消活動',
                    display_text='我要取消活動',
                    data=f'action=cancel_event&orderid={orderid}'
                )
            ]
        )
    )
    try:
        line_bot_api.push_message(booker, message)
    except Exception as e:
        print('推播失敗', e)

def set_event_continue(orderid):
    conn = get_db()
    cursor = conn.cursor()
    # 將活動設為隱藏狀態（你可以自訂狀態名稱，例如「已隱藏」）
    cursor.execute("UPDATE order_detail SET state='已隱藏' WHERE orderid=%s", (orderid,))
    conn.commit()
    conn.close()

def cancel_event_and_notify_participants(orderid):
    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    # 取得參與者
    cursor.execute("SELECT uid FROM involvement WHERE orderid=%s", (orderid,))
    uids = [row['uid'] for row in cursor.fetchall()]
    # 活動資訊
    cursor.execute("SELECT event.content as event_name FROM order_detail LEFT JOIN event ON order_detail.event_id=event.event_id WHERE order_detail.orderid=%s", (orderid,))
    row = cursor.fetchone()
    event_name = row.get('event_name', '') if row else ''
    # 刪除活動（order_detail）
    cursor.execute("DELETE FROM order_detail WHERE orderid=%s", (orderid,))
    conn.commit()
    conn.close()
    msg = f"您參加的活動《{event_name}》因人數未滿已被發起人取消。"
    for uid in uids:
        try:
            line_bot_api.push_message(uid, TextSendMessage(text=msg))
        except Exception as e:
            print("推播失敗", e)



######################### register

#使用者跳轉到註冊頁面，偷取LINE的user_id
@app.route('/register', methods=['GET'])
def register_page():
    uid = request.args.get('uid')
    print("GET 傳進來的 UID：", uid)

    return render_template('register.html', uid=uid)

#使用者註冊
@app.route('/register', methods=['POST'])
def register():
    uid = request.form.get('uid')
    
    #lineid
    uid = request.form.get('uid')
    #暱稱
    username = request.form.get('username')
    #本名
    name = request.form.get('name')
    #性別
    gender = request.form.get('gender')
    #生日
    birthday = request.form.get('birthday')
    #電話號碼
    phone = request.form.get('phone')
    #身分證
    identify_ID = request.form.get('identify_ID')
    print("UID:", uid)


    # 生日驗證
    if birthday:
        try:
            birthday_date = datetime.datetime.strptime(birthday, '%Y-%m-%d').date()
            today = datetime.date.today()
            if birthday_date > today:
                return '''
                    <script>
                        alert('生日不能超過今天日期');
                        window.history.back();
                    </script>
                '''
            # 計算年齡
            age = today.year - birthday_date.year - ((today.month, today.day) < (birthday_date.month, birthday_date.day))
        except ValueError:
           return '''
                <script>
                    alert('生日格式錯誤，請用 YYYY-MM-DD');
                    window.history.back();
                </script>
            '''
        
    conn = get_db()
    cursor = conn.cursor()
    
    # 用uid判斷是否已註冊
    cursor.execute("SELECT * FROM user WHERE uid=%s", (uid,))
    if cursor.fetchone():
        conn.close()
        return "該帳號已經被註冊"

    # 插入資料
    cursor.execute("INSERT INTO user (uid, username, name, gender, birthday, phone, identify_ID) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                   (uid, username, name, gender, birthday, phone, identify_ID))
    conn.commit()
    cursor.close()
    conn.close()

    #進入主要網頁
    # return redirect(url_for('index'))
    return redirect(f'{NGROK_URL}/index?uid={uid}')

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


######################### 點擊richmenu 提供連結進入網頁

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    uid = event.source.user_id

    if data.startswith("action=continue_event") or data.startswith("action=cancel_event"):
        params = dict(item.split("=") for item in data.split("&"))
        action = params.get('action')
        orderid = params.get('orderid')
        if not orderid:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="缺少活動資訊，請稍後重試。"))
            return

        if action == 'continue_event':
            set_event_continue(orderid)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="已繼續發起活動。\n活動將不會在一般列表顯示，並會於開始時間自動結束。")
            )
        elif action == 'cancel_event':
            cancel_event_and_notify_participants(orderid)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="已取消活動並通知所有參與者。")
            )
        return  # 注意！處理完直接 return

    if data == "action=grade":
        grade_url = f"{NGROK_URL}/grade?uid={uid}"
        flex_message = FlexSendMessage(
            alt_text="前往評分頁面",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "前往評分頁面",
                            "weight": "bold",
                            "size": "xl",
                            "margin": "md"
                        },
                        {
                            "type": "text",
                            "text": "請點選下方按鈕開始評分",
                            "size": "sm",
                            "color": "#999999",
                            "wrap": True,
                            "margin": "md"
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "color": "#1DB446",
                            "action": {
                                "type": "uri",
                                "label": "開始評分",
                                "uri": grade_url
                            }
                        }
                    ]
                }
            }
        )
        line_bot_api.reply_message(event.reply_token, flex_message)

    elif data == "action=index":
        index_url = f"{NGROK_URL}/index?uid={uid}"
        flex_message = FlexSendMessage(
            alt_text="前往首頁",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "前往首頁",
                            "weight": "bold",
                            "size": "xl",
                            "margin": "md"
                        },
                        {
                            "type": "text",
                            "text": "請點選下方按鈕進入首頁",
                            "size": "sm",
                            "color": "#999999",
                            "wrap": True,
                            "margin": "md"
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "color": "#1DB446",
                            "action": {
                                "type": "uri",
                                "label": "進入首頁",
                                "uri": index_url
                            }
                        }
                    ]
                }
            }
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
    
    elif data == "action=profile":
        profile_url = f"{NGROK_URL}/profile?uid={uid}"
        flex_message = FlexSendMessage(
            alt_text="前往個人資料",
            contents={
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "前往個人資料",
                            "weight": "bold",
                            "size": "xl",
                            "margin": "md"
                        },
                        {
                            "type": "text",
                            "text": "請點選下方按鈕進入個人資料",
                            "size": "sm",
                            "color": "#999999",
                            "wrap": True,
                            "margin": "md"
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "color": "#1DB446",
                            "action": {
                                "type": "uri",
                                "label": "進入個人資料",
                                "uri": profile_url
                            }
                        }
                    ]
                }
            }
        )
        line_bot_api.reply_message(event.reply_token, flex_message)


######################### grade

#評分系統
@app.route('/grade')
@require_registered_user
def grade():
    uid = request.args.get('uid')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM user WHERE uid=%s", (uid,))
    result = cursor.fetchone()
    name = result['name'] if result else "未知使用者"
    cursor.close()
    conn.close()

    print(f"User Page - uid: {uid}, name: {name}")
    
    return render_template('grade.html', uid=uid, name=name)

@app.route("/api/grade", methods=["GET", "POST"])
def grade_api():
    try:
        uid = request.args.get("uid") if request.method == "GET" else request.form.get("uid")
        conn = get_db()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        if request.method == "POST":
            orderid = request.form.get("orderid")
            uid_list = request.form.getlist("uid_list[]")
            comment_list = request.form.getlist("comment_list[]")
            evaluation_list = request.form.getlist("evaluation_list[]")

            print("POST orderid:", orderid)
            print("POST uid:", uid)
            print("POST uid_list:", uid_list)
            print("POST comment_list:", comment_list)
            print("POST evaluation_list:", evaluation_list)

            cursor.execute("SELECT booker FROM order_detail WHERE orderid = %s", (orderid,))
            booker_id = cursor.fetchone()["booker"]

            for target_uid, comment, evaluation in zip(uid_list, comment_list, evaluation_list):
                evaluation = int(evaluation)

                if uid == booker_id:
                    # 發起者評分參與者
                    sql = "UPDATE involvement SET booker_eval = %s, evaluation = %s WHERE orderid = %s AND uid = %s"
                    print("UPDATE SQL:", sql, comment, evaluation, orderid, target_uid)
                    cursor.execute(sql, (comment, evaluation, orderid, target_uid))
                else:
                    # 參與者評分發起者
                    sql = "UPDATE involvement SET eval_to_booker = %s, evaluation = %s WHERE orderid = %s AND uid = %s"
                    print("UPDATE SQL:", sql, comment, evaluation, orderid, target_uid)
                    cursor.execute(sql, (comment, evaluation, orderid, uid))

            conn.commit()
            return "評分成功"

        # GET 取得活動
        sql = """
            SELECT od.orderid, 
                od.location, 
                od.start_time, 
                od.booker,
                inv.uid, 
                inv.eval_to_booker, 
                inv.booker_eval, 
                inv.evaluation,
                u.username AS participant_username,
                b.username AS booker_username
            FROM order_detail od
            JOIN involvement inv ON od.orderid = inv.orderid
            JOIN user u ON inv.uid = u.uid
            JOIN user b ON od.booker = b.uid
            WHERE (inv.uid = %s OR od.booker = %s) AND od.state = '已結束'
            ORDER BY od.start_time DESC
            """
        cursor.execute(sql, (uid, uid))
        result = cursor.fetchall()

        print("收到的 uid:", uid)
        print("查詢結果:", result)

        events_dict = {}
        for row in result:
            orderid = row["orderid"]
            if orderid not in events_dict:
                events_dict[orderid] = {
                    "orderid": orderid,
                    "location": row["location"],
                    "time": row["start_time"],
                    "booker": row["booker"],  # 用於判斷是誰發起
                    "booker_username": row["booker_username"],
                    "participants": [],
                    "can_rate": False,
                }

            # 加入參與者 uid 與 username
            participant = {
                "uid": row["uid"],
                "username": row["participant_username"]
            }
            if participant not in events_dict[orderid]["participants"]:
                events_dict[orderid]["participants"].append(participant)

        # 修正 can_rate 判斷
        for event in events_dict.values():
            # 發起者身份
            if uid == event["booker"]:
                # 只要有一位參與者(非自己)尚未被評分，can_rate=True
                cursor.execute(
                    "SELECT COUNT(*) AS cnt FROM involvement WHERE orderid=%s AND uid!=%s AND booker_eval IS NULL",
                    (event["orderid"], event["booker"])
                )
                cnt = cursor.fetchone()["cnt"]
                event["can_rate"] = cnt > 0
            else:
                # 參與者身份
                cursor.execute(
                    "SELECT eval_to_booker FROM involvement WHERE orderid=%s AND uid=%s",
                    (event["orderid"], uid)
                )
                row = cursor.fetchone()
                event["can_rate"] = row and row["eval_to_booker"] is None

        print("events_dict:", events_dict)
        print("jsonify:", [event for event in events_dict.values() if event["can_rate"]])

        return jsonify([event for event in events_dict.values() if event["can_rate"]])
    
    except Exception as e:
        print("錯誤:", e)
        return jsonify({"error": "伺服器錯誤"}), 500


######################### 進入揪團系統

#使用者介面
@app.route('/index')
@require_registered_user
def index():
    uid = request.args.get('uid')
    return render_template('index.html', uid=uid)


######################### index
@app.route('/api/<action>', methods=['GET', 'POST', 'OPTIONS'])
def api_router(action):
    if request.method == 'OPTIONS':
        return '', 204

    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # 用 DictCursor 方便直接用欄位名

    def fetch_all(sql, params=None):
        cursor.execute(sql, params or [])
        return cursor.fetchall()

    # ping
    if action == 'ping':
        return jsonify({'pong': True})

    # list_categories
    if action == 'list_categories':
        rows = fetch_all("SELECT categories_id, content FROM categories")
        return jsonify(rows)

    # list_event_types
    if action == 'list_event_types':
        rows = fetch_all("""SELECT e.event_id, e.content, c.categories_id, c.content as category_name 
                            FROM event e LEFT JOIN categories c ON e.categories_id=c.categories_id""")
        return jsonify(rows)
    
    # list_users
    if action == 'list_users':
        users = fetch_all("SELECT uid, username, name, gender, isadmin FROM user")
        for u in users:
            u['avatarUrl'] = ""
        return jsonify(users)
    
    # list_events
    if action == 'list_events':
        # --- 1. 先自動關閉/取消過期活動 ---
        now = datetime.datetime.now()
        cursor.execute("""
            SELECT orderid FROM order_detail
            WHERE deadtime < %s AND state = '已成立'
        """, (now,))
        expired = cursor.fetchall()
        for ev in expired:
            orderid = ev['orderid']
            # 取得目前參與人數
            cursor.execute("SELECT COUNT(*) as cnt FROM involvement WHERE orderid=%s", (orderid,))
            cnt = cursor.fetchone()['cnt']
            # 取得人數上限
            cursor.execute("SELECT participants FROM order_detail WHERE orderid=%s", (orderid,))
            participants_limit = cursor.fetchone()['participants']
            if cnt == 0:
                cursor.execute("DELETE FROM order_detail WHERE orderid=%s", (orderid,))
            elif cnt < participants_limit:
                notify_event_not_full(orderid)  # 傳送詢問訊息
                cursor.execute("UPDATE order_detail SET state='待確認' WHERE orderid=%s", (orderid,))
            else:
                cursor.execute("UPDATE order_detail SET state='已結束' WHERE orderid=%s", (orderid,))
        conn.commit()
        where = []
        params = []
        if request.args.get('cat'):
            where.append("c.categories_id=%s")
            params.append(request.args['cat'])
        if request.args.get('time'):
            where.append("od.deadtime>=%s")
            params.append(request.args['time'])
        sql = """SELECT od.*, e.content as event_name, c.content as category_name, c.categories_id,
                    COALESCE(od.male_limit+od.female_limit, od.participants) as participants_limit
                FROM order_detail od
                LEFT JOIN event e ON od.event_id = e.event_id
                LEFT JOIN categories c ON e.categories_id = c.categories_id
                WHERE od.state != '待確認'"""
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY od.deadtime DESC"
        events = fetch_all(sql, params)
        for ev in events:
            invs = fetch_all("SELECT uid FROM involvement WHERE orderid=%s", (ev['orderid'],))
            ev['participants_list'] = [i['uid'] for i in invs]
            ev['current_participants'] = len(ev['participants_list'])
            ev['starttime'] = ev.get('start_time')
            ev['deadtime'] = ev.get('deadtime')
        return jsonify(events)
    
    # event_detail
    if action == 'event_detail':
        orderid = request.args.get('orderid')
        evs = fetch_all("""SELECT od.*, e.content as event_name, c.content as category_name, c.categories_id,
                                COALESCE(od.male_limit+od.female_limit, od.participants) as participants_limit
                        FROM order_detail od
                        LEFT JOIN event e ON od.event_id = e.event_id
                        LEFT JOIN categories c ON e.categories_id = c.categories_id
                        WHERE od.orderid=%s""", (orderid,))
        if not evs:
            return jsonify({'error':'not found'}), 404
        ev = evs[0]
        invs = fetch_all("SELECT uid FROM involvement WHERE orderid=%s", (orderid,))
        ev['participants_list'] = [i['uid'] for i in invs]
        ev['starttime'] = ev.get('start_time')
        ev['deadtime'] = ev.get('deadtime')
        return jsonify(ev)

    # list_my_events
    if action == 'list_my_events':
        uid = request.args.get('uid')
        print("收到 list_my_events 請求，uid=", uid)
        if not uid:
            return jsonify({'error': '缺少 uid'}), 400
        sql = """SELECT od.*, e.content as event_name, c.content as category_name, c.categories_id,
                    COALESCE(od.male_limit+od.female_limit, od.participants) as participants_limit
                FROM order_detail od
                LEFT JOIN event e ON od.event_id = e.event_id
                LEFT JOIN categories c ON e.categories_id = c.categories_id
                WHERE od.booker=%s
                ORDER BY od.deadtime DESC"""
        events = fetch_all(sql, (uid,))
        for ev in events:
            invs = fetch_all("SELECT uid FROM involvement WHERE orderid=%s", (ev['orderid'],))
            ev['participants_list'] = [i['uid'] for i in invs]
            ev['current_participants'] = len(ev['participants_list'])
            ev['starttime'] = ev.get('start_time')
            ev['deadtime'] = ev.get('deadtime')
        return jsonify(events)
    
    # create_event
    if action == 'create_event' and request.method == 'POST':
        data = request.form if request.form else request.json
        booker = data.get('booker')
        event_id = data.get('event_id')
        deadtime = data.get('deadtime')
        start_time = data.get('start_time')
        location = data.get('location')
        participants = data.get('participants')
        annotation = data.get('annotation')
        gender_limit = data.get('gender_limit')
        male_limit = data.get('male_limit')
        female_limit = data.get('female_limit')
        print('gender_limit:', request.form.get('gender_limit'))

        # 取得現在時間
        now = datetime.datetime.now()
        

        cursor.execute("""
            SELECT COUNT(*) as cnt FROM order_detail
            WHERE booker=%s AND start_time=%s AND state='已成立'
        """, (booker, start_time))
        if cursor.fetchone()['cnt'] > 0:
            return jsonify({'message': '您已有相同開始時間的活動，請選擇不同時間！'}), 400


        if deadtime and start_time and deadtime > start_time:
            return jsonify({'message': '表單截止時間不能大於活動開始時間！'}), 400

        cursor.execute("""
        INSERT INTO order_detail
                (booker, location, deadtime, start_time, annotation, participants, state, event_id, male_limit, female_limit, gender_limit)
            VALUES
                (%s, %s, %s, %s, %s, %s, '已成立', %s, %s, %s, %s)
            """, (
                booker, location, deadtime, start_time, annotation, participants,
                event_id, male_limit, female_limit, gender_limit
        ))
        conn.commit()
        orderid = cursor.lastrowid
        return jsonify({'message':'活動已發起'})

    # join_event
    if action == 'join_event' and request.method == 'POST':
        data = request.form if request.form else request.json
        orderid = data.get('orderid')
        uid = data.get('uid')

        # 取得參加者性別
        user = fetch_all("SELECT gender FROM user WHERE uid=%s", (uid,))
        if not user or not user[0].get('gender'):
            return jsonify({'message':'無法取得使用者性別'})
        gender = user[0]['gender']  # '男' or '女'

        # 取得活動限制
        row = fetch_all("SELECT event_id, start_time FROM order_detail WHERE orderid=%s", (orderid,))
        if not row:
            return jsonify({'message': '活動不存在'})
        event_id = row[0]['event_id']
        start_time = row[0]['start_time']
        
        cursor.execute("""
            SELECT COUNT(*) as cnt FROM order_detail
            WHERE booker=%s AND start_time=%s AND state='已成立'
        """, (uid, start_time))
        if cursor.fetchone()['cnt'] > 0:
            return jsonify({'message': '您已有相同開始時間的活動，請選擇不同時間！'}), 400

        od = fetch_all("SELECT participants, male_limit, female_limit, male_num, female_num, gender_limit FROM order_detail WHERE orderid=%s", (orderid,))
        if not od:
            return jsonify({'message':'活動不存在'})

        limit = od[0]
        gender_limit = int(limit.get('gender_limit') or 0)
        # 只有性別限制為1才檢查性別名額
        if gender_limit == 1:
            if gender == '男':
                if not limit['male_limit'] or limit['male_limit'] == 0:
                    return jsonify({'message':'此活動不開放男性參加'})
                if limit['male_num'] >= limit['male_limit']:
                    return jsonify({'message':'男生名額已滿'})
            elif gender == '女':
                if not limit['female_limit'] or limit['female_limit'] == 0:
                    return jsonify({'message':'此活動不開放女性參加'})
                if limit['female_num'] >= limit['female_limit']:
                    return jsonify({'message':'女生名額已滿'})
        # 檢查總人數
        curr = fetch_all("SELECT COUNT(*) as cnt FROM involvement WHERE orderid=%s", (orderid,))
        if curr and curr[0]['cnt'] >= limit['participants']:
            return jsonify({'message':'活動人數已滿'})
        # 已經參加過
        check = fetch_all("SELECT * FROM involvement WHERE orderid=%s AND uid=%s", (orderid, uid))
        if check:
            return jsonify({'message':'您已參與'})
        # 正常加入
        cursor.execute("INSERT INTO involvement(orderid, uid) VALUES (%s, %s)", (orderid, uid))
        # 更新對應性別人數
        if gender_limit == 1:
            if gender == '男':
                cursor.execute("UPDATE order_detail SET male_num = male_num + 1 WHERE orderid=%s", (orderid,))
            elif gender == '女':
                cursor.execute("UPDATE order_detail SET female_num = female_num + 1 WHERE orderid=%s", (orderid,))
        conn.commit()
        return jsonify({'message':'加入成功'})

    # leave_event
    if action == 'leave_event' and request.method == 'POST':
        data = request.form if request.form else request.json
        orderid = data.get('orderid')
        uid = data.get('uid')
        od = fetch_all("SELECT booker FROM order_detail WHERE orderid=%s", (orderid,))
        if od and od[0]['booker'] == uid:
            return jsonify({'message':'發起人無法退出'})
        cursor.execute("DELETE FROM involvement WHERE orderid=%s AND uid=%s", (orderid, uid))
        conn.commit()
        return jsonify({'message':'已退出'})

    # cancel_event
    if action == 'cancel_event' and request.method == 'POST':
        data = request.form if request.form else request.json
        orderid = data.get('orderid')
        uid = data.get('uid')
        od = fetch_all("SELECT booker FROM order_detail WHERE orderid=%s", (orderid,))
        if not od or od[0]['booker'] != uid:
            return jsonify({'message':'只有發起人可取消'})
        
        notify_event_cancelled(orderid)

        cursor.execute("DELETE FROM order_detail WHERE orderid=%s", (orderid,))
        conn.commit()
        return jsonify({'message':'活動已取消'})

    # end_event
    if action == 'end_event' and request.method == 'POST':
        data = request.form if request.form else request.json
        orderid = data.get('orderid')
        uid = data.get('uid')
        od = fetch_all("SELECT booker FROM order_detail WHERE orderid=%s", (orderid,))
        print("orderid:", orderid, "uid:", uid)
        if not od or od[0]['booker'] != uid:
            return jsonify({'message': '只有發起人可結束活動'})
        cursor.execute("UPDATE order_detail SET state=%s WHERE orderid=%s", ('已結束', orderid))
        conn.commit()
        return jsonify({'message': '已結束活動'})
        
    return jsonify({'error': 'unknown action'}), 400


######################### admin
@app.route('/admin_api', methods=['GET', 'POST'])
def admin_api():
    if request.method == 'POST':
        # 全部都從 JSON 取
        data = request.get_json(force=True)
        action = data.get('action')
    else:
        # GET 用 query string
        action = request.args.get('action')
        data = request.args

    conn = get_db()
    cursor = conn.cursor()
    try:
        if action == 'get_max_event_id':
            cursor.execute("SELECT MAX(event_id) AS max_id FROM event")
            row = cursor.fetchone()
            return jsonify({'max_id': row['max_id'] if row['max_id'] is not None else 0})

        # 1. 類別
        if action == 'list_categories':
            cursor.execute("SELECT * FROM categories ORDER BY categories_id")
            return jsonify(cursor.fetchall())
        if action == 'add_category':
            name = data.get('name')
            cursor.execute("INSERT INTO categories (content) VALUES (%s)", (name,))
            conn.commit()
            return jsonify({'success': True})
        if action == 'delete_category':
            catid = data.get('id')
            cursor.execute("DELETE FROM categories WHERE categories_id = %s", (catid,))
            conn.commit()
            return jsonify({'success': True})

        # 2. 活動
        if action == 'list_events':
            cursor.execute("SELECT * FROM event")
            return jsonify(cursor.fetchall())
        if action == 'add_event':
            cat = data.get('cat')
            name = data.get('name')
            eid = data.get('id')
            cursor.execute("INSERT INTO event (event_id, categories_id, content) VALUES (%s, %s, %s)", (eid, cat, name))
            conn.commit()
            return jsonify({'success': True})
        if action == 'delete_event':
            eid = data.get('id')
            cursor.execute("DELETE FROM event WHERE event_id = %s", (eid,))
            conn.commit()
            return jsonify({'success': True})

        # 3. 訂單
        if action == 'list_orders':
            cursor.execute("SELECT o.orderid, o.booker, u.username, o.location, o.event_id, o.state FROM order_detail o LEFT JOIN user u ON o.booker = u.uid")
            return jsonify(cursor.fetchall())

        # 4. 評價
        if action == 'list_evals':
            cursor.execute("SELECT i.*, u.username FROM involvement i LEFT JOIN user u ON i.uid = u.uid")
            return jsonify(cursor.fetchall())

        # 5. 使用者
        if action == 'list_users':
            cursor.execute("SELECT * FROM user")
            return jsonify(cursor.fetchall())
        if action == 'delete_user':
            uid = data.get('uid')
            cursor.execute("DELETE FROM user WHERE uid = %s", (uid,))
            conn.commit()
            return jsonify({'success': True})

        return jsonify({'error': 'unknown action'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


######################### profile

@app.route('/profile', methods=['GET', 'POST'])
@require_registered_user
def profile():
    
    my_uid = request.args.get('uid')
    profile_uid = request.args.get('other_uid', my_uid)

    conn = get_db()
    cur = conn.cursor()

    # cur.execute("SELECT name FROM user WHERE uid=%s", (my_uid,))
    # result = cur.fetchone()
    # if not result:
    #     cur.close()  # 記得關
    #     conn.close()
    #     return render_template('register.html', uid=my_uid)

    # 管理員判斷
    cur.execute("SELECT isadmin FROM user WHERE uid = %s", (my_uid,))
    row = cur.fetchone()
    is_admin = (row and row['isadmin'] == 1)

    # 權限：自己或管理員可編輯
    canEdit = (my_uid == profile_uid) or is_admin
    print(f'canEdit={canEdit}, my_uid={my_uid}, profile_uid={profile_uid}, is_admin={is_admin}')  # debug

    # 更新個資
    if request.method == 'POST':
        if not canEdit:
            conn.close()
            return "你沒有權限編輯此用戶", 403
        new_username = request.form.get('username', '')
        new_name = request.form.get('name', '')
        new_gender = request.form.get('gender', '')
        new_birthday = request.form.get('birthday', None)
        new_phone = request.form.get('phone', '')
        new_intro = request.form.get('self_introduction', '')

        cur.execute("""
            UPDATE user SET 
                username = %s, 
                name = %s, 
                gender = %s, 
                birthday = %s, 
                phone = %s, 
                self_introduction = %s 
            WHERE uid = %s
        """, (new_username, new_name, new_gender, new_birthday, new_phone, new_intro, profile_uid))
        conn.commit()
        conn.close()
        return redirect(url_for('profile', uid=my_uid, other_uid=profile_uid))

    # 個人資料
    cur.execute("SELECT * FROM user WHERE uid = %s", (profile_uid,))
    user = cur.fetchone()

    # # 我發起的活動
    cur.execute("""
        SELECT od.*, e.content AS event_name 
        FROM order_detail od
        JOIN event e ON od.event_id = e.event_id
        WHERE od.booker = %s
    """, (profile_uid,))
    created_events = cur.fetchall()



    # 我參加的活動
    cur.execute("""
        SELECT od.*, e.content AS event_name, u.username AS booker_username, i.eval_to_booker, i.booker_eval, i.evaluation 
        FROM involvement i
        JOIN order_detail od ON i.orderid = od.orderid
        JOIN event e ON od.event_id = e.event_id
        JOIN user u ON od.booker = u.uid
        WHERE i.uid = %s
    """, (profile_uid,))
    joined_events = cur.fetchall()

    # 評價統計
    cur.execute("""
        SELECT 
          SUM(CASE WHEN i.evaluation = 1 THEN 1 ELSE 0 END) AS likes,
          SUM(CASE WHEN i.evaluation = -1 THEN 1 ELSE 0 END) AS dislikes
        FROM involvement i
        JOIN order_detail o ON i.orderid = o.orderid
        WHERE i.uid = %s AND o.booker != i.uid
    """, (profile_uid,))
    eval_data = cur.fetchone()
    # 防呆: 查不到時給預設值
    if not eval_data or eval_data['likes'] is None or eval_data['dislikes'] is None:
        eval_data = {'likes': 0, 'dislikes': 0}

    conn.close()
    return render_template(
        'profile.html',
        user=user,
        canEdit=canEdit,
        created_events=created_events,
        joined_events=joined_events,
        eval_data=eval_data,
        uid=my_uid,
        other_uid=profile_uid
    )


# 啟動 Flask
if __name__ == "__main__":
    print(app.url_map)
    app.run(port=8000, debug=True)
    # remind_events()
    # time.sleep(60)  # 每分鐘檢查一次