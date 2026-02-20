"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import { courses, enrollments, payments, notifications, type Course } from "@/lib/api";
import { Header } from "@/components/Header";
import { useAuth } from "@/hooks/use-auth";

const LEVEL_LABELS: Record<string, string> = {
  beginner: "Начальный",
  intermediate: "Средний",
  advanced: "Продвинутый",
};

export default function CoursePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { user, token } = useAuth();
  const [course, setCourse] = useState<Course | null>(null);
  const [error, setError] = useState("");
  const [enrolled, setEnrolled] = useState(false);
  const [enrollCount, setEnrollCount] = useState(0);
  const [enrolling, setEnrolling] = useState(false);

  useEffect(() => {
    courses.get(id).then(setCourse).catch((e) => setError(e.message));
    enrollments.courseCount(id).then((r) => setEnrollCount(r.count)).catch(() => {});
  }, [id]);

  useEffect(() => {
    if (!token) return;
    enrollments.me(token, { limit: 100 }).then((r) => {
      if (r.items.some((e) => e.course_id === id)) setEnrolled(true);
    }).catch(() => {});
  }, [token, id]);

  async function handleEnroll() {
    if (!token || !course) return;
    setEnrolling(true);
    try {
      let paymentId: string | undefined;
      if (!course.is_free && course.price) {
        const payment = await payments.create(token, {
          course_id: course.id,
          amount: course.price,
        });
        paymentId = payment.id;
      }
      await enrollments.create(token, {
        course_id: course.id,
        payment_id: paymentId,
      });
      await notifications.create(token, {
        type: "enrollment",
        title: `Вы записались на курс: ${course.title}`,
        body: course.is_free ? "Бесплатная запись" : `Оплата: $${course.price}`,
      });
      setEnrolled(true);
      setEnrollCount((c) => c + 1);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка записи");
    } finally {
      setEnrolling(false);
    }
  }

  return (
    <>
      <Header />
      <main className="mx-auto max-w-3xl px-4 py-6">
        <Link href="/" className="mb-4 inline-block text-sm text-blue-600 hover:underline">
          &larr; Назад к курсам
        </Link>

        {error ? (
          <div className="rounded bg-red-50 p-4 text-red-600">{error}</div>
        ) : !course ? (
          <p className="text-gray-400">Загрузка...</p>
        ) : (
          <div className="rounded-lg border border-gray-200 bg-white p-6">
            <h1 className="mb-2 text-2xl font-bold">{course.title}</h1>
            <div className="mb-4 flex items-center gap-3">
              <span className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                {LEVEL_LABELS[course.level] || course.level}
              </span>
              {course.is_free ? (
                <span className="rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-700">
                  Бесплатно
                </span>
              ) : (
                <span className="text-lg font-bold">${course.price}</span>
              )}
              {course.duration_minutes > 0 && (
                <span className="text-sm text-gray-400">
                  {course.duration_minutes} мин.
                </span>
              )}
              <span className="text-sm text-gray-400">
                {enrollCount} записавшихся
              </span>
            </div>
            <p className="mb-4 text-gray-600">{course.description}</p>

            <div className="mb-4">
              {!user ? (
                <Link
                  href="/login"
                  className="inline-block rounded bg-gray-200 px-4 py-2 text-sm text-gray-700 hover:bg-gray-300"
                >
                  Войдите для записи
                </Link>
              ) : enrolled ? (
                <span className="inline-block rounded bg-green-100 px-4 py-2 text-sm text-green-700">
                  Вы записаны
                </span>
              ) : user.role === "student" ? (
                <button
                  onClick={handleEnroll}
                  disabled={enrolling}
                  className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {enrolling
                    ? "Записываемся..."
                    : course.is_free
                      ? "Записаться бесплатно"
                      : `Купить за $${course.price}`}
                </button>
              ) : null}
            </div>

            <p className="text-xs text-gray-400">
              Добавлен: {new Date(course.created_at).toLocaleDateString("ru")}
            </p>
          </div>
        )}
      </main>
    </>
  );
}
