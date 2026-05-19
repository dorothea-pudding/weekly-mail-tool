import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta

class GmailService:
    def __init__(self, email_address, password):
        self.email_address = email_address
        self.password = password
        self.imap_server = "imap.gmail.com"

    def fetch_last_7_days_emails(self):
        mail = imaplib.IMAP4_SSL(self.imap_server)
        mail.login(self.email_address, self.password)
        mail.select("inbox")

        # 計算 7 天前日期，強制使用英文月份，避免樹莓派中文語系導致 IMAP 格式錯誤
        past_date = datetime.now() - timedelta(days=7)
        en_months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        since_date = f"{past_date.day:02d}-{en_months[past_date.month - 1]}-{past_date.year}"

        # 讀取全部（不加 UNSEEN）
        status, messages = mail.search(None, f'(SINCE "{since_date}")')

        email_texts = []

        if status == "OK":
            for num in messages[0].split():
                status, msg_data = mail.fetch(num, "(RFC822)")
                if status != "OK":
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        # 確保寄件人也經過解碼，避免亂碼
                        subject = self._decode_mime(msg.get("Subject"))
                        from_ = self._decode_mime(msg.get("From"))

                        body = self._get_email_body(msg)

                        full_text = f"""
                            From: {from_}
                            Subject: {subject}

                            {body}
                            """
                        email_texts.append(full_text)

        mail.logout()
        return email_texts

    def _decode_mime(self, text):
        if not text:
            return ""
        decoded = decode_header(text)
        result = ""
        for part, encoding in decoded:
            if isinstance(part, bytes):
                result += part.decode(encoding or "utf-8", errors="ignore")
            else:
                result += part
        return result

    def _get_email_body(self, msg):
        html_body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # 略過附件
                if "attachment" in content_disposition:
                    continue

                if content_type == "text/plain":
                    return part.get_payload(decode=True).decode(errors="ignore")
                elif content_type == "text/html":
                    # 備用：如果沒有 text/plain，就保留 html 格式
                    html_body = part.get_payload(decode=True).decode(errors="ignore")
            
            # 若跑完迴圈都沒有 plain text，則回傳 html
            return html_body
        else:
            return msg.get_payload(decode=True).decode(errors="ignore")

        return ""
