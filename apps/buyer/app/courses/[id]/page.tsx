"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import { courses, type Course } from "@/lib/api";
import { Header } from "@/components/Header";

const LEVEL_LABELS: Record<string, string> = {
  beginner: "Начальный",
  intermediate: "Средний",
  advanced: "Продвинутый",
};

export default function CoursePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [course, setCourse] = useState<Course | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    courses
      .get(id)
      .then(setCourse)
      .catch((e) => setError(e.message));
  }, [id]);

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
            </div>
            <p className="mb-4 text-gray-600">{course.description}</p>
            <p className="text-xs text-gray-400">
              Добавлен: {new Date(course.created_at).toLocaleDateString("ru")}
            </p>
          </div>
        )}
      </main>
    </>
  );
}
