


## اجرای تست‌ها

دو مجموعه‌ی جدا از تست داریم:

- **`pytest -m unit`** — سریع (چند ثانیه)، بدون هیچ وابستگی بیرونی. باید در
  **هر push، روی هر برنچ** اجرا بشه — چون هزینه‌اش تقریباً صفره.
- **`pytest -m integration`** — نیاز به یک Postgres واقعی داره (از طریق
  `.env.test`). کندتره. باید فقط روی **pull requestها به سمت `main`**
  اجرا بشه (نه هر commit)، تا CI رو کند نکنه.

CI (که هنوز نساختیمش) قرار است این دو مرحله رو جدا اجرا کنه:
1. `pytest -m unit` — روی هر push
2. `pytest -m integration` — فقط روی PR، با یک سرویس Postgres که در همون
   pipeline (مثلاً به‌عنوان یک "service container" در GitHub Actions) بالا میاد