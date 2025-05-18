# from linebot import LineBotApi
# from linebot.exceptions import LineBotApiError
# from linebot.models import RichMenu, RichMenuArea, RichMenuSize, RichMenuBounds, MessageAction, PostbackAction,URIAction
# import json

# NGROK_URL = 'https://844a-61-216-173-5.ngrok-free.app'  # 你的 ngrok 網址
# line_bot_api = LineBotApi('5greXasUuMtXP4KYR526MH8jXiZrHYlVVlwMyFaam9Sad/zZlRPbovaRc9neqLJkhS7jLjYPdrGG1WYHzPWIdlZEdmohsWrmF5efXOKi2lp8Q3YUG7J/x2DeHGoou/72LwYl81b68pNqKBoxK/9lywdB04t89/1O/w1cDnyilFU=')

# student_rich_menu_id = None
# professor_rich_menu_id = None
# student_rich_menu = None
# professor_rich_menu = None

# # 設定 Rich Menu
# tudent_rich_menu_id = line_bot_api.create_rich_menu(rich_menu=student_rich_menu)
# professor_rich_menu_id = line_bot_api.create_rich_menu(rich_menu=professor_rich_menu)

# # 存到 JSON 檔
# richmenu_ids = {
#     "student": student_rich_menu_id,
#     "professor": professor_rich_menu_id
# }
# with open('richmenu_id.json', 'w') as f:
#     json.dump(richmenu_ids, f)


# button1 = RichMenuArea(  # 設定 RichMenu 的一個按鈕區域，命名為 "Button 1"，並設定 PostbackAction 動作
#     bounds=RichMenuBounds(x=0, y=0, width=1250, height=1686),
#     action=PostbackAction(label='button 1', data='action=input')
# )

# button2 = RichMenuArea(  # 設定 RichMenu 的第二個按鈕區域，命名為 "查詢個人資料"，並設定 MessageAction 動作
#     bounds=RichMenuBounds(x=1250, y=0, width=1250, height=1686),
#     action=MessageAction(label='發送訊息', text='發送訊息')
# )

# rich_menu = RichMenu(
#     size=RichMenuSize(width=2500, height=1686),  # 設定 RichMenu 大小
#     selected=True,
#     name='reservation',  # 設定 RichMenu 的名稱
#     chat_bar_text='reservation',  # 設定 RichMenu 在聊天視窗中的顯示文字
#     areas=[button1, button2]  # 設定 RichMenu 的點擊區域
# )


# student_rich_menu = RichMenu(
#     size=RichMenuSize(width=2500, height=843),
#     selected=True,
#     name='Student Menu',
#     chat_bar_text='選單',
#     areas=[
#         RichMenuArea(
#             bounds=RichMenuBounds(x=0, y=0, width=1250, height=843),
#             action=URIAction(label='預約系統', uri=f'{NGROK_URL}/student')
#         ),
#         # RichMenuArea(
#         #     bounds=RichMenuBounds(x=1250, y=0, width=1250, height=843),
#         #     action=URIAction(label='傳訊息', uri=f'{NGROK_URL}/student/message')
#         # )
#     ]
# )

# professor_rich_menu = RichMenu(
#     size=RichMenuSize(width=2500, height=843),
#     selected=True,
#     name='Professor Menu',
#     chat_bar_text='選單',
#     areas=[
#         RichMenuArea(
#             bounds=RichMenuBounds(x=0, y=0, width=2500, height=843),
#             action=URIAction(label='預約系統', uri=f'{NGROK_URL}/professor')
#         )

#     ]
# )
# try:
#     # === 建立並獲取 Rich Menu ID ===
#     student_rich_menu_id = line_bot_api.create_rich_menu(rich_menu=student_rich_menu)
#     professor_rich_menu_id = line_bot_api.create_rich_menu(rich_menu=professor_rich_menu)
#     print(f'學生 Rich Menu ID: {student_rich_menu_id}')
#     print(f'教授 Rich Menu ID: {professor_rich_menu_id}')

