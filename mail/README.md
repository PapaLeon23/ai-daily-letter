# mail/

메일 발송용 파일. Google Apps Script(SKTL AI Link 발송기)가 이 파일을 읽어 "SKTL AI Link" 이름으로 메일을 보낸다.

- `daily-latest.json`: 매일 레터 최신 호. 필드: type("daily"), id("daily-YYYY-MM-DD"), issue, date(YYYY-MM-DD), subject, html, text
- `monthly-latest.json`: 월간 리뷰 최신 호(html은 templates/mail_monthly.html 기반). 필드: type("monthly"), id("monthly-YYYY-MM"), date(발행일 YYYY-MM-DD), subject, html, text

Apps Script는 id가 이전에 보낸 것과 다르고 date가 오늘(KST)일 때만 한 번 보낸다. 받는 사람 주소는 Apps Script 안에만 있다.
