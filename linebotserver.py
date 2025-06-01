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


conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='project1',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

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
NGROK_URL = 'https://c3d4-60-250-225-145.ngrok-free.app'

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
def grade():
    uid = request.args.get('uid')

    if not uid:
        return "找不到 uid，請重新登入", 400

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
def index():
    uid = request.args.get('uid')
    if not uid:
        return "請從首頁登入", 400
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
            reviews = fetch_all("SELECT evaluation, eval_to_booker FROM involvement WHERE uid=%s", (u['uid'],))
            u['review_good'] = len([r for r in reviews if r['evaluation']==1])
            u['review_bad'] = len([r for r in reviews if r['evaluation']==-1])
            u['review_msgs'] = [r['eval_to_booker'] for r in reviews]
            u['avatarUrl'] = ""
        return jsonify(users)
    
    # list_events
    if action == 'list_events':
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
                 LEFT JOIN categories c ON e.categories_id = c.categories_id"""
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY od.deadtime DESC"
        events = fetch_all(sql, params)
        for ev in events:
            invs = fetch_all("SELECT uid FROM involvement WHERE orderid=%s", (ev['orderid'],))
            ev['participants_list'] = [i['uid'] for i in invs]
            ev['current_participants'] = len(ev['participants_list'])
            # 直接將 start_time, deadtime 原樣傳
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
        event_id = data.get('eventType')
        deadtime = data.get('deadtime')
        start_time = data.get('start_time')
        location = data.get('location')
        participants = data.get('participants')
        annotation = data.get('annotation')
        cursor.execute("""INSERT INTO order_detail(booker, location, deadtime, start_time, annotation, participants, state, event_id)
                          VALUES (%s,%s,%s,%s,%s,%s,'已成立',%s)""",
                       (booker, location, deadtime, start_time, annotation, participants, event_id))
        conn.commit()
        orderid = cursor.lastrowid
        cursor.execute("INSERT INTO involvement(orderid, uid, evaluation) VALUES (%s, %s, NULL)", (orderid, booker))
        conn.commit()
        return jsonify({'message':'活動已發起'})

    # join_event
    if action == 'join_event' and request.method == 'POST':
        data = request.form if request.form else request.json
        orderid = data.get('orderid')
        uid = data.get('uid')
        check = fetch_all("SELECT * FROM involvement WHERE orderid=%s AND uid=%s", (orderid, uid))
        if check:
            return jsonify({'message':'您已參與'})
        od = fetch_all("SELECT COALESCE(male_limit+female_limit, participants) as participants_limit FROM order_detail WHERE orderid=%s", (orderid,))
        curr = fetch_all("SELECT COUNT(*) as cnt FROM involvement WHERE orderid=%s", (orderid,))
        if curr and od and curr[0]['cnt'] >= od[0]['participants_limit']:
            return jsonify({'message':'活動已滿'})
        cursor.execute("INSERT INTO involvement(orderid, uid, evaluation) VALUES (%s, %s, NULL)", (orderid, uid))
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
            cursor.execute("INSERT INTO event (categories_id, content) VALUES (%s, %s)", (cat, name))
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
def profile():
    my_uid = request.args.get('uid')
    profile_uid = request.args.get('other_uid', my_uid)

    if not my_uid:
        return "請從首頁進入", 400

    conn = get_db()
    cur = conn.cursor()

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

    # 我發起的活動
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