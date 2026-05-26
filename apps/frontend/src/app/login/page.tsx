"use client";

import type { FormEvent, ReactNode } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { AppHeader } from "@/components/AppHeader";

export default function LoginPage() {
  const router = useRouter();

  const submitMockForm = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    router.push("/benefits");
  };

  return (
    <main className="min-h-screen bg-[linear-gradient(135deg,#f7fffb_0%,#f8fbff_50%,#eef8f3_100%)] text-slate-950">
      <AppHeader />

      <div className="mx-auto flex w-full max-w-6xl items-center px-4 py-10 sm:px-6 lg:min-h-[calc(100vh-80px)] lg:px-8 lg:py-12">
        <section className="grid w-full overflow-hidden rounded-[8px] border border-slate-200 bg-white shadow-[0_24px_70px_-42px_rgba(15,23,42,0.55)] lg:grid-cols-[0.9fr_1.1fr]">
          <div className="bg-emerald-800 px-6 py-8 text-white sm:px-8 lg:px-10 lg:py-12">
            <p className="text-sm font-bold text-emerald-100">
              給付金サポート
            </p>
            <h1 className="mt-4 text-2xl font-bold leading-tight sm:text-3xl">
              アカウントにログイン
            </h1>
            <p className="mt-4 max-w-sm text-sm font-semibold leading-7 text-emerald-50">
              保存した条件やお気に入り、お知らせをまとめて確認できます。
            </p>

            <div className="mt-8 space-y-4 text-sm font-semibold text-emerald-50">
              <BenefitPoint label="条件を保存" />
              <BenefitPoint label="気になる給付金を管理" />
              <BenefitPoint label="新着や締切のお知らせを確認" />
            </div>
          </div>

          <div className="px-5 py-7 sm:px-8 lg:px-10 lg:py-10">
            <div>
              <h2 className="text-xl font-bold text-slate-950">
                ログイン
              </h2>
              <p className="mt-2 text-sm font-semibold leading-6 text-slate-600">
                登録済みのメールアドレスとパスワードを入力してください。
              </p>
            </div>

            <form className="mt-7 space-y-5" onSubmit={submitMockForm}>
              <Field label="メールアドレス">
                <input
                  className={inputClass}
                  type="email"
                  name="email"
                  placeholder="example@example.com"
                  autoComplete="email"
                  required
                />
              </Field>

              <Field label="パスワード">
                <input
                  className={inputClass}
                  type="password"
                  name="password"
                  placeholder="8文字以上"
                  autoComplete="current-password"
                  minLength={8}
                  required
                />
              </Field>

              <div className="flex items-center justify-between gap-3 text-sm font-semibold text-slate-600">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-slate-300 text-emerald-700 focus:ring-emerald-600"
                  />
                  ログイン状態を保持
                </label>

                <Link href="#" className="text-emerald-700 hover:text-emerald-800">
                  パスワードを忘れた方
                </Link>
              </div>

              <button
                type="submit"
                className="inline-flex h-12 w-full items-center justify-center rounded-[6px] bg-emerald-700 px-5 text-sm font-bold text-white transition hover:bg-emerald-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-600 focus-visible:ring-offset-2"
              >
                ログイン
              </button>
            </form>

            <div className="mt-6 border-t border-slate-200 pt-5 text-center text-sm font-semibold text-slate-600">
              <Link href="/signup" className="text-emerald-700 hover:text-emerald-800">
                はじめて利用する方はこちら
              </Link>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

const inputClass =
  "h-12 w-full rounded-[6px] border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-900 shadow-sm outline-none transition placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100" as const;

function Field({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <label className="block">
      <span className="text-sm font-bold text-slate-800">{label}</span>
      <span className="mt-2 block">{children}</span>
    </label>
  );
}

function BenefitPoint({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-3">
      <span className="grid h-6 w-6 shrink-0 place-items-center rounded-full bg-white/15">
        <Icon path="m6 12 4 4 8-9" className="h-4 w-4" />
      </span>
      <span>{label}</span>
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
