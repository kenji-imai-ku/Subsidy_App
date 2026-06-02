"use client";

import { useState } from "react";
import { AppHeader } from "@/components/AppHeader";

type BenefitTone = "child" | "housing" | "school";
type BenefitFlag = "おすすめ" | "期限が近い" | "確認が必要";
type MatchStatus = "eligible" | "possible";

type FavoriteBenefit = {
  id: string;
  name: string;
  amount: string;
  deadline: string;
  overview: string;
  target: string;
  flag: BenefitFlag;
  tone: BenefitTone;
  provider: string;
  score: number;
  status: MatchStatus;
  statusLabel: string;
  supportType: string;
  applicationMethod: string;
  applicationUrl: string | null;
  confidenceLabel: string;
  reasons: readonly string[];
  warnings: readonly string[];
};

const favoriteBenefits = [
  {
    id: "housing-support",
    name: "住居確保給付金",
    amount: "家賃相当額（上限あり）",
    deadline: "2026/05/31（日）",
    overview: "離職や収入減少などにより、住居を失うおそれがある方を支援する制度です。",
    target: "離職中 / 収入減少 / 賃貸住宅",
    flag: "期限が近い",
    tone: "housing",
    provider: "京都市",
    score: 86,
    status: "possible",
    statusLabel: "確認後に対象の可能性",
    supportType: "助成",
    applicationMethod: "窓口",
    applicationUrl: null,
    confidenceLabel: "公式情報",
    reasons: [
      "居住地が対象地域に合致しています",
      "賃貸住宅にお住まいの条件を満たしています",
    ],
    warnings: ["収入減少の有無について確認が必要です"],
  },
  {
    id: "childcare-support",
    name: "子育て世帯生活支援特別給付金",
    amount: "1世帯あたり 50,000円",
    deadline: "2026/06/30（火）",
    overview: "子どもがいる世帯を対象に、生活費の一部を支援する給付金です。",
    target: "子育て世帯 / 所得条件あり",
    flag: "おすすめ",
    tone: "child",
    provider: "京都市",
    score: 94,
    status: "eligible",
    statusLabel: "条件に合致",
    supportType: "現金給付",
    applicationMethod: "オンライン / 窓口",
    applicationUrl: null,
    confidenceLabel: "確認済み",
    reasons: [
      "子どもがいる世帯向け条件に合致しています",
      "居住地が対象地域に合致しています",
    ],
    warnings: [],
  },
  {
    id: "school-expense",
    name: "就学援助制度",
    amount: "学用品費・給食費など",
    deadline: "2026/07/10（金）",
    overview: "小中学校に通う子どもの学用品費や給食費などを支援する制度です。",
    target: "小中学生のいる世帯 / 所得条件あり",
    flag: "確認が必要",
    tone: "school",
    provider: "京都市教育委員会",
    score: 78,
    status: "possible",
    statusLabel: "確認後に対象の可能性",
    supportType: "助成",
    applicationMethod: "学校 / 窓口",
    applicationUrl: null,
    confidenceLabel: "推定を含む",
    reasons: [
      "居住地が対象地域に合致しています",
      "就学支援に関連する制度です",
    ],
    warnings: ["世帯所得と在学状況の確認が必要です"],
  },
] as const satisfies readonly FavoriteBenefit[];

const toneClass = {
  child: "bg-rose-50 text-rose-500 ring-rose-100",
  housing: "bg-violet-50 text-violet-600 ring-violet-100",
  school: "bg-amber-50 text-amber-600 ring-amber-100",
} as const satisfies Record<BenefitTone, string>;

const flagClass = {
  おすすめ: "bg-rose-500 text-white",
  期限が近い: "bg-sky-600 text-white",
  確認が必要: "bg-amber-500 text-white",
} as const satisfies Record<BenefitFlag, string>;

const iconPath = {
  child:
    "M12 21c4 0 7-2.7 7-6.5S16 8 12 8s-7 2.7-7 6.5S8 21 12 21Zm-4-9v-1a4 4 0 0 1 8 0v1M9 15h.01M15 15h.01M10 17c1.2.8 2.8.8 4 0",
  housing: "M4 11 12 4l8 7v9h-5v-6H9v6H4v-9Z",
  school: "M4 8 12 4l8 4-8 4-8-4Zm3 3v5c2.5 2 7.5 2 10 0v-5",
} as const satisfies Record<BenefitTone, string>;

