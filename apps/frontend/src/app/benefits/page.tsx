"use client";

import Link from "next/link";
import Image from "next/image";
import { useEffect, useMemo, useState } from "react";

const DEFAULT_API_BASE_URL = "http://localhost:8000" as const;
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_API_BASE_URL;

type BenefitTone =
  | "child"
  | "tax"
  | "work"
  | "housing"
  | "medical"
  | "school"
  | "care";
type BenefitFlag = "おすすめ" | "期限が近い" | "確認が必要";

type Benefit = {
  id: string;
  name: string;
  amount: string;
  deadline: string;
  overview: string;
  category: string;
  target: string;
  flag: BenefitFlag;
  tone: BenefitTone;
  provider: string;
  score: number;
  status: string;
  reasons: readonly string[];
  warnings: readonly string[];
};

type TabKey = "all" | "recommended" | "deadline";
type SortKey = "recommended" | "deadline" | "amount";
type ApiProfile = {
  id: number;
  name: string;
  prefecture: string;
  birthDate: string;
  householdIncome: string;
  familyType: string;
  childrenCount: number;
  gender: string;
  taxExempt: string;
};

type ApiProgram = {
  id: number;
  title: string;
  provider: string;
  summary: string;
  benefit: string | null;
  category: string | null;
  targetPrefecture: string | null;
  targetCity: string | null;
  targetWard: string | null;
  applicationUrl: string | null;
  deadline: string | null;
};

type ApiMatch = {
  program: ApiProgram;
  score: number;
  status: "eligible" | "possible" | string;
  reasons: string[];
  warnings: string[];
};

// タブの内部キーと画面表示名を分けて、絞り込み条件を扱いやすくする。
const tabLabels = {
  all: "すべて",
  recommended: "おすすめ",
  deadline: "期限が近い",
} as const satisfies Record<TabKey, string>;

// 給付金カテゴリごとの色味。カード左側のアイコン背景と文字色を揃える。
const toneClass = {
  child: "bg-rose-50 text-rose-500 ring-rose-100",
  tax: "bg-sky-50 text-sky-600 ring-sky-100",
  work: "bg-emerald-50 text-emerald-700 ring-emerald-100",
  housing: "bg-violet-50 text-violet-600 ring-violet-100",
  medical: "bg-teal-50 text-teal-600 ring-teal-100",
  school: "bg-amber-50 text-amber-600 ring-amber-100",
  care: "bg-lime-50 text-lime-700 ring-lime-100",
} as const satisfies Record<BenefitTone, string>;

// おすすめや期限の状態を、一覧で瞬時に判別できるバッジ色へ変換する。
const flagClass = {
  おすすめ: "bg-rose-500 text-white",
  期限が近い: "bg-sky-600 text-white",
  確認が必要: "bg-amber-500 text-white",
} as const satisfies Record<BenefitFlag, string>;

// 外部アイコン依存を増やさず、カテゴリごとの線画アイコンだけをここで管理する。
const iconPath = {
  child:
    "M12 21c4 0 7-2.7 7-6.5S16 8 12 8s-7 2.7-7 6.5S8 21 12 21Zm-4-9v-1a4 4 0 0 1 8 0v1M9 15h.01M15 15h.01M10 17c1.2.8 2.8.8 4 0",
  tax:
    "M7 3v4M17 3v4M4 9h16M6 5h12a2 2 0 0 1 2 2v12H4V7a2 2 0 0 1 2-2Zm3 8h2v2H9v-2Zm4 0h2v2h-2v-2Z",
  work:
    "M9 6V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v1M4 8h16v11H4V8Zm0 5h16M10 13v2h4v-2",
  housing:
    "M4 11 12 4l8 7v9h-5v-6H9v6H4v-9Z",
  medical:
    "M12 5v14M5 12h14M7 4h10a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V7a3 3 0 0 1 3-3Z",
  school:
    "M4 8 12 4l8 4-8 4-8-4Zm3 3v5c2.5 2 7.5 2 10 0v-5",
  care:
    "M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.7A4 4 0 0 1 19 10c0 5.5-7 10-7 10Z",
} as const satisfies Record<BenefitTone, string>;

