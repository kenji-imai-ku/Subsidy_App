"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

type Benefit = {
  id: string;
  name: string;
  amount: string;
  deadline: string;
  overview: string;
  category: string;
  status: "申請受付中" | "確認が必要" | "まもなく締切";
};

const benefits: Benefit[] = [
  {
    id: "childcare-support",
    name: "子育て世帯生活支援特別給付金",
    amount: "児童1人あたり 5万円",
    deadline: "2026年6月30日",
    overview:
      "低所得の子育て世帯を対象に、食費や教育費などの負担を軽減するための給付金です。",
    category: "子育て",
    status: "申請受付中",
  },
  {
    id: "housing-support",
    name: "住居確保給付金",
    amount: "家賃相当額を原則3か月支給",
    deadline: "随時受付",
    overview:
      "離職や収入減少により住居を失うおそれがある方に、一定期間の家賃相当額を支援します。",
    category: "住まい",
    status: "確認が必要",
  },
  {
    id: "tax-exempt-household",
    name: "住民税非課税世帯向け給付金",
    amount: "1世帯あたり 3万円",
    deadline: "2026年5月31日",
    overview:
      "住民税非課税世帯など、物価高の影響を受けやすい世帯を対象に生活費を支援する給付金です。",
    category: "生活支援",
    status: "まもなく締切",
  },
];

const statusClass: Record<Benefit["status"], string> = {
  申請受付中: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  確認が必要: "bg-sky-50 text-sky-700 ring-sky-200",
  まもなく締切: "bg-amber-50 text-amber-700 ring-amber-200",
};

type SortKey = "deadline" | "amount";

export default function BenefitsPage() {
  const [sortKey, setSortKey] = useState<SortKey>("deadline");

  const sortedBenefits = useMemo(() => {
    return [...benefits].sort((a, b) => {
      if (sortKey === "deadline") {
        return getDeadlineValue(b.deadline) - getDeadlineValue(a.deadline);
      }

      return getAmountValue(b.amount) - getAmountValue(a.amount);
    });
  }, [sortKey]);

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-8 text-slate-900">
      <div className="mx-auto w-full max-w-5xl">
        <header className="mb-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:mb-8 md:p-6">
          <div className="flex w-full flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
            <div className="space-y-3">
              <p className="inline-block rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700 ring-1 ring-emerald-100">
                判定結果
              </p>
              <div className="flex flex-wrap items-center gap-3">
                <h1 className="text-2xl font-bold leading-tight text-slate-950 md:text-3xl">
                  該当する可能性がある給付金
                </h1>
                <span className="rounded-full bg-emerald-50 px-4 py-1.5 text-lg font-bold text-emerald-700 ring-1 ring-emerald-200">
                  {benefits.length}件
                </span>
              </div>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
              <label className="space-y-2">
                <span className="text-sm font-semibold text-slate-700">
                  並び替え
                </span>
                <select
                  value={sortKey}
                  onChange={(event) =>
                    setSortKey(event.target.value as SortKey)
                  }
                  className="h-11 w-full rounded-xl border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-800 shadow-sm outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 sm:w-40"
                >
                  <option value="deadline">期限順</option>
                  <option value="amount">支給金額順</option>
                </select>
              </label>

              <Link
                href="/"
                className="inline-flex h-11 items-center justify-center rounded-xl border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-emerald-300 hover:text-emerald-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2 md:w-auto"
              >
                入力内容を修正
              </Link>
            </div>
          </div>
        </header>

        <section
          className="w-full max-w-5xl space-y-4 lg:ml-0 lg:w-[58%] lg:max-w-none"
          aria-label="給付金一覧"
        >
          {sortedBenefits.map((benefit) => (
            <article
              key={benefit.id}
              className="rounded-2xl border border-slate-200 bg-white p-5 shadow-[0_10px_32px_-22px_rgba(15,23,42,0.45)] md:p-6"
            >
              <div className="flex flex-col gap-4">
                <div className="min-w-0 space-y-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                      {benefit.category}
                    </span>
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ring-1 ${statusClass[benefit.status]}`}
                    >
                      {benefit.status}
                    </span>
                  </div>
                  <h2 className="text-xl font-bold leading-snug text-slate-950">
                    {benefit.name}
                  </h2>
                  <p className="text-sm leading-6 text-slate-600">
                    {benefit.overview}
                  </p>
                </div>

                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  <Info
                    label="もらえる金額"
                    value={benefit.amount}
                    tone="amount"
                  />
                  <Info
                    label="申請期限"
                    value={benefit.deadline}
                    tone="deadline"
                  />
                </div>
              </div>
            </article>
          ))}
        </section>
      </div>
    </main>
  );
}

function Info({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "amount" | "deadline";
}) {
  const toneClass =
    tone === "amount"
      ? "border-emerald-200 bg-emerald-50 text-emerald-800"
      : "border-amber-200 bg-amber-50 text-amber-800";

  return (
    <div className={`rounded-xl border p-4 ${toneClass}`}>
      <p className="text-xs font-semibold">{label}</p>
      <p className="mt-2 text-lg font-bold leading-6">{value}</p>
    </div>
  );
}

function getDeadlineValue(deadline: string) {
  if (deadline === "随時受付") return Number.MAX_SAFE_INTEGER;

  const matched = deadline.match(/(\d{4})年(\d{1,2})月(\d{1,2})日/);
  if (!matched) return 0;

  const [, year, month, day] = matched;
  return new Date(Number(year), Number(month) - 1, Number(day)).getTime();
}

function getAmountValue(amount: string) {
  const tenThousandYen = amount.match(/(\d+)万円/);
  if (tenThousandYen) return Number(tenThousandYen[1]) * 10000;

  return 0;
}
