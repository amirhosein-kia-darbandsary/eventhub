import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  scenarios: {
    flash_sale: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "10s", target: 50 },   // شروع آروم: به ۵۰ کاربر برسه
        // { duration: "20s", target: 200 },  // جهش ناگهانی: شبیه‌سازی "فروش آغاز شد"
        // { duration: "30s", target: 200 },  // نگه‌داشتن فشار بالا
        // { duration: "10s", target: 0 },    // فروکش
      ],
    },
  },
  thresholds: {
    http_req_duration: ["p(95)<2000"],   // ۹۵٪ درخواست‌ها باید زیر ۲ ثانیه باشن
    http_req_failed: ["rate<0.05"],       // کمتر از ۵٪ خطای ۵xx قابل قبوله
  },
};

const BASE_URL = "http://localhost:8000";

export default function () {
  // فرض: یک ticket_type_id با موجودی محدود از قبل ساختی (مثلا با ۵۰ عدد موجودی)
  const TICKET_TYPE_ID = __ENV.TICKET_TYPE_ID || 1;

  // هر VU (کاربر مجازی) باید توکن خودش رو داشته باشه -- برای سادگی اینجا
  // فرض می‌کنیم یک توکن مشترک تستی از قبل داری (در عمل بهتره هر VU لاگین جدا بزنه)
  const token = __ENV.TEST_TOKEN;

  const res = http.post(
    `${BASE_URL}/reservations`,
    JSON.stringify({ ticket_type_id: Number(TICKET_TYPE_ID), quantity: 1 }),
    { headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` } }
  );

  check(res, {
    "status is 201 or 409": (r) => r.status === 201 || r.status === 409,
    "no 500 errors": (r) => r.status !== 500,
  });

  sleep(1);
}