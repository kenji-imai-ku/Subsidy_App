"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type { FormEvent } from "react";
import { useMemo, useState } from "react";

const DEFAULT_API_BASE_URL = "http://localhost:8000" as const;
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_API_BASE_URL;

// 都道府県用の固定値（日本の全47都道府県）
const PREFECTURES = [
  "北海道",
  "青森県",
  "岩手県",
  "宮城県",
  "秋田県",
  "山形県",
  "福島県",
  "茨城県",
  "栃木県",
  "群馬県",
  "埼玉県",
  "千葉県",
  "東京都",
  "神奈川県",
  "新潟県",
  "富山県",
  "石川県",
  "福井県",
  "山梨県",
  "長野県",
  "岐阜県",
  "静岡県",
  "愛知県",
  "三重県",
  "滋賀県",
  "京都府",
  "大阪府",
  "兵庫県",
  "奈良県",
  "和歌山県",
  "鳥取県",
  "島根県",
  "岡山県",
  "広島県",
  "山口県",
  "徳島県",
  "香川県",
  "愛媛県",
  "高知県",
  "福岡県",
  "佐賀県",
  "長崎県",
  "熊本県",
  "大分県",
  "宮崎県",
  "鹿児島県",
  "沖縄県",
] as const;

// 世帯年収用の固定値
const INCOME_OPTIONS = [
  "200万円未満",
  "200万円〜400万円未満",
  "400万円〜600万円未満",
  "600万円〜800万円未満",
  "800万円〜1,000万円未満",
  "1,000万円以上",
] as const;

// 家族構成・性別・非課税世帯の選択肢
const FAMILY_OPTIONS = ["独身", "配偶者あり", "ひとり親", "その他"] as const;
const GENDER_OPTIONS = ["男性", "女性", "その他", "回答しない"] as const;
const TAX_EXEMPT_OPTIONS = ["はい", "いいえ", "わからない"] as const;