export default function FavoritesPage() {
  const [selectedBenefit, setSelectedBenefit] = useState<FavoriteBenefit | null>(null);

  return (
    <main className="min-h-screen bg-[linear-gradient(150deg,#f8fffc_0%,#f7fbff_48%,#f1f8f4_100%)] text-slate-950">
      <AppHeader authAction="logout" />

      <div className="mx-auto w-full max-w-7xl px-4 py-7 sm:px-6 lg:px-8">
        <section>
          <h1 className="text-2xl font-bold tracking-normal text-slate-950">
            お気に入り
          </h1>
          <p className="mt-2 text-sm font-semibold leading-6 text-slate-600">
            気になる給付金を保存して、申請期限や確認事項をまとめて見られます。
          </p>
        </section>

        <section className="mt-7 grid gap-4 md:grid-cols-2" aria-label="お気に入りの概要">
          <SummaryItem label="お気に入り" value={`${favoriteBenefits.length}件`} />
          <SummaryItem label="直近の期限" value="2026/05/31" />
        </section>

        <section className="mt-6 space-y-4" aria-label="お気に入り一覧">
          {favoriteBenefits.map((benefit) => (
            <FavoriteCard
              key={benefit.id}
              benefit={benefit}
              onOpenDetail={setSelectedBenefit}
            />
          ))}
        </section>
      </div>

      {selectedBenefit ? (
        <BenefitDetailModal
          benefit={selectedBenefit}
          onClose={() => setSelectedBenefit(null)}
        />
      ) : null}
    </main>
  );
}

function FavoriteCard({
  benefit,
  onOpenDetail,
}: {
  benefit: FavoriteBenefit;
  onOpenDetail: (benefit: FavoriteBenefit) => void;
}) {
  return (
    <article className="overflow-hidden rounded-[8px] border border-slate-200 bg-white shadow-[0_12px_32px_-26px_rgba(15,23,42,0.5)]">
      <div className="grid gap-0 md:grid-cols-[112px_minmax(0,1fr)_150px_150px_170px]">
        <div className={`flex items-center justify-center p-5 ring-1 ring-inset ${toneClass[benefit.tone]}`}>
          <div className="grid h-16 w-16 place-items-center rounded-[8px] bg-white/75 ring-1 ring-current/20">
            <Icon path={iconPath[benefit.tone]} className="h-10 w-10" />
          </div>
        </div>

        <div className="min-w-0 px-5 py-5">
          <div className="flex flex-wrap items-center gap-2">
            <span className={`rounded-[4px] px-2 py-1 text-xs font-bold ${flagClass[benefit.flag]}`}>
              {benefit.flag}
            </span>
            <span className={`rounded-[4px] border px-2 py-1 text-xs font-bold ${getStatusClass(benefit.status)}`}>
              {benefit.statusLabel}
            </span>
          </div>
          <h2 className="mt-3 text-lg font-bold leading-snug text-slate-950">
            {benefit.name}
          </h2>
          <p className="mt-2 text-xs font-bold text-slate-500">
            {benefit.provider} / 対象: {benefit.target}
          </p>
          <p className="mt-2 text-sm leading-6 text-slate-600">{benefit.overview}</p>
          <p className="mt-2 text-sm font-bold text-emerald-700">
            マッチ度 {benefit.score}点
          </p>
          {benefit.warnings.length > 0 ? (
            <p className="mt-2 text-xs font-semibold leading-5 text-amber-700">
              確認事項: {benefit.warnings.join(" / ")}
            </p>
          ) : (
            <p className="mt-2 text-xs font-semibold leading-5 text-emerald-700">
              入力内容では大きな確認事項はありません
            </p>
          )}
        </div>

        <Metric label="もらえる金額" value={benefit.amount} tone="amount" />
        <Metric label="申請期限" value={benefit.deadline} tone="deadline" />

        <div className="flex flex-col justify-center gap-3 border-t border-slate-100 px-5 py-5 md:border-l md:border-t-0">
          <button
            type="button"
            className="inline-flex h-11 items-center justify-center gap-2 rounded-[6px] border border-rose-200 bg-rose-50 px-3 text-sm font-bold text-rose-600 transition hover:bg-rose-100"
          >
            <Icon path="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.7A4 4 0 0 1 19 10c0 5.5-7 10-7 10Z" className="h-4 w-4" />
            保存済み
          </button>
          <button
            type="button"
            onClick={() => onOpenDetail(benefit)}
            className="inline-flex h-11 items-center justify-center gap-2 rounded-[6px] bg-emerald-700 px-3 text-sm font-bold text-white transition hover:bg-emerald-800"
          >
            詳細を見る
            <Icon path="m9 6 6 6-6 6" className="h-4 w-4" />
          </button>
        </div>
      </div>
    </article>
  );
}

