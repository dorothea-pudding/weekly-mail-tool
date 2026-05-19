from app.services.gmail_service import GmailService
from app.services.importance_service import ImportanceService
from app.services.line_service import LineService
from app.core.config import settings

def main():
    importance = ImportanceService()
    line = LineService()

    all_accounts = settings.EMAILS

    # 用來儲存三大區塊的資料
    overview_events = []
    action_items = []
    account_summaries = {}

    for account in all_accounts:
        email_address = account["email"]
        # 取得信箱別名，若設定檔未提供 alias，則取信箱 @ 前面的名稱
        account_alias = account.get("alias", email_address.split('@')[0])
        
        print(f"Reading mailbox: {email_address} (Alias: {account_alias})")
        
        account_summaries[account_alias] = []

        try:
            gmail = GmailService(
                email_address,
                account["password"]
            )

            emails = gmail.fetch_last_7_days_emails()
            
            # 用於該信箱內部去重
            seen_summaries = set()

            for email_text in emails:
                result = importance.analyze(email_text)
                print(result)

                if result.get("important"):
                    title = result.get("title", "未命名事件")
                    summary = result.get("summary", "無摘要")
                    requires_action = result.get("requires_action", False)
                    action_item = result.get("action_item", "")

                    # 避免同信箱內記錄重複的信件內容
                    if summary not in seen_summaries:
                        seen_summaries.add(summary)
                        
                        # 1. 加入總覽清單
                        overview_events.append(
                            f"**{title}**：{summary}（來源：{account_alias}）。"
                        )
                        
                        # 2. 加入行動清單 (如果有要求行動)
                        if requires_action and action_item:
                            action_items.append(
                                f"**{title}**：{action_item}（來源：{account_alias}）。"
                            )
                        
                        # 3. 加入個別信箱重點摘要
                        account_summaries[account_alias].append(f"- {summary}")

        except Exception as e:
            print(f"Error processing mailbox {email_address}: {e}")

    # 檢查是否有收集到任何資料
    has_important_emails = bool(overview_events)

    if has_important_emails:
        # 開始組合最終報表字串
        report_lines = ["【本週綜合郵件週報】\n"]

        # 區塊 1：重要事件總覽
        report_lines.append("### 【本週重要事件總覽】")
        for i, event in enumerate(overview_events, 1):
            report_lines.append(f"{i}. {event}")
        
        report_lines.append("") 

        # 區塊 2：需採取行動事項
        report_lines.append("### 【需採取行動事項】")
        if action_items:
            for i, action in enumerate(action_items, 1):
                report_lines.append(f"{i}. {action}")
        else:
            report_lines.append("本週無須採取特別行動。")
            
        report_lines.append("")

        # 區塊 3：各信箱重點摘要
        report_lines.append("### 【各信箱重點摘要】")
        for alias, summaries in account_summaries.items():
            if summaries:
                report_lines.append(f"#### [{alias}]")
                report_lines.extend(summaries)
                report_lines.append("") 

        # 結語
        report_lines.append("---")
        report_lines.append("\n敬請您查看相關郵件內容，採取必要行動，並查詢詳細資訊。")

        # 合併為單一字串
        final_report = "\n".join(report_lines).strip()

        success = line.push(
            settings.LINE_USER_ID,
            final_report
        )

        if success:
            print("LINE push successful")
        else:
            print("LINE push failed")

    else:
        print("No important emails this week")

if __name__ == "__main__":
    main()
