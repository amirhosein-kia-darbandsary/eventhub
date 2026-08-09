# ADR-0012: استراتژی دیتابیس Integration Test

## وضعیت

Accepted

---

## Context

برای Integration Testها نیاز داشتیم تست‌ها روی دیتابیسی اجرا شوند که رفتار آن تا حد ممکن به محیط واقعی Production نزدیک باشد.

در ابتدا گزینه‌هایی مانند SQLite in-memory و Testcontainers مطرح بودند، اما در نهایت تصمیم گرفتیم تست‌ها مستقیماً به یک PostgreSQL واقعی متصل شوند.

### چرا SQLite کافی نبود؟

SQLite برای Unit Test یا تست‌های ساده مناسب است، اما برای Integration Test این پروژه نمی‌توانست رفتار واقعی PostgreSQL را به‌درستی شبیه‌سازی کند.

در این پروژه از قابلیت‌هایی استفاده می‌کنیم که رفتارشان به PostgreSQL وابسته است؛ از جمله:

* PostgreSQL Enum
* Transaction و Locking
* CHECK Constraintها
* رفتار واقعی Foreign Key و محدودیت‌های دیتابیس

بنابراین ممکن بود یک تست روی SQLite موفق شود، اما همان کد روی PostgreSQL با خطا مواجه شود.

هدف Integration Test این است که تعامل واقعی Application با Database را آزمایش کند؛ بنابراین استفاده از SQLite می‌توانست بخشی از خطاهای واقعی را پنهان کند.

---

## چرا Testcontainers انتخاب نشد؟

Testcontainers گزینه مناسبی برای Integration Test است، زیرا می‌تواند برای تست یک PostgreSQL واقعی و ایزوله ایجاد کند.

اما در محیط فعلی، Docker روی سرور اجرا می‌شد و Docker به صورت مستقیم روی محیط لوکال توسعه‌دهنده در دسترس نبود.

در نتیجه استفاده از Testcontainers در این مرحله عملی نبود و به جای اضافه کردن پیچیدگی و وابستگی به یک زیرساخت Docker در محیط توسعه، تصمیم گرفتیم مستقیماً به PostgreSQL موجود متصل شویم.

---

## Decision

Integration Testها مستقیماً روی یک PostgreSQL واقعی اجرا می‌شوند.

ساختار تست به صورت کلی به این شکل است:

```text
Integration Test
       │
       ▼
    FastAPI
       │
       ▼
  AsyncSession
       │
       ▼
 PostgreSQL واقعی
```

Database تست از Database اصلی جدا نگه داشته می‌شود تا اجرای تست‌ها روی داده‌های Development تأثیری نداشته باشد.

---

## مشکلات واقعی و راه‌حل‌ها

استفاده از PostgreSQL واقعی باعث شد چند مشکل واقعی که در محیط ساده‌تر ممکن بود دیده نشوند، شناسایی و حل شوند.

### ۱. مشکل Event Loop و Connection Pool

در ابتدا هنگام اجرای Integration Testهای Async با `asyncpg` با `InterfaceError` مواجه شدیم.

ترکیب `pytest-asyncio`، `TestClient` و Connection Pool باعث می‌شد Connection مربوط به یک AsyncIO context در context دیگری مورد استفاده قرار بگیرد.

در بررسی این مشکل، استفاده از `AsyncClient` به جای `TestClient` بررسی و اعمال شد تا کل مسیر تست Async باقی بماند.

راه‌حل تعیین‌کننده برای مشکل Connection، استفاده از `NullPool` برای `test_engine` بود.

با `NullPool`، Connectionها بین contextهای مختلف از Pool مجدداً استفاده نمی‌شوند و هر بار Connection موردنیاز ایجاد و پس از استفاده بسته می‌شود.

این تغییر باعث شد `InterfaceError` برطرف شود.

---

### ۲. وابستگی `Base.metadata.create_all()` به ترتیب Import

مشکل دیگری هنگام راه‌اندازی Schema تست مشاهده شد.

استفاده از:

```text
Base.metadata.create_all()
```

وابسته به این است که Modelهای SQLAlchemy قبل از اجرای آن Import شده باشند تا Tableهای آن‌ها در `Base.metadata` ثبت شده باشند.

بنابراین ترتیب Import می‌توانست روی Schema ایجادشده تأثیر بگذارد.

این مسئله نشان داد که برای راه‌اندازی واقعی Schema، اتکا به `create_all()` راه‌حل ایده‌آلی نیست و Migrationهای Alembic باید منبع اصلی Schema دیتابیس باشند.