function BenefitDetailModal({
  benefit,
  onClose,
}: {
  benefit: FavoriteBenefit;
  onClose: () => void;
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/45 px-4 py-6"
      role="dialog"
      aria-modal="true"
      aria-labelledby="favorite-benefit-detail-title"
    >
      <div className="max-h-[calc(100vh-48px)] w-full max-w-2xl overflow-y-auto rounded-[8px] bg-white shadow-[0_24px_80px_-28px_rgba(15,23,42,0.65)]">
        <div className="flex items-start justify-between gap-4 border-b border-slate-200 px-5 py-4 sm:px-6">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className={`rounded-[4px] px-2 py-1 text-xs font-bold ${flagClass[benefit.flag]}`}>
                {benefit.flag}
              </span>
              <span className={`rounded-[4px] border px-2 py-1 text-xs font-bold ${getStatusClass(benefit.status)}`}>
                {benefit.statusLabel}
              </span>
            </div>
            <h2
              id="favorite-benefit-detail-title"
              className="mt-3 text-xl font-bold leading-snug text-slate-950"
            >
              {benefit.name}
            </h2>
            <p className="mt-2 text-sm font-semibold text-slate-500">
              {benefit.provider}
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="grid h-9 w-9 shrink-0 place-items-center rounded-[6px] border border-slate-200 text-slate-600 transition hover:bg-slate-50 hover:text-slate-950"
            aria-label="詳細を閉じる"
          >
            <Icon path="M6 6l12 12M18 6 6 18" className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-5 px-5 py-5 sm:px-6">
          <div className="grid gap-3 sm:grid-cols-3">
            <DetailMetric label="マッチ度" value={`${benefit.score}点`} />
            <DetailMetric label="もらえる金額" value={benefit.amount} />
            <DetailMetric label="申請期限" value={benefit.deadline} />
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            <DetailMetric label="支援種別" value={benefit.supportType} />
            <DetailMetric label="申請方法" value={benefit.applicationMethod} />
            <DetailMetric label="データ信頼度" value={benefit.confidenceLabel} />
          </div>

          <section>
            <h3 className="text-sm font-bold text-slate-900">概要</h3>
            <p className="mt-2 text-sm leading-6 text-slate-700">
              {benefit.overview}
            </p>
          </section>

          <section>
            <h3 className="text-sm font-bold text-slate-900">対象</h3>
            <p className="mt-2 text-sm leading-6 text-slate-700">
              {benefit.target}
            </p>
          </section>

          <DetailList title="マッチした理由" items={benefit.reasons} />
          <DetailList title="確認が必要な項目" items={benefit.warnings} />
        </div>

        <div className="flex flex-col-reverse gap-3 border-t border-slate-200 px-5 py-4 sm:flex-row sm:justify-end sm:px-6">
          <button
            type="button"
            onClick={onClose}
            className="inline-flex h-11 items-center justify-center rounded-[6px] border border-slate-200 bg-white px-5 text-sm font-bold text-slate-700 transition hover:bg-slate-50"
          >
            閉じる
          </button>
          <button
            type="button"
            onClick={() => {
              if (benefit.applicationUrl) {
                window.open(benefit.applicationUrl, "_blank", "noopener,noreferrer");
              }
            }}
            disabled={!benefit.applicationUrl}
            className="inline-flex h-11 items-center justify-center rounded-[6px] bg-emerald-700 px-5 text-sm font-bold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {benefit.applicationUrl ? "申請ページを開く" : "公式情報を確認"}
          </button>
        </div>
      </div>
    </div>
  );
}

function SummaryItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[8px] border border-slate-200 bg-white px-5 py-4 shadow-[0_10px_28px_-24px_rgba(15,23,42,0.55)]">
      <p className="text-xs font-bold text-slate-500">{label}</p>
      <p className="mt-2 text-xl font-bold text-slate-950">{value}</p>
    </div>
  );
}

function DetailMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[6px] border border-slate-200 bg-slate-50 px-4 py-3">
      <p className="text-xs font-bold text-slate-500">{label}</p>
      <p className="mt-1 text-base font-bold text-slate-950">{value}</p>
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

function Metric({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "amount" | "deadline";
}) {
  const valueClass = tone === "amount" ? "text-emerald-700" : "text-rose-600";

  return (
    <div className="flex flex-col justify-center border-t border-slate-100 px-5 py-5 md:border-l md:border-t-0">
      <p className="text-xs font-bold text-slate-600">{label}</p>
      <p className={`mt-2 text-xl font-bold leading-tight ${valueClass}`}>{value}</p>
      {tone === "deadline" && value !== "随時受付" ? (
        <p className="mt-1 text-xs font-semibold text-slate-600">まで</p>
      ) : null}
    </div>
  );
}

function getStatusClass(status: MatchStatus) {
  if (status === "eligible") {
    return "border-emerald-200 bg-emerald-50 text-emerald-700";
  }

  return "border-amber-200 bg-amber-50 text-amber-700";
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
