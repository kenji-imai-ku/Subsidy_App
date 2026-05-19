import Link from "next/link";

export function AppHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex h-20 w-full max-w-[1500px] items-center justify-between px-5 sm:px-7 lg:px-9">
        <Link href="/" className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-[8px] bg-emerald-50 ring-1 ring-emerald-100">
            <Icon
              path="M12 4c2.2 0 4 1.8 4 4 0 3.5-4 6-4 6S8 11.5 8 8c0-2.2 1.8-4 4-4Zm-7 9c3.5 0 7 3 7 7-3.5 0-7-3-7-7Zm14 0c-3.5 0-7 3-7 7 3.5 0 7-3 7-7Z"
              className="h-7 w-7 text-emerald-700"
            />
          </div>
          <div>
            <p className="text-lg font-bold leading-none text-slate-950">
              給付金サポート
            </p>
            <p className="mt-1 text-xs font-semibold text-slate-500">
              あなたに合った給付金を、かんたん検索
            </p>
          </div>
        </Link>

        <nav className="hidden items-center gap-8 text-sm font-bold text-slate-800 md:flex">
          <Link className="flex items-center gap-2 hover:text-emerald-700" href="/benefits">
            <Icon path="M5 7h14M7 12h10M9 17h6" className="h-5 w-5" />
            給付金一覧
          </Link>
          <Link className="relative flex items-center gap-2 hover:text-emerald-700" href="/notifications">
            <Icon path="M18 9a6 6 0 1 0-12 0c0 7-3 7-3 7h18s-3 0-3-7M10 19h4" className="h-5 w-5 text-emerald-700" />
            <span className="absolute -right-3 -top-3 grid h-5 min-w-5 place-items-center rounded-full bg-rose-500 px-1 text-[10px] text-white">
              3
            </span>
            お知らせ
          </Link>
          <Link className="flex items-center gap-2 hover:text-emerald-700" href="#">
            <Icon path="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.7A4 4 0 0 1 19 10c0 5.5-7 10-7 10Z" className="h-5 w-5" />
            お気に入り
          </Link>
        </nav>
      </div>
    </header>
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