در نتیجه Integration Test باید در نهایت بر اساس همان Migrationهایی اجرا شود که Schema واقعی پروژه را ایجاد می‌کنند.

---

## Alternatives Considered

| گزینه                                       | مزایا                                                         | معایب                                                                        |
| ------------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| SQLite in-memory                            | بسیار سریع، ساده و بدون نیاز به PostgreSQL                    | رفتار متفاوت در Enum، Locking، CHECK Constraint و سایر قابلیت‌های PostgreSQL |
| Database تست مشترک ساده                     | راه‌اندازی ساده و بدون ابزار اضافی                            | احتمال باقی ماندن داده بین تست‌ها و وابستگی تست‌ها به وضعیت Database         |
| Testcontainers                              | PostgreSQL واقعی، ایزوله و قابل تکرار                         | نیازمند Docker و زیرساخت مناسب در محیط اجرای تست                             |
| PostgreSQL واقعی جدا برای تست — انتخاب فعلی | رفتار واقعی PostgreSQL، بدون وابستگی به Docker/Testcontainers | نیازمند مدیریت Database تست و زیرساخت PostgreSQL                             |

---

## Consequences

### مزایا

* Integration Testها رفتار واقعی PostgreSQL را آزمایش می‌کنند.
* تفاوت‌های مهم SQLite و PostgreSQL باعث False Positive در تست‌ها نمی‌شوند.
* Constraintها، Enumها، Transactionها و رفتار دیتابیس واقعی آزمایش می‌شوند.
* مشکلات واقعی مربوط به AsyncPG، Event Loop و Connection Pool در محیط تست شناسایی شدند.
* وابستگی `create_all()` به ترتیب Import نیز آشکار شد.
* تست‌ها به Database اصلی وابسته نیستند و روی Database تست اجرا می‌شوند.

### یک نتیجه مهم

Integration Test توانست باگی را پیدا کند که Unit Test نتوانسته بود پیدا کند: **ثبت کاربر با Email تکراری**.

Unit Test منطق Service را به صورت مستقل بررسی می‌کرد، اما محدودیت `UNIQUE` در نهایت یک رفتار واقعی Database است.

Integration Test با اجرای مسیر واقعی:

```text
HTTP Request
    ↓
FastAPI
    ↓
Service
    ↓
Repository
    ↓
PostgreSQL
```

نشان داد که Database در برابر Email تکراری چه رفتاری دارد.

این دقیقاً یکی از دلایل اصلی وجود Integration Test است: بعضی خطاها متعلق به تعامل بین چند لایه هستند و در Unit Test یک لایه به تنهایی قابل مشاهده نیستند.

---

## معایب و ریسک‌ها

* تست‌ها به یک PostgreSQL واقعی وابسته هستند.
* اجرای آن‌ها نسبت به SQLite in-memory کندتر است.
* محیط تست نیازمند دسترسی به PostgreSQL است.
* Database تست باید به شکل صحیح مدیریت و پاک‌سازی شود.
* در آینده اگر محیط CI/CD مستقل و قابل تکرار باشد، Testcontainers می‌تواند دوباره به عنوان یک گزینه مناسب بررسی شود.

---

## DoD

Integration Testها باید بتوانند مسیرهای اصلی Application را روی PostgreSQL واقعی اجرا کنند و حداقل موارد زیر را پوشش دهند:

* اجرای Migration/Schema تست
* اجرای Request واقعی از طریق FastAPI
* تعامل واقعی با PostgreSQL
* Rollback یا Isolation مناسب بین تست‌ها
* بررسی Constraintهای دیتابیس
* شناسایی خطاهایی که Unit Test قادر به شناسایی آن‌ها نیست

یکی از نمونه‌های موفق این تصمیم، شناسایی **Duplicate Email** بود که در Unit Test دیده نشد اما Integration Test آن را در تعامل واقعی Application و PostgreSQL شناسایی کرد.

---

## نتیجه نهایی

برای این مرحله، PostgreSQL واقعی بهترین تعادل بین صحت تست و پیچیدگی زیرساختی است.

SQLite بیش از حد از محیط واقعی فاصله دارد و Testcontainers در محیط فعلی به دلیل وابستگی به Docker قابل استفاده نبود.

بنابراین فعلاً Integration Testها مستقیماً روی PostgreSQL تست اجرا می‌شوند و در صورت فراهم شدن زیرساخت مناسب CI/CD، Testcontainers به عنوان گزینه آینده قابل بررسی است.
