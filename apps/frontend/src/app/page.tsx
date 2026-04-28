"use client";

import { useMemo, useState } from "react";

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
];

const INCOME_OPTIONS = [
  "200万円未満",
  "200万円〜400万円未満",
  "400万円〜600万円未満",
  "600万円〜800万円未満",
  "800万円〜1,000万円未満",
  "1,000万円以上",
];

const FAMILY_OPTIONS = ["独身", "配偶者あり", "ひとり親", "その他"];
const GENDER_OPTIONS = ["男性", "女性", "その他", "回答しない"];
const TAX_EXEMPT_OPTIONS = ["はい", "いいえ", "わからない"];

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
const years = Array.from({ length: 101 }, (_, i) => String(currentYear - i));
const months = Array.from({ length: 12 }, (_, i) => String(i + 1));

export default function ProfileInputPage() {
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

  const days = useMemo(() => {
    const year = Number(formData.birthYear);
    const month = Number(formData.birthMonth);

    if (!year || !month) return [];
    return Array.from(
      { length: new Date(year, month, 0).getDate() },
      (_, i) => String(i + 1)
    );
  }, [formData.birthYear, formData.birthMonth]);

  const updateField = (key: keyof FormData, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [key]: value,
      ...(key === "birthYear" || key === "birthMonth" ? { birthDay: "" } : {}),
    }));
  };

  return (
    <main className="min-h-screen bg-[linear-gradient(140deg,#fdf6ec_0%,#f8fbff_45%,#e9f6ef_100%)] px-4 py-8">
      <div className="mx-auto w-full max-w-3xl rounded-3xl border border-slate-200/70 bg-white/90 p-5 shadow-[0_10px_40px_-18px_rgba(10,40,20,0.28)] backdrop-blur md:p-8">
        <div className="mb-8 space-y-3">
          <p className="inline-block rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold tracking-wide text-emerald-700">
            給付金案内アプリ
          </p>
          <h1 className="text-2xl font-bold leading-tight text-slate-900 md:text-3xl">
            まずはプロフィールを入力してください
          </h1>
        </div>

        <form className="grid grid-cols-1 gap-5 md:grid-cols-2">
          <Field label="名前" required>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => updateField("name", e.target.value)}
              placeholder="例: 山田 太郎"
              className={inputClass}
            />
          </Field>

          <Field label="居住地（都道府県）" required>
            <select
              value={formData.prefecture}
              onChange={(e) => updateField("prefecture", e.target.value)}
              className={inputClass}
            >
              <option value="">選択してください</option>
              {PREFECTURES.map((prefecture) => (
                <option key={prefecture} value={prefecture}>
                  {prefecture}
                </option>
              ))}
            </select>
          </Field>

          <Field label="生年月日" required className="md:col-span-2">
            <div className="grid grid-cols-3 gap-3">
              <select
                value={formData.birthYear}
                onChange={(e) => updateField("birthYear", e.target.value)}
                className={inputClass}
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

          <Field label="世帯年収" required>
            <select
              value={formData.householdIncome}
              onChange={(e) => updateField("householdIncome", e.target.value)}
              className={inputClass}
            >
              <option value="">選択してください</option>
              {INCOME_OPTIONS.map((income) => (
                <option key={income} value={income}>
                  {income}
                </option>
              ))}
            </select>
          </Field>

          <Field label="家族構成" required>
            <select
              value={formData.familyType}
              onChange={(e) => updateField("familyType", e.target.value)}
              className={inputClass}
            >
              <option value="">選択してください</option>
              {FAMILY_OPTIONS.map((family) => (
                <option key={family} value={family}>
                  {family}
                </option>
              ))}
            </select>
          </Field>

          <Field label="子供の人数">
            <input
              type="number"
              min={0}
              value={formData.childrenCount}
              onChange={(e) => updateField("childrenCount", e.target.value)}
              placeholder="例: 2"
              className={inputClass}
            />
          </Field>

          <Field label="性別" required>
            <select
              value={formData.gender}
              onChange={(e) => updateField("gender", e.target.value)}
              className={inputClass}
            >
              <option value="">選択してください</option>
              {GENDER_OPTIONS.map((gender) => (
                <option key={gender} value={gender}>
                  {gender}
                </option>
              ))}
            </select>
          </Field>

          <Field label="非課税世帯かどうか" required className="md:col-span-2">
            <select
              value={formData.taxExempt}
              onChange={(e) => updateField("taxExempt", e.target.value)}
              className={inputClass}
            >
              <option value="">選択してください</option>
              {TAX_EXEMPT_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </Field>

          <div className="pt-2 md:col-span-2">
            <button
              type="button"
              className="w-full rounded-xl bg-emerald-600 px-5 py-3 font-semibold text-white transition hover:bg-emerald-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2"
            >
              入力内容を確認する
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}

const inputClass =
  "w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 disabled:bg-slate-100";

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
    <label className={`space-y-2 ${className}`}>
      <span className="text-sm font-semibold text-slate-700">
        {label}
        {required && <span className="ml-1 text-rose-500">*</span>}
      </span>
      {children}
    </label>
  );
}
