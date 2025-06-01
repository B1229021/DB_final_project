from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuArea, RichMenuSize, RichMenuBounds, URIAction, PostbackAction
from linebot.exceptions import LineBotApiError
import json

# 設定 LINE Bot API
NGROK_URL = 'https://c3d4-60-250-225-145.ngrok-free.app'  # 你的 ngrok 網址
line_bot_api = LineBotApi('5greXasUuMtXP4KYR526MH8jXiZrHYlVVlwMyFaam9Sad/zZlRPbovaRc9neqLJkhS7jLjYPdrGG1WYHzPWIdlZEdmohsWrmF5efXOKi2lp8Q3YUG7J/x2DeHGoou/72LwYl81b68pNqKBoxK/9lywdB04t89/1O/w1cDnyilFU=')

# === 設定使用者 Rich Menu ===
user_rich_menu = RichMenu(
    size=RichMenuSize(width=2500, height=1686),
    selected=True,
    name='Booker Menu',
    chat_bar_text='選單',
    areas=[
        # 登入
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=0, width=1250, height=1686),
            action=PostbackAction(label="登入", data="action=index")
        ),
        # # 個人資料
        # RichMenuArea(
        #     bounds=RichMenuBounds(x=1250, y=0, width=1250, height=843),
        #     action=PostbackAction(label="個人資料", data="action=grade")
        # ),
        # # 評分
        # RichMenuArea(
        #     bounds=RichMenuBounds(x=1250, y=843, width=1250, height=843),
        #     action=PostbackAction(label="評分", data="action=profile")
        # ),
                # 個人資料
        RichMenuArea(
            bounds=RichMenuBounds(x=1250, y=0, width=1250, height=843),
            action=PostbackAction(label="個人資料", data="action=profile")
        ),
        # 評分
        RichMenuArea(
            bounds=RichMenuBounds(x=1250, y=843, width=1250, height=843),
            action=PostbackAction(label="評分", data="action=grade")
        ),
    ]
)

try:
    # === 建立並獲取 Rich Menu ID ===
    user_rich_menu_id = line_bot_api.create_rich_menu(rich_menu=user_rich_menu)
    print(f'user Rich Menu ID: {user_rich_menu_id}')

    # === 上傳圖片到 LINE 平台 ===
    with open('C:/xampp/htdocs/linebot3.0/static/images/richmenu.png', 'rb') as f:
        line_bot_api.set_rich_menu_image(user_rich_menu_id, 'image/png', f)
        print('使用者 Rich Menu 圖片已上傳')

    # === 儲存 ID 到 JSON 檔案 ===
    richmenu_ids = {
        "user": user_rich_menu_id,
    }
    with open('C:/xampp/htdocs/linebot3.0/richmenu_id.json', 'w') as f:
        json.dump(richmenu_ids, f)

except LineBotApiError as e:
    print(f"發生錯誤: {e}")