"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { courses, enrollments, type Course } from "@/lib/api";
import { Header } from "@/components/Header";
import { useAuth } from "@/hooks/use-auth";

export default function MyCoursesPage() {
  const { user, token } = useAuth();
  const [myCourses, setMyCourses] = useState<Course[]>([]);
  const [enrollCounts, setEnrollCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token || !user || user.role !== "teacher") {
      setLoading(false);
      return;
    }
    courses.my(token, { limit: 100 }).then(async (r) => {
      setMyCourses(r.items);
      const counts: Record<string, number> = {};
      await Promise.all(
        r.items.map(async (c) => {
          try {
            const res = await enrollments.courseCount(c.id);
            counts[c.id] = res.count;
          } catch {
            counts[c.id] = 0;
          }
        }),
      );
      setEnrollCounts(counts);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [token, user]);

  return (
    <>
      <Header />
      <main className="mx-auto max-w-4xl px-4 py-6">
        <h1 className="mb-4 text-2xl font-bold">Мои курсы</h1>

        {user?.role === "teacher" && !user.is_verified && (
          <div className="mb-4 rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-800">
            Ваш аккаунт ожидает верификации. После одобрения администратором вы сможете создавать курсы.
          </div>
        )}

        {!user ? (
          <p className="text-gray-500">
            <Link href="/login" className="text-blue-600 hover:underline">Войдите</Link> для просмотра
          </p>
        ) : user.role !== "teacher" ? (
          <p className="text-gray-500">Эта страница доступна только преподавателям</p>
        ) : loading ? (
          <p className="text-gray-400">Загрузка...</p>
        ) : myCourses.length === 0 ? (
          <p className="text-gray-500">У вас пока нет курсов.{" "}
            <Link href="/courses/new" className="text-blue-600 hover:underline">Создать курс</Link>
          </p>
        ) : (
          <div className="space-y-3">
            {myCourses.map((c) => (
              <div
                key={c.id}
                className="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-4"
              >
                <div>
                  <Link href={`/courses/${c.id}`} className="font-semibold hover:underline">
                    {c.title}
                  </Link>
                  <div className="mt-1 flex items-center gap-3 text-sm text-gray-500">
                    <span>{enrollCounts[c.id] ?? 0} студентов</span>
                    {c.avg_rating != null && (
                      <span className="text-yellow-500">★ {c.avg_rating}</span>
                    )}
                    <span>{c.is_free ? "Бесплатно" : `$${c.price}`}</span>
                  </div>
                </div>
                <Link
                  href={`/courses/${c.id}/edit`}
                  className="rounded border border-gray-200 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50"
                >
                  Редактировать
                </Link>
              </div>
            ))}
          </div>
        )}
      </main>
    </>
  );
}
