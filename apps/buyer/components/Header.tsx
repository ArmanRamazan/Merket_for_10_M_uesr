"use client";

import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";

const ROLE_LABELS: Record<string, string> = {
  student: "Студент",
  teacher: "Преподаватель",
};

export function Header() {
  const { user, loading, logout } = useAuth();

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="text-xl font-bold">
          EduPlatform
        </Link>

        <nav className="flex items-center gap-4">
          <Link href="/" className="text-sm hover:underline">
            Курсы
          </Link>

          {loading ? (
            <span className="text-sm text-gray-400">...</span>
          ) : user ? (
            <>
              <Link href="/enrollments" className="text-sm hover:underline">
                Мои курсы
              </Link>
              <Link href="/notifications" className="text-sm hover:underline">
                Уведомления
              </Link>
              {user.role === "teacher" && user.is_verified && (
                <Link href="/courses/new" className="text-sm hover:underline">
                  Создать курс
                </Link>
              )}
              <span className="text-sm text-gray-500">{user.name}</span>
              <span className="rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-700">
                {ROLE_LABELS[user.role] || user.role}
              </span>
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
