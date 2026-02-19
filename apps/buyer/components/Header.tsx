"use client";

import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";

export function Header() {
  const { user, loading, logout } = useAuth();

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="text-xl font-bold">
          Marketplace
        </Link>

        <nav className="flex items-center gap-4">
          <Link href="/" className="text-sm hover:underline">
            Каталог
          </Link>

          {loading ? (
            <span className="text-sm text-gray-400">...</span>
          ) : user ? (
            <>
              <Link href="/products/new" className="text-sm hover:underline">
                Продать
              </Link>
              <span className="text-sm text-gray-500">{user.name}</span>
              <button
                onClick={logout}
                className="rounded bg-gray-200 px-3 py-1 text-sm hover:bg-gray-300"
              >
                Выйти
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="rounded bg-blue-600 px-3 py-1 text-sm text-white hover:bg-blue-700"
              >
                Войти
              </Link>
              <Link href="/register" className="text-sm hover:underline">
                Регистрация
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
