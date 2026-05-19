import Link from "next/link";
import { AppHeader } from "@/components/AppHeader";
import { categoryTone, notifications, type NotificationItem } from "./data";

const tabs = [
  { key: "all", label: "すべて", count: 5 },
  { key: "newBenefit", label: "新着の給付金", count: 2 },
  { key: "deadline", label: "締め切りが近い", count: 1 },
  { key: "season", label: "その他", count: 2 },
] as const;

export default function NotificationsPage() {
  return (
    <main className="min-h-screen bg-white text-slate-950">
      <AppHeader />

      <div className="mx-auto w-full max-w-6xl px-4 py-7 sm:px-6 lg:px-8">
        <section>
          <div>
            <h1 className="text-2xl font-bold tracking-normal text-slate-950">
              お知らせ
            </h1>
            <p className="mt-2 text-sm font-semibold leading-6 text-slate-600">
              条件に合う新着給付金、締切が近い制度、これから始まる申請シーズンをお届けします。
            </p>
          </div>

          <div className="mt-8 flex gap-8 overflow-x-auto border-b border-slate-200">
            {tabs.map((tab, index) => (
              <button
                key={tab.key}
                type="button"
                className={`flex h-12 shrink-0 items-center gap-2 border-b-2 px-1 text-sm font-bold transition ${
                  index === 0
                    ? "border-emerald-600 text-emerald-700"
                    : "border-transparent text-slate-700 hover:text-emerald-700"
                }`}
              >
                {tab.label}
                {"count" in tab ? (
                  <span className="grid h-5 min-w-5 place-items-center rounded-full bg-rose-500 px-1 text-[10px] text-white">
                    {tab.count}
                  </span>
                ) : null}
              </button>
            ))}
          </div>

          <div className="mt-4 flex items-center justify-between gap-3">
            <p className="text-sm font-semibold text-slate-600">
              全5件を表示
            </p>
            <select className="h-11 rounded-[6px] border border-slate-200 bg-white px-4 text-sm font-bold text-slate-700 shadow-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100">
              <option>新しい順</option>
              <option>期限が近い順</option>
              <option>重要度順</option>
            </select>
          </div>

          <section className="mt-5 space-y-3" aria-label="お知らせ一覧">
            {notifications.map((notification) => (
              <NotificationCard key={notification.id} notification={notification} />
            ))}
          </section>

          <div className="mt-5 flex items-center justify-center gap-6 text-sm font-bold text-slate-700">
            <span className="grid h-9 w-9 place-items-center rounded-[6px] bg-emerald-700 text-white">
              1
            </span>
            <button type="button" className="hover:text-emerald-700">2</button>
            <button type="button" className="hover:text-emerald-700">3</button>
            <span>...</span>
            <button type="button" className="inline-flex items-center gap-2 hover:text-emerald-700">
              次へ
              <Icon path="m9 6 6 6-6 6" className="h-4 w-4" />
            </button>
          </div>
        </section>
      </div>
    </main>
  );
}

function NotificationCard({ notification }: { notification: NotificationItem }) {
  const tone = categoryTone[notification.category];

  return (
    <Link
      href={`/notifications/${notification.id}`}
      className="block rounded-[8px] border border-slate-200 bg-white shadow-[0_10px_26px_-22px_rgba(15,23,42,0.55)] transition hover:border-emerald-200 hover:bg-emerald-50/40"
    >
      <article className="grid gap-0 sm:grid-cols-[minmax(0,1fr)_150px_32px]">
        <div className="min-w-0 px-5 py-4">
          <span className={`rounded-[4px] px-2 py-1 text-xs font-bold ${tone.badge}`}>
            {notification.label}
          </span>
          <h2 className="mt-3 text-base font-bold leading-snug text-slate-950">
            {notification.title}
          </h2>
        </div>

        <div className="px-4 py-4 text-left text-xs font-semibold text-slate-600 sm:text-right">
          {notification.date}
        </div>

        <div className="flex items-start justify-end px-4 py-4">
          <Icon path="m9 6 6 6-6 6" className="h-5 w-5 text-slate-700" />
        </div>
      </article>
    </Link>
  );
}

function Icon({ path, className }: { path: string; className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      className={className}
      aria-hidden="true"
    >
      <path d={path} />
    </svg>
  );
}
