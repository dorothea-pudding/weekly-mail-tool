import os
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

# 從雲端環境變數讀取 Token 與 Secret
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
channel_secret = os.getenv("LINE_CHANNEL_SECRET")

if not channel_access_token or not channel_secret:
    print("Warning: LINE_CHANNEL_ACCESS_TOKEN or LINE_CHANNEL_SECRET is missing.")

configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route("/callback", methods=['POST'])
def callback():
    # 取得 LINE 傳來的簽章並驗證
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text
    user_id = event.source.user_id

    # 判斷指令是否為 /id 或是 我的ID
    if user_message.strip().lower() in ["/id", "我的id"]:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            
            reply_text = f"Your LINE User ID is:\n{user_id}\n\nPlease copy this and paste it into the LINE_USER_ID field in your .env file."
            
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )

# 雲端伺服器不需要 app.run()，會交由 gunicorn 啟動
