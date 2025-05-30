from flask import Flask, render_template, redirect, url_for, request, abort, jsonify, session
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
    database='project',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

#pip install line-bot-sdk
#pip install pymysql
#pip install Flask
#pip install flask-cors

with open('richmenu_id.json', 'r') as f:
    richmenu_ids = json.load(f)


#使用者的rich_menu
USER_RICH_MENU_ID = richmenu_ids['user']


# 全域變數，修改ngrok抓的8000
NGROK_URL = 'https://0f0a-61-216-173-102.ngrok-free.app'

# LOCALHOST_URL = 'http://localhost/linebot2.0'

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
        database='project',
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


#使用者介面
@app.route('/index')
def index():
    uid = request.args.get('uid')
    
    # 如果 u_id 不存在，代表可能是非法訪問
    if not uid:
        return "找不到 uid，請重新登入", 400
    
    name = session.get('name')
    print(f"User Page - uid: {uid}, name: {name}")

    # return render_template('index.html', uid=uid, name=name)
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
    name = result[0] if result else "未知使用者"
    cursor.close()
    conn.close()

    print(f"User Page - uid: {uid}, name: {name}")
    
    return render_template('grade.html', uid=uid, name=name)

@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == "action=grade":
        uid = event.source.user_id
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

        line_bot_api.reply_message(
            event.reply_token,
            flex_message
        )

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

            cursor.execute("SELECT booker FROM order_detail WHERE orderid = %s", (orderid,))
            booker_id = cursor.fetchone()["booker"]

            for target_uid, comment, evaluation in zip(uid_list, comment_list, evaluation_list):
                evaluation = int(evaluation)

                if uid == booker_id:
                    # 發起者評分參與者
                    sql = "UPDATE involvement SET booker_eval = %s, evaluation = %s WHERE orderid = %s AND uid = %s"
                    cursor.execute(sql, (comment, evaluation, orderid, target_uid))
                else:
                    # 參與者評分發起者
                    sql = "UPDATE involvement SET eval_to_booker = %s, evaluation = %s WHERE orderid = %s AND uid = %s"
                    cursor.execute(sql, (comment, evaluation, orderid, uid))

            conn.commit()
            return "評分成功"

        # GET 取得活動
        sql = """
        SELECT od.orderid, 
            c.content AS title, 
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
        JOIN categories c ON od.orderid = c.categories_id
        JOIN user u ON inv.uid = u.uid
        JOIN user b ON od.booker = b.uid
        WHERE (inv.uid = %s OR od.booker = %s) AND od.state = '已結束'
        ORDER BY od.start_time DESC
        """
        cursor.execute(sql, (uid, uid))
        result = cursor.fetchall()

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

            # 無論是否已經加入過該參與者，都要檢查是否還可以評分
            if uid == row["booker"]:
                # 發起者：若尚未對這位參與者評價
                if row["booker_eval"] is None:
                    events_dict[orderid]["can_rate"] = True
            else:
                # 參與者：若尚未對發起者評價
                if row["eval_to_booker"] is None:
                    events_dict[orderid]["can_rate"] = True

        return jsonify(list(events_dict.values()))
    
    except Exception as e:
        print("錯誤:", e)
        return jsonify({"error": "伺服器錯誤"}), 500


######################### index
# @app.after_request
# def after_request(response):
#     # CORS headers
#     response.headers["Access-Control-Allow-Origin"] = "*"
#     response.headers["Access-Control-Allow-Headers"] = "Content-Type"
#     response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
#     return response

@app.route('/api/<action>', methods=['GET', 'POST', 'OPTIONS'])
def api_router(action):
    if request.method == 'OPTIONS':
        return '', 204

    conn = get_db()
    cursor = conn.cursor()

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
            ev['participants_list'] = [i['uid'] for i in invs]  # 目前參加者陣列
            ev['current_participants'] = len(ev['participants_list'])  # 目前人數
            # participants_limit 已經在 SELECT 裡叫出來，記得有這個欄位
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
        ev['participants'] = [i['uid'] for i in invs]
        return jsonify(ev)

    # create_event
    if action == 'create_event' and request.method == 'POST':
        data = request.form if request.form else request.json
        booker = data.get('booker')
        event_id = data.get('eventType')
        deadtime = data.get('deadtime')
        location = data.get('location')
        participants = data.get('participants')
        annotation = data.get('annotation')
        cursor.execute("""INSERT INTO order_detail(booker, location, deadtime, annotation, participants, state, event_id)
                          VALUES (%s,%s,%s,%s,%s,'已成立',%s)""",
                       (booker, location, deadtime, annotation, participants, event_id))
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

    return jsonify({'error': 'unknown action'}), 400



# 啟動 Flask
if __name__ == "__main__":
    print(app.url_map)
    app.run(port=8000, debug=True)