export default function BenefitsPage() {
  const [activeTab, setActiveTab] = useState<TabKey>("all");
  const [sortKey, setSortKey] = useState<SortKey>("recommended");
  const [profile, setProfile] = useState<ApiProfile | null>(null);
  const [matches, setMatches] = useState<ApiMatch[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  // 保存済みプロフィールと、それをもとにしたマッチング結果をバックエンドから取得する。
  useEffect(() => {
    const fetchResults = async () => {
      setIsLoading(true);
      setLoadError("");

      try {
        const [profileResponse, matchesResponse] = await Promise.all([
          fetch(`${API_BASE_URL}/profile`),
          fetch(`${API_BASE_URL}/matches`),
        ]);

        if (!profileResponse.ok) {
          throw new Error("プロフィール情報を取得できませんでした");
        }

        if (!matchesResponse.ok) {
          throw new Error("給付金のマッチング結果を取得できませんでした");
        }

        const profileData = (await profileResponse.json()) as ApiProfile;
        const matchData = (await matchesResponse.json()) as ApiMatch[];

        setProfile(profileData);
        setMatches(matchData);
      } catch (error) {
        setLoadError(
          error instanceof Error
            ? error.message
            : "バックエンドとの接続に失敗しました"
        );
      } finally {
        setIsLoading(false);
      }
    };

    void fetchResults();
  }, []);

  // 入力済みの項目だけを検索条件として表示し、未入力の項目は一覧から省く。
  const searchConditionLabels = useMemo(() => {
    return profile ? buildSearchConditionLabels(profile) : [];
  }, [profile]);

  // APIレスポンスを画面表示用のBenefit型へ変換し、UI側の責務を描画に絞る。
  const benefits = useMemo(() => {
    return matches.map(mapMatchToBenefit);
  }, [matches]);

  // タブと並び替えは画面上だけの操作なので、元データを直接変更せず表示用配列を作る。
  const filteredBenefits = useMemo(() => {
    const filtered = benefits.filter((benefit) => {
      if (activeTab === "recommended") return benefit.flag === "おすすめ";
      if (activeTab === "deadline") return benefit.flag === "期限が近い";
      return true;
    });

    return [...filtered].sort((a, b) => {
      if (sortKey === "amount") return getAmountValue(b.amount) - getAmountValue(a.amount);
      if (sortKey === "deadline") return getDeadlineValue(a.deadline) - getDeadlineValue(b.deadline);
      return getPriorityValue(a.flag) - getPriorityValue(b.flag);
    });
  }, [activeTab, benefits, sortKey]);

  if (isLoading) {
    return <BenefitsPageFallback />;
  }

  return (
    <main className="min-h-screen bg-[linear-gradient(150deg,#f8fffc_0%,#f7fbff_48%,#f1f8f4_100%)] text-slate-950">
      <SiteHeader />

      <div className="mx-auto w-full max-w-7xl px-4 py-7 sm:px-6 lg:px-8">
        {/* 診断完了とヒット件数を最初に見せて、結果画面であることを明確にする。 */}
        <section className="relative h-[136px] overflow-hidden rounded-[8px] border border-emerald-100 bg-white/70 px-5 shadow-[0_18px_50px_-32px_rgba(15,23,42,0.45)] sm:px-8 lg:h-[148px] lg:px-10">
          <div className="flex h-full items-center gap-4">
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-white shadow-lg shadow-emerald-900/15">
                <Icon path="M6 12.5 10 16l8-9" className="h-7 w-7" />
              </div>
              <div>
                <p className="text-sm font-bold text-slate-700">
                  診断が完了しました！
                </p>
                <h1 className="mt-2 text-xl font-bold leading-snug sm:text-2xl">
                  あなたが受け取れる可能性のある給付金は{" "}
                  <span className="text-3xl text-emerald-700">{benefits.length}</span>{" "}
                  件ありました
                </h1>
              </div>
            </div>

            <div className="relative hidden h-full w-[240px] shrink-0 md:block lg:w-[280px]">
              <Image
                src="/benefits-woman.png"
                alt="スマートフォンを持つ女性のイラスト"
                width={140}
                height={180}
                priority
                className="absolute -bottom-4 left-0 h-[220px] w-[170px] object-contain object-bottom lg:h-[240px] lg:w-[186px]"
              />
            </div>
          </div>
        </section>

        {loadError ? (
          <section className="mt-5 rounded-[8px] border border-rose-200 bg-rose-50 px-5 py-4 text-sm font-semibold text-rose-700">
            {loadError}
          </section>
        ) : null}

        {/* 入力済み条件を一覧直前に置き、条件変更へ戻れる導線をまとめる。 */}
        <section className="mt-5 rounded-[8px] border border-slate-200 bg-white px-5 py-4 shadow-[0_10px_28px_-24px_rgba(15,23,42,0.55)]">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <div className="flex items-center gap-2 text-sm font-bold text-slate-900">
                <Icon path="M5 7h14M7 12h10M9 17h6" className="h-4 w-4 text-emerald-700" />
                現在の検索条件
              </div>
              <dl className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-sm text-slate-700">
                {searchConditionLabels.length > 0 ? (
                  searchConditionLabels.map((label) => (
                    <Condition key={label} label={label} />
                  ))
                ) : (
                  <Condition label="プロフィール未入力" />
                )}
              </dl>
            </div>

            <Link
              href="/"
              className="inline-flex h-11 items-center justify-center gap-2 rounded-[6px] border border-emerald-100 bg-white px-4 text-sm font-bold text-emerald-700 shadow-sm transition hover:border-emerald-300 hover:bg-emerald-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-600 focus-visible:ring-offset-2"
            >
              <Icon path="M4 16.5V20h3.5L18 9.5 14.5 6 4 16.5ZM13 7l3 3" className="h-4 w-4" />
              条件を変更する
            </Link>
          </div>
        </section>

        {/* 一覧の見方を切り替える操作群。画像のタブUIに合わせて下線で現在地を示す。 */}
        <div className="mt-7 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex gap-7 overflow-x-auto border-b border-slate-200">
            {(["all", "recommended", "deadline"] as const).map((tab) => (
              <button
                key={tab}
                type="button"
                onClick={() => setActiveTab(tab)}
                className={`h-11 shrink-0 border-b-2 px-1 text-sm font-bold transition ${
                  activeTab === tab
                    ? "border-emerald-600 text-emerald-700"
                    : "border-transparent text-slate-600 hover:text-slate-950"
                }`}
              >
                {tabLabels[tab]}（{getTabCount(tab, benefits)}件）
              </button>
            ))}
          </div>

          <label className="flex items-center gap-2 self-start md:self-auto">
            <span className="sr-only">並び替え</span>
            <select
              value={sortKey}
              onChange={(event) => setSortKey(event.target.value as SortKey)}
              className="h-11 rounded-[6px] border border-slate-200 bg-white px-4 text-sm font-bold text-slate-700 shadow-sm outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
            >
              <option value="recommended">おすすめ順</option>
              <option value="deadline">期限が近い順</option>
              <option value="amount">金額が高い順</option>
            </select>
          </label>
        </div>

        <section className="mt-4 space-y-4" aria-label="給付金一覧">
          {filteredBenefits.length > 0 ? (
            filteredBenefits.map((benefit) => (
              <BenefitCard key={benefit.id} benefit={benefit} />
            ))
          ) : (
            <div className="rounded-[8px] border border-slate-200 bg-white px-5 py-8 text-center text-sm font-semibold text-slate-600">
              条件に合う給付金はまだ見つかっていません。
            </div>
          )}
        </section>

        <button
          type="button"
          className="mt-4 h-11 w-full rounded-[6px] border border-emerald-100 bg-white text-sm font-bold text-emerald-700 shadow-sm transition hover:bg-emerald-50"
        >
          もっと詳しく知りたい方へ
        </button>

        <p className="mt-4 rounded-[6px] border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm leading-6 text-slate-700">
          この結果は、入力いただいた情報に基づく目安です。実際の受給可否は各制度の条件や審査により決定されます。
        </p>
      </div>
    </main>
  );
}

function SiteHeader() {
  return (
    // プロフィール入力画面と同じサービスに見えるよう、ブランドと主要ナビを固定表示する。
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex h-20 w-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-full bg-emerald-50 ring-1 ring-emerald-100">
            <Icon
              path="M12 4c2.2 0 4 1.8 4 4 0 3.5-4 6-4 6S8 11.5 8 8c0-2.2 1.8-4 4-4Zm-7 9c3.5 0 7 3 7 7-3.5 0-7-3-7-7Zm14 0c-3.5 0-7 3-7 7 3.5 0 7-3 7-7Z"
              className="h-7 w-7 text-emerald-700"
            />
          </div>
          <div>
            <p className="text-lg font-bold leading-none">俺たちの血肉</p>
            <p className="mt-1 text-xs font-semibold text-slate-500">
              あなたに合った給付金を、かんたん検索
            </p>
          </div>
        </Link>

        <nav className="hidden items-center gap-6 text-sm font-bold text-slate-700 md:flex">
          <a className="flex items-center gap-2 hover:text-emerald-700" href="#">
            <Icon path="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.7A4 4 0 0 1 19 10c0 5.5-7 10-7 10Z" className="h-5 w-5" />
            お気に入り
          </a>
          <a className="relative flex items-center gap-2 hover:text-emerald-700" href="#">
            <Icon path="M18 9a6 6 0 1 0-12 0c0 7-3 7-3 7h18s-3 0-3-7M10 19h4" className="h-5 w-5" />
            <span className="absolute -left-2 -top-2 grid h-5 w-5 place-items-center rounded-full bg-rose-500 text-[10px] text-white">
              2
            </span>
            お知らせ
          </a>
          <a className="flex items-center gap-2 hover:text-emerald-700" href="#">
            <Icon path="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm-7 8a7 7 0 0 1 14 0" className="h-5 w-5" />
            メニュー
          </a>
        </nav>
      </div>
    </header>
  );
}

function BenefitsPageFallback() {
  return (
    <main className="min-h-screen bg-[linear-gradient(150deg,#f8fffc_0%,#f7fbff_48%,#f1f8f4_100%)] text-slate-950">
      <SiteHeader />
      <div className="mx-auto w-full max-w-7xl px-4 py-7 sm:px-6 lg:px-8">
        <section className="rounded-[8px] border border-emerald-100 bg-white/70 px-5 py-6 shadow-[0_18px_50px_-32px_rgba(15,23,42,0.45)] sm:px-8 lg:px-10">
          <p className="text-sm font-bold text-slate-700">
            検索条件を読み込んでいます
          </p>
        </section>
      </div>
    </main>
  );
}

function BenefitCard({ benefit }: { benefit: Benefit }) {
  return (
    // 画像の右側画面に合わせ、制度名・金額・期限・操作を横並びで比較できる形にする。
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
            <span className="rounded-[4px] bg-emerald-50 px-2 py-1 text-xs font-bold text-emerald-700">
              {benefit.category}
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
          ) : null}
          <button
            type="button"
            className="mt-2 text-sm font-bold text-sky-600 hover:text-sky-700"
          >
            詳しく見る
          </button>
        </div>

        <Metric label="もらえる金額" value={benefit.amount} tone="amount" />
        <Metric label="申請期限" value={benefit.deadline} tone="deadline" />

        <div className="flex flex-col justify-center gap-3 border-t border-slate-100 px-5 py-5 md:border-l md:border-t-0">
          <button
            type="button"
            className="inline-flex h-11 items-center justify-center gap-2 rounded-[6px] border border-slate-200 bg-white px-3 text-sm font-bold text-slate-700 transition hover:border-rose-200 hover:bg-rose-50 hover:text-rose-600"
          >
            <Icon path="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.7A4 4 0 0 1 19 10c0 5.5-7 10-7 10Z" className="h-4 w-4" />
            お気に入り
          </button>
          <button
            type="button"
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

function Condition({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-4">
      <dt className="sr-only">検索条件</dt>
      <dd>{label}</dd>
      <span className="text-slate-300" aria-hidden="true">
        |
      </span>
    </div>
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

function getTabCount(tab: TabKey, benefits: readonly Benefit[]) {
  if (tab === "recommended") return benefits.filter((benefit) => benefit.flag === "おすすめ").length;
  if (tab === "deadline") return benefits.filter((benefit) => benefit.flag === "期限が近い").length;
  return benefits.length;
}

function getPriorityValue(flag: BenefitFlag) {
  if (flag === "おすすめ") return 0;
  if (flag === "期限が近い") return 1;
  return 2;
}

function buildSearchConditionLabels(profile: ApiProfile) {
  const labels = [
    profile.prefecture,
    getBirthConditionLabel(profile),
    profile.householdIncome ? `世帯年収 ${profile.householdIncome}` : "",
    profile.familyType,
    `子ども ${profile.childrenCount}人`,
    profile.gender ? `性別 ${profile.gender}` : "",
    profile.taxExempt ? `非課税世帯 ${profile.taxExempt}` : "",
  ] as const;

  return labels.filter((label) => label.length > 0);
}

function getBirthConditionLabel(profile: ApiProfile) {
  if (!profile.birthDate) return "";

  const birthDate = new Date(profile.birthDate);

  if (Number.isNaN(birthDate.getTime())) return "";

  const age = getAge(birthDate);
  const formattedDate = profile.birthDate.replaceAll("-", "/");

  return `${age}歳（${formattedDate}生）`;
}

function mapMatchToBenefit(match: ApiMatch): Benefit {
  const { program } = match;
  const flag = getBenefitFlag(match);

  return {
    id: String(program.id),
    name: program.title,
    amount: program.benefit ?? "公式情報を確認",
    deadline: program.deadline ? program.deadline.replaceAll("-", "/") : "随時受付",
    overview: program.summary,
    category: getCategoryLabel(program.category),
    target: getTargetLabel(program),
    flag,
    tone: getBenefitTone(program.category),
    provider: program.provider,
    score: match.score,
    status: match.status,
    reasons: match.reasons,
    warnings: match.warnings,
  };
}

function getBenefitFlag(match: ApiMatch): BenefitFlag {
  if (match.warnings.length > 0 || match.status === "possible") return "確認が必要";
  if (match.score >= 90) return "おすすめ";
  return "おすすめ";
}

function getCategoryLabel(category: string | null) {
  const categoryLabels: Record<string, string> = {
    housing: "住まいの支援",
    childcare: "子育て世帯向け",
    low_income: "低所得世帯向け",
  } as const;

  if (!category) return "支援制度";
  return categoryLabels[category] ?? category;
}

function getBenefitTone(category: string | null): BenefitTone {
  const categoryTones: Record<string, BenefitTone> = {
    housing: "housing",
    childcare: "child",
    low_income: "tax",
  } as const;

  if (!category) return "work";
  return categoryTones[category] ?? "work";
}

function getTargetLabel(program: ApiProgram) {
  const targets = [
    program.targetPrefecture,
    program.targetCity,
    program.targetWard,
  ].filter((target): target is string => Boolean(target));

  return targets.length > 0 ? targets.join(" ") : "全国または条件指定なし";
}

function getAge(birthDate: Date) {
  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  const hasBirthdayPassed =
    today.getMonth() > birthDate.getMonth() ||
    (today.getMonth() === birthDate.getMonth() &&
      today.getDate() >= birthDate.getDate());

  if (!hasBirthdayPassed) age -= 1;
  return age;
}

function getDeadlineValue(deadline: string) {
  if (deadline === "随時受付") return Number.MAX_SAFE_INTEGER;

  const date = new Date(deadline);
  if (Number.isNaN(date.getTime())) return Number.MAX_SAFE_INTEGER;
  return date.getTime();
}

function getAmountValue(amount: string) {
  const matched = amount.match(/([\d,]+)円/);
  if (!matched) return 0;
  return Number(matched[1].replaceAll(",", ""));
}
