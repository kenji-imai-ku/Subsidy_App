import Link from "next/link";
import { notFound } from "next/navigation";
import { AppHeader } from "@/components/AppHeader";
import { categoryTone, notifications } from "../data";
import { NotificationDetailContent } from "./NotificationDetailContent";

export function generateStaticParams() {
  return notifications.map((notification) => ({
    id: notification.id,
  }));
}

export default async function NotificationDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const notification = notifications.find((item) => item.id === id);

  if (!notification) {
    notFound();
  }

  const tone = categoryTone[notification.category];

  return (
    <main className="min-h-screen bg-white text-slate-950">
      <AppHeader />

      <div className="mx-auto w-full max-w-4xl px-4 py-7 sm:px-6 lg:px-8">
        <Link
          href="/notifications"
          className="inline-flex items-center gap-2 text-sm font-bold text-emerald-700 hover:text-emerald-800"
        >
          <Icon path="m15 18-6-6 6-6" className="h-4 w-4" />
          お知らせ一覧へ戻る
        </Link>

        <article className="mt-6 rounded-[8px] border border-slate-200 bg-white shadow-[0_14px_36px_-28px_rgba(15,23,42,0.55)]">
          <div className="border-b border-slate-200 px-5 py-5 sm:px-7">
            <div className="flex flex-wrap items-center gap-3">
              <span className={`rounded-[4px] px-2 py-1 text-xs font-bold ${tone.badge}`}>
                {notification.label}
              </span>
              <span className="text-xs font-bold text-slate-500">
                {notification.date}
              </span>
            </div>
            <h1 className="mt-4 text-2xl font-bold leading-snug tracking-normal text-slate-950">
              {notification.title}
            </h1>
          </div>

          <NotificationDetailContent notification={notification} />
        </article>
      </div>
    </main>
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