// プロフィール入力フォーム全体の型
type FormData = {
  name: string;
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

const currentYear = new Date().getFullYear();
// 生年月日の年/月プルダウンを生成
const years = Array.from({ length: 101 }, (_, i) => String(currentYear - i));
const months = Array.from({ length: 12 }, (_, i) => String(i + 1));

export default function ProfileInputPage() {
  const router = useRouter();
  // 画面内の入力値を1つのstateで管理
  const [formData, setFormData] = useState<FormData>({
    name: "",
    prefecture: "",
    birthYear: "",
    birthMonth: "",
    birthDay: "",
    householdIncome: "",
    familyType: "",
    childrenCount: "",
    gender: "",
    taxExempt: "",
  });
  const [submitError, setSubmitError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 選択済みの年・月から日数を計算
  const days = useMemo(() => {
    const year = Number(formData.birthYear);
    const month = Number(formData.birthMonth);

    if (!year || !month) return [];
    return Array.from(
      { length: new Date(year, month, 0).getDate() },
      (_, i) => String(i + 1)
    );
  }, [formData.birthYear, formData.birthMonth]);

  // フォーム値を更新する共通関数
  // 年/月の変更時に日を空に戻すことで、2/31のような不正日付を防ぐ
  const updateField = (key: keyof FormData, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [key]: value,
      ...(key === "birthYear" || key === "birthMonth" ? { birthDay: "" } : {}),
    }));
  };

  // バックエンドにプロフィールを保存してから、マッチング結果画面へ遷移する。
  const submitProfile = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitError("");
    setIsSubmitting(true);

    try {
      const response = await fetch(`${API_BASE_URL}/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...formData,
          childrenCount: formData.childrenCount || "0",
        }),
      });

      if (!response.ok) {
        const errorBody = (await response.json().catch(() => null)) as {
          detail?: string;
        } | null;
        throw new Error(errorBody?.detail ?? "プロフィールを保存できませんでした");
      }

      router.push("/benefits");
    } catch (error) {
      setSubmitError(
        error instanceof Error
          ? error.message
          : "プロフィールを保存できませんでした"
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    // 給付金判定の前段として、ユーザー属性を入力する画面
    <main className="min-h-screen bg-[linear-gradient(135deg,#f7fffb_0%,#f8fbff_52%,#eef8f3_100%)] text-slate-950">
      <SiteHeader />

      <div className="mx-auto w-full max-w-6xl px-4 py-9 sm:px-6 lg:px-8">
        <section className="text-center">
          <h1 className="text-2xl font-bold tracking-normal text-slate-950 sm:text-3xl">
            あなたについて教えてください
          </h1>
          <p className="mt-4 text-sm font-semibold leading-6 text-slate-700">
            いくつかの質問に答えるだけで、受け取れる可能性のある給付金を検索できます。
          </p>
        </section>

        <form
          className="mx-auto mt-8 w-full max-w-5xl rounded-[8px] border border-slate-200 bg-white p-5 shadow-[0_18px_50px_-34px_rgba(15,23,42,0.45)] sm:p-7 lg:p-9"
          onSubmit={submitProfile}
        >
          <section>
            <h2 className="text-xl font-bold text-emerald-700">基本情報</h2>

            <div className="mt-6 grid grid-cols-1 gap-x-7 gap-y-6 md:grid-cols-2">
              <Field label="お名前（ニックネーム可）">
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => updateField("name", e.target.value)}
                  placeholder="例）山田 太郎"
                  className={inputClass}
                />
              </Field>

              <Field label="性別" required>
                <select
                  value={formData.gender}
                  onChange={(e) => updateField("gender", e.target.value)}
                  className={inputClass}
                  required
                >
                  <option value="">選択してください</option>
                  {GENDER_OPTIONS.map((gender) => (
                    <option key={gender} value={gender}>
                      {gender}
                    </option>
                  ))}
                </select>
              </Field>

              <Field label="生年月日" required>
                <div className="grid grid-cols-3 gap-3">
                  <select
                    value={formData.birthYear}
                    onChange={(e) => updateField("birthYear", e.target.value)}
                    className={inputClass}
                    required
                  >
                    <option value="">年</option>
                    {years.map((year) => (
                      <option key={year} value={year}>
                        {year}
                      </option>
                    ))}
                  </select>
                  <select
                    value={formData.birthMonth}
                    onChange={(e) => updateField("birthMonth", e.target.value)}
                    className={inputClass}
                    required
                  >
                    <option value="">月</option>
                    {months.map((month) => (
                      <option key={month} value={month}>
                        {month}
                      </option>
                    ))}
                  </select>
                  <select
                    value={formData.birthDay}
                    onChange={(e) => updateField("birthDay", e.target.value)}
                    className={inputClass}
                    disabled={days.length === 0}
                    required
                  >
                    <option value="">日</option>
                    {days.map((day) => (
                      <option key={day} value={day}>
                        {day}
                      </option>
                    ))}
                  </select>
                </div>
              </Field>

              <Field label="お住まいの都道府県" required>
                <select
                  value={formData.prefecture}
                  onChange={(e) => updateField("prefecture", e.target.value)}
                  className={inputClass}
                  required
                >
                  <option value="">選択してください</option>
                  {PREFECTURES.map((prefecture) => (
                    <option key={prefecture} value={prefecture}>
                      {prefecture}
                    </option>
                  ))}
                </select>
              </Field>
            </div>
          </section>

          <section className="mt-8 border-t border-slate-200 pt-7">
            <h2 className="text-xl font-bold text-emerald-700">家族・収入</h2>

            <div className="mt-6 grid grid-cols-1 gap-x-7 gap-y-6 md:grid-cols-2">
              <Field label="家族構成" required>
                <SegmentedFamily
                  value={formData.familyType}
                  onChange={(value) => updateField("familyType", value)}
                />
              </Field>

              <Field label="子供の人数">
                <input
                  type="number"
                  min={0}
                  value={formData.childrenCount}
                  onChange={(e) =>
                    updateField("childrenCount", e.target.value)
                  }
                  placeholder="例）2"
                  className={inputClass}
                />
              </Field>

              <Field label="世帯年収（税込）" required>
                <select
                  value={formData.householdIncome}
                  onChange={(e) =>
                    updateField("householdIncome", e.target.value)
                  }
                  className={inputClass}
                  required
                >
                  <option value="">選択してください</option>
                  {INCOME_OPTIONS.map((income) => (
                    <option key={income} value={income}>
                      {income}
                    </option>
                  ))}
                </select>
              </Field>

              <Field label="非課税世帯かどうか" required>
                <select
                  value={formData.taxExempt}
                  onChange={(e) => updateField("taxExempt", e.target.value)}
                  className={inputClass}
                  required
                >
                  <option value="">選択してください</option>
                  {TAX_EXEMPT_OPTIONS.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </Field>
            </div>
          </section>

          {submitError ? (
            <p className="mt-6 rounded-[6px] border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700">
              {submitError}
            </p>
          ) : null}

          <div className="mt-8">
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex h-14 w-full items-center justify-center gap-3 rounded-[6px] bg-emerald-700 px-5 text-base font-bold text-white shadow-[0_12px_24px_-16px_rgba(4,120,87,0.75)] transition hover:bg-emerald-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-600 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              {isSubmitting ? "保存しています" : "入力内容を確認する"}
              <span aria-hidden="true">›</span>
            </button>
          </div>
        </form>

        <p className="mt-5 text-center text-sm font-semibold text-slate-500">
          入力した情報は暗号化され、安全に管理されます。
        </p>
      </div>
    </main>
  );
}

const inputClass =
  "h-14 w-full rounded-[6px] border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 disabled:bg-slate-100" as const;

function SiteHeader() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex h-20 w-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-full bg-emerald-50 ring-1 ring-emerald-100">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              className="h-7 w-7 text-emerald-700"
              aria-hidden="true"
            >
              <path d="M12 4c2.2 0 4 1.8 4 4 0 3.5-4 6-4 6S8 11.5 8 8c0-2.2 1.8-4 4-4Zm-7 9c3.5 0 7 3 7 7-3.5 0-7-3-7-7Zm14 0c-3.5 0-7 3-7 7 3.5 0 7-3 7-7Z" />
            </svg>
          </div>
          <div>
            <p className="text-lg font-bold leading-none">俺たちの血肉</p>
            <p className="mt-1 text-xs font-semibold text-slate-500">
              あなたに合った給付金を、かんたん検索
            </p>
          </div>
        </Link>

        <a
          href="#"
          className="hidden items-center gap-2 text-sm font-bold text-slate-700 hover:text-emerald-700 md:flex"
        >
          <span
            className="grid h-6 w-6 place-items-center rounded-full border border-emerald-700 text-xs text-emerald-700"
            aria-hidden="true"
          >
            ?
          </span>
          このサイトについて
        </a>
      </div>
    </header>
  );
}

function SegmentedFamily({
  value,
  onChange,
}: {
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="grid h-14 grid-cols-2 overflow-hidden rounded-[6px] border border-slate-300 bg-white">
      {FAMILY_OPTIONS.map((family) => (
        <button
          key={family}
          type="button"
          onClick={() => onChange(family)}
          className={`border-r border-slate-200 px-2 text-sm font-bold last:border-r-0 ${
            value === family
              ? "bg-emerald-700 text-white"
              : "text-slate-700 hover:bg-emerald-50"
          }`}
        >
          {family}
        </button>
      ))}
    </div>
  );
}

// ラベルと必須マークの表示を共通化する部品
function Field({
  label,
  required,
  className = "",
  children,
}: {
  label: string;
  required?: boolean;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={`space-y-2 ${className}`}>
      <span className="text-sm font-semibold text-slate-700">
        {label}
        {required && <span className="ml-1 text-rose-500">*</span>}
      </span>
      {children}
    </div>
  );
}
