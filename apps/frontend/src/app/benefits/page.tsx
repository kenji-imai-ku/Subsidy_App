"use client";

import Link from "next/link";
import Image from "next/image";
import { useSearchParams } from "next/navigation";
import { Suspense, useMemo, useState } from "react";

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
};

type TabKey = "all" | "recommended" | "deadline";
type SortKey = "recommended" | "deadline" | "amount";
type ProfileSearchParams = {
  prefecture: string;
  birthYear: string;
  birthMonth: string;
  birthDay: string;
  householdIncome: string;
  familyType: string;
  childrenCount: string;
  gender: string;
  taxExempt: string;
};

// 画面確認用の給付金データ。後でAPI接続する場合も、この形を表示側の受け口にする。
const benefits = [
  {
    id: "childcare-support",
    name: "子育て世帯生活支援特別給付金",
    amount: "100,000円",
    deadline: "2024/12/31",
    overview:
      "低所得の子育て世帯を支援する給付金です。18歳未満の児童がいる世帯が対象です。",
    category: "子育て世帯向け",
    target: "子ども 1人",
    flag: "おすすめ",
    tone: "child",
  },
  {
    id: "tax-exempt-household",
    name: "住民税非課税世帯給付金",
    amount: "70,000円",
    deadline: "2024/06/30",
    overview: "住民税非課税世帯を対象とした給付金です。",
    category: "すべての世帯向け",
    target: "世帯単位",
    flag: "期限が近い",
    tone: "tax",
  },
  {
    id: "vocational-training",
    name: "高等職業訓練促進給付金",
    amount: "100,000円",
    deadline: "2024/12/31",
    overview:
      "資格取得のために養成機関で修業する方を支援する給付金です。",
    category: "ひとり親家庭向け",
    target: "月額支給",
    flag: "おすすめ",
    tone: "work",
  },
  {
    id: "housing-security",
    name: "住居確保給付金",
    amount: "53,700円",
    deadline: "随時受付",
    overview:
      "離職や収入減少により住居を失うおそれがある方へ家賃相当額を支援します。",
    category: "住まいの支援",
    target: "原則 3か月",
    flag: "確認が必要",
    tone: "housing",
  },
  {
    id: "medical-expense",
    name: "ひとり親家庭等医療費助成",
    amount: "医療費の一部",
    deadline: "随時受付",
    overview:
      "ひとり親家庭などを対象に、医療機関でかかった費用の一部を助成します。",
    category: "医療費助成",
    target: "親子対象",
    flag: "おすすめ",
    tone: "medical",
  },
  {
    id: "school-expense",
    name: "就学援助制度",
    amount: "学用品費など",
    deadline: "2024/07/31",
    overview:
      "小中学校に通うお子さまの学用品費、給食費などを援助する制度です。",
    category: "教育支援",
    target: "小中学生",
    flag: "期限が近い",
    tone: "school",
  },
  {
    id: "care-support",
    name: "介護保険負担限度額認定",
    amount: "食費・居住費を軽減",
    deadline: "随時受付",
    overview:
      "介護保険施設などを利用する方の食費や居住費の負担を軽減します。",
    category: "介護支援",
    target: "介護利用者",
    flag: "確認が必要",
    tone: "care",
  },
] as const satisfies readonly Benefit[];

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
  return (
    <Suspense fallback={<BenefitsPageFallback />}>
      <BenefitsPageContent />
    </Suspense>
  );
}

function BenefitsPageContent() {
  const searchParams = useSearchParams();
  const [activeTab, setActiveTab] = useState<TabKey>("all");
  const [sortKey, setSortKey] = useState<SortKey>("recommended");

  // プロフィール入力画面から渡されたURLクエリを、検索条件表示に使う値へ戻す。
  const profileSearchParams = useMemo<ProfileSearchParams>(() => {
    return {
      prefecture: searchParams.get("prefecture") ?? "",
      birthYear: searchParams.get("birthYear") ?? "",
      birthMonth: searchParams.get("birthMonth") ?? "",
      birthDay: searchParams.get("birthDay") ?? "",
      householdIncome: searchParams.get("householdIncome") ?? "",
      familyType: searchParams.get("familyType") ?? "",
      childrenCount: searchParams.get("childrenCount") ?? "",
      gender: searchParams.get("gender") ?? "",
      taxExempt: searchParams.get("taxExempt") ?? "",
    };
  }, [searchParams]);

  // 入力済みの項目だけを検索条件として表示し、未入力の項目は一覧から省く。
  const searchConditionLabels = useMemo(() => {
    return buildSearchConditionLabels(profileSearchParams);
  }, [profileSearchParams]);

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
  }, [activeTab, sortKey]);

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
                {tabLabels[tab]}（{getTabCount(tab)}件）
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
          {filteredBenefits.map((benefit) => (
            <BenefitCard key={benefit.id} benefit={benefit} />
          ))}
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
            <p className="text-lg font-bold leading-none">給付金サポート</p>
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
            対象: {benefit.target}
          </p>
          <p className="mt-2 text-sm leading-6 text-slate-600">{benefit.overview}</p>
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

function getTabCount(tab: TabKey) {
  if (tab === "recommended") return benefits.filter((benefit) => benefit.flag === "おすすめ").length;
  if (tab === "deadline") return benefits.filter((benefit) => benefit.flag === "期限が近い").length;
  return benefits.length;
}

function getPriorityValue(flag: BenefitFlag) {
  if (flag === "おすすめ") return 0;
  if (flag === "期限が近い") return 1;
  return 2;
}

function buildSearchConditionLabels(profile: ProfileSearchParams) {
  const labels = [
    profile.prefecture,
    getBirthConditionLabel(profile),
    profile.householdIncome ? `世帯年収 ${profile.householdIncome}` : "",
    profile.familyType,
    profile.childrenCount ? `子ども ${profile.childrenCount}人` : "",
    profile.gender ? `性別 ${profile.gender}` : "",
    profile.taxExempt ? `非課税世帯 ${profile.taxExempt}` : "",
  ] as const;

  return labels.filter((label) => label.length > 0);
}

function getBirthConditionLabel(profile: ProfileSearchParams) {
  const { birthYear, birthMonth, birthDay } = profile;
  if (!birthYear || !birthMonth || !birthDay) return "";

  const birthDate = new Date(
    Number(birthYear),
    Number(birthMonth) - 1,
    Number(birthDay)
  );

  if (Number.isNaN(birthDate.getTime())) return "";

  const age = getAge(birthDate);
  const formattedDate = [
    birthYear,
    birthMonth.padStart(2, "0"),
    birthDay.padStart(2, "0"),
  ].join("/");

  return `${age}歳（${formattedDate}生）`;
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