#     # === 上傳圖片到 Line 平台 ===
#     with open('C:/xampp/htdocs/linebot2.0/images/student_richmenu.png', 'rb') as f:
#         line_bot_api.set_rich_menu_image(student_rich_menu_id, 'image/png', f)
#         print('學生 Rich Menu 圖片已上傳')

#     with open('C:/xampp/htdocs/linebot2.0/images/professor_richmenu.png', 'rb') as f:
#         line_bot_api.set_rich_menu_image(professor_rich_menu_id, 'image/png', f)
#         print('教授 Rich Menu 圖片已上傳')

# except LineBotApiError as e:
#     print(f"發生錯誤: {e}")
from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuArea, RichMenuSize, RichMenuBounds, URIAction
from linebot.exceptions import LineBotApiError
import json

# 設定 LINE Bot API
NGROK_URL = 'https://33fb-211-72-73-194.ngrok-free.app'  # 你的 ngrok 網址
line_bot_api = LineBotApi('5greXasUuMtXP4KYR526MH8jXiZrHYlVVlwMyFaam9Sad/zZlRPbovaRc9neqLJkhS7jLjYPdrGG1WYHzPWIdlZEdmohsWrmF5efXOKi2lp8Q3YUG7J/x2DeHGoou/72LwYl81b68pNqKBoxK/9lywdB04t89/1O/w1cDnyilFU=')

# === 設定學生 Rich Menu ===
student_rich_menu = RichMenu(
    size=RichMenuSize(width=2500, height=843),
    selected=True,
    name='Student Menu',
    chat_bar_text='選單',
    areas=[
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=0, width=1250, height=843),
            action=URIAction(label='預約系統', uri=f'{NGROK_URL}/student')
        ),
        RichMenuArea(
            bounds=RichMenuBounds(x=1250, y=0, width=1250, height=843),
            action=URIAction(label='傳訊息', uri=f'{NGROK_URL}/student/message')
        )
    ]
)

# === 設定教授 Rich Menu ===
professor_rich_menu = RichMenu(
    size=RichMenuSize(width=2500, height=843),
    selected=True,
    name='Professor Menu',
    chat_bar_text='選單',
    areas=[
        RichMenuArea(
            bounds=RichMenuBounds(x=0, y=0, width=2500, height=843),
            action=URIAction(label='預約系統', uri=f'{NGROK_URL}/professor')
        )
    ]
)

try:
    # === 建立並獲取 Rich Menu ID ===
    student_rich_menu_id = line_bot_api.create_rich_menu(rich_menu=student_rich_menu)
    professor_rich_menu_id = line_bot_api.create_rich_menu(rich_menu=professor_rich_menu)
    print(f'學生 Rich Menu ID: {student_rich_menu_id}')
    print(f'教授 Rich Menu ID: {professor_rich_menu_id}')

    # === 上傳圖片到 LINE 平台 ===
    with open('C:/xampp/htdocs/linebot2.0/images/student_richmenu.png', 'rb') as f:
        line_bot_api.set_rich_menu_image(student_rich_menu_id, 'image/png', f)
        print('學生 Rich Menu 圖片已上傳')

    with open('C:/xampp/htdocs/linebot2.0/images/professor_richmenu.png', 'rb') as f:
        line_bot_api.set_rich_menu_image(professor_rich_menu_id, 'image/png', f)
        print('教授 Rich Menu 圖片已上傳')

    # === 儲存 ID 到 JSON 檔案 ===
    richmenu_ids = {
        "student": student_rich_menu_id,
        "professor": professor_rich_menu_id
    }
    with open('C:/xampp/htdocs/linebot2.0/richmenu_id.json', 'w') as f:
        json.dump(richmenu_ids, f)

except LineBotApiError as e:
    print(f"發生錯誤: {e}")