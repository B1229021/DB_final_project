from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuArea, RichMenuSize, RichMenuBounds, URIAction
from linebot.exceptions import LineBotApiError
import json

# 設定 LINE Bot API
NGROK_URL = 'https://33fb-211-72-73-194.ngrok-free.app'  # 你的 ngrok 網址
line_bot_api = LineBotApi('5greXasUuMtXP4KYR526MH8jXiZrHYlVVlwMyFaam9Sad/zZlRPbovaRc9neqLJkhS7jLjYPdrGG1WYHzPWIdlZEdmohsWrmF5efXOKi2lp8Q3YUG7J/x2DeHGoou/72LwYl81b68pNqKBoxK/9lywdB04t89/1O/w1cDnyilFU=')

# === 設定使用者 Rich Menu ===
user_rich_menu = RichMenu(
    size=RichMenuSize(width=2500, height=843),
    selected=True,
    name='Booker Menu',
    chat_bar_text='選單',
    areas=[
        #新增
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=0, width=1250, height=422),
            action=URIAction(label='新增預約', uri=f'{NGROK_URL}/index')
        ),
        #刪除
        RichMenuArea(
            bounds=RichMenuBounds(x=1250, y=0, width=1250, height=422),
            action=URIAction(label='刪除預約', uri=f'{NGROK_URL}/index/message')
        ),
        #登入
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=422, width=1250, height=422),
            action=URIAction(label='登入', uri=f'{NGROK_URL}/index/message')
        ),
        #評分
        RichMenuArea(
            bounds=RichMenuBounds(x=1250, y=422, width=1250, height=422),
            action=URIAction(label='評分', uri=f'{NGROK_URL}/grade')
        )
    ]
)

try:
    # === 建立並獲取 Rich Menu ID ===
    user_rich_menu_id = line_bot_api.create_rich_menu(rich_menu=user_rich_menu)
    print(f'user Rich Menu ID: {user_rich_menu_id}')

    # === 上傳圖片到 LINE 平台 ===
    with open('C:/xampp/htdocs/linebot2.0/images/user_richmenu.png', 'rb') as f:
        line_bot_api.set_rich_menu_image(user_rich_menu_id, 'image/png', f)
        print('學生 Rich Menu 圖片已上傳')

    # === 儲存 ID 到 JSON 檔案 ===
    richmenu_ids = {
        "user": user_rich_menu_id,
    }
    with open('C:/xampp/htdocs/linebot2.0/richmenu_id.json', 'w') as f:
        json.dump(richmenu_ids, f)

except LineBotApiError as e:
    print(f"發生錯誤: {e}")