"use client";

import Link from "next/link";
import { useState } from "react";
import type { NotificationItem } from "../data";

export function NotificationDetailContent({
  notification,
}: {
  notification: NotificationItem;
}) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <div className="space-y-5 px-5 py-6 sm:px-7">
        <p className="text-base font-semibold leading-7 text-slate-800">
          {notification.detailMessage}
        </p>

        {notification.benefitDetail ? (
          <div>
            <p className="text-sm font-semibold leading-6 text-slate-700">
              詳細はこちらからご確認ください。
            </p>
            <button
              type="button"
              onClick={() => setIsModalOpen(true)}
              className="mt-3 inline-flex h-10 items-center justify-center gap-2 rounded-[6px] bg-emerald-700 px-4 text-sm font-bold text-white transition hover:bg-emerald-800"
            >
              対象の給付金を見る
              <Icon path="m9 6 6 6-6 6" className="h-4 w-4" />
            </button>
          </div>
        ) : null}

        <div className="flex flex-col gap-3 border-t border-slate-200 pt-5 sm:flex-row sm:justify-end">
          <Link
            href="/benefits"
            className="inline-flex h-11 items-center justify-center gap-2 rounded-[6px] bg-emerald-700 px-5 text-sm font-bold text-white transition hover:bg-emerald-800"
          >
            給付金一覧を見る
            <Icon path="m9 6 6 6-6 6" className="h-4 w-4" />
          </Link>
        </div>
      </div>

      {notification.benefitDetail && isModalOpen ? (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/45 px-4 py-6"
          role="dialog"
          aria-modal="true"
          aria-labelledby="notification-benefit-title"
        >
          <div className="max-h-[calc(100vh-48px)] w-full max-w-2xl overflow-y-auto rounded-[8px] bg-white shadow-[0_24px_80px_-28px_rgba(15,23,42,0.65)]">
            <div className="flex items-start justify-between gap-4 border-b border-slate-200 px-5 py-4 sm:px-6">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded-[4px] bg-rose-500 px-2 py-1 text-xs font-bold text-white">
                    {notification.benefitDetail.flag}
                  </span>
                  <span className="rounded-[4px] border border-emerald-200 bg-emerald-50 px-2 py-1 text-xs font-bold text-emerald-700">
                    {notification.benefitDetail.statusLabel}
                  </span>
                </div>
                <h2
                  id="notification-benefit-title"
                  className="mt-3 text-xl font-bold leading-snug text-slate-950"
                >
                  {notification.benefitDetail.name}
                </h2>
                <p className="mt-1 text-sm font-semibold text-slate-500">
                  {notification.benefitDetail.provider}
                </p>
              </div>

              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="grid h-9 w-9 shrink-0 place-items-center rounded-[6px] border border-slate-200 text-slate-600 transition hover:bg-slate-50 hover:text-slate-950"
                aria-label="給付金詳細を閉じる"
              >
                <Icon path="M6 6l12 12M18 6 6 18" className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-5 px-5 py-5 sm:px-6">
              <div className="grid gap-3 sm:grid-cols-3">
                <DetailMetric label="マッチ度" value={`${notification.benefitDetail.score}点`} />
                <DetailMetric label="もらえる金額" value={notification.benefitDetail.amount} />
                <DetailMetric label="申請期限" value={notification.benefitDetail.deadline} />
              </div>

              <div className="grid gap-3 sm:grid-cols-3">
                <DetailMetric label="支援種別" value={notification.benefitDetail.supportType} />
                <DetailMetric label="申請方法" value={notification.benefitDetail.applicationMethod} />
                <DetailMetric label="データ信頼度" value={notification.benefitDetail.confidenceLabel} />
              </div>

              <section>
                <h3 className="text-sm font-bold text-slate-900">概要</h3>
                <p className="mt-2 text-sm leading-6 text-slate-700">
                  {notification.benefitDetail.overview}
                </p>
              </section>

              <section>
                <h3 className="text-sm font-bold text-slate-900">対象</h3>
                <p className="mt-2 text-sm leading-6 text-slate-700">
                  {notification.benefitDetail.target}
                </p>
              </section>

              <DetailList title="マッチした理由" items={notification.benefitDetail.reasons} />
              <DetailList title="確認が必要な項目" items={notification.benefitDetail.warnings} />
            </div>

            <div className="flex flex-col-reverse gap-3 border-t border-slate-200 px-5 py-4 sm:flex-row sm:justify-end sm:px-6">
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="inline-flex h-11 items-center justify-center rounded-[6px] border border-slate-200 bg-white px-5 text-sm font-bold text-slate-700 transition hover:bg-slate-50"
              >
                閉じる
              </button>
              <Link
                href="/benefits"
                className="inline-flex h-11 items-center justify-center rounded-[6px] bg-emerald-700 px-5 text-sm font-bold text-white transition hover:bg-emerald-800"
              >
                給付金一覧で確認する
              </Link>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}

function DetailMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[6px] border border-slate-200 bg-slate-50 px-4 py-3">
      <p className="text-xs font-bold text-slate-500">{label}</p>
      <p className="mt-1 text-base font-bold leading-5 text-slate-950">{value}</p>
    </div>
  );
}

function DetailList({
  title,
  items,
}: {
  title: string;
  items: readonly string[];
}) {
  return (
    <section>
      <h3 className="text-sm font-bold text-slate-900">{title}</h3>
      {items.length > 0 ? (
        <ul className="mt-2 space-y-2 text-sm leading-6 text-slate-700">
          {items.map((item) => (
            <li key={item} className="flex gap-2">
              <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-600" />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-2 text-sm leading-6 text-slate-500">なし</p>
      )}
    </section>
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
