"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import {
  courses,
  lessons as lessonsApi,
  progress as progressApi,
  type Lesson,
  type CurriculumModule,
} from "@/lib/api";
import { Header } from "@/components/Header";
import { useAuth } from "@/hooks/use-auth";

export default function LessonPage({
  params,
}: {
  params: Promise<{ id: string; lessonId: string }>;
}) {
  const { id: courseId, lessonId } = use(params);
  const { token } = useAuth();
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [curriculum, setCurriculum] = useState<CurriculumModule[]>([]);
  const [completedIds, setCompletedIds] = useState<Set<string>>(new Set());
  const [completing, setCompleting] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [courseTitle, setCourseTitle] = useState("");

  // Flat list of all lesson IDs for prev/next
  const allLessons = curriculum.flatMap((m) => m.lessons);
  const currentIdx = allLessons.findIndex((l) => l.id === lessonId);
  const prevLesson = currentIdx > 0 ? allLessons[currentIdx - 1] : null;
  const nextLesson = currentIdx < allLessons.length - 1 ? allLessons[currentIdx + 1] : null;

  useEffect(() => {
    lessonsApi.get(lessonId).then(setLesson).catch((e) => setError(e.message));
    courses.curriculum(courseId).then((r) => {
      setCurriculum(r.modules);
      setCourseTitle(r.course.title);
    }).catch(() => {});
    setSidebarOpen(false);
  }, [courseId, lessonId]);

  useEffect(() => {
    if (!token) return;
    progressApi.completedLessons(token, courseId).then((r) => {
      const ids = new Set(r.completed_lesson_ids);
      setCompletedIds(ids);
      setCompleted(ids.has(lessonId));
    }).catch(() => {});
  }, [token, courseId, lessonId]);

  async function handleComplete() {
    if (!token) return;
    setCompleting(true);
    try {
      await progressApi.complete(token, lessonId, courseId);
      setCompleted(true);
      setCompletedIds((prev) => new Set([...prev, lessonId]));
    } catch {
      // already completed — ignore
      setCompleted(true);
    } finally {
      setCompleting(false);
    }
  }

  return (
    <>
      <Header />
      <div className="mx-auto max-w-5xl px-4 py-6">
        {/* Breadcrumbs */}
        <nav className="mb-4 text-sm text-gray-500">
          <Link href="/" className="hover:underline">Курсы</Link>
          {" / "}
          <Link href={`/courses/${courseId}`} className="hover:underline">
            {courseTitle || "..."}
          </Link>
          {lesson && (
            <>
              {" / "}
              <span className="text-gray-700">{lesson.title}</span>
            </>
          )}
        </nav>

        {/* Mobile toggle */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="mb-3 rounded border border-gray-200 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50 md:hidden"
        >
          {sidebarOpen ? "Скрыть программу" : "Показать программу"}
        </button>

        <div className="flex gap-6">
        {/* Sidebar */}
        <aside className={`${sidebarOpen ? "block" : "hidden"} w-64 shrink-0 md:block`}>
          <Link href={`/courses/${courseId}`} className="mb-3 block text-sm text-blue-600 hover:underline">
            &larr; К курсу
          </Link>
          <nav className="space-y-3">
            {curriculum.map((mod) => (
              <div key={mod.id}>
                <h4 className="mb-1 text-xs font-semibold uppercase text-gray-400">{mod.title}</h4>
                <ul className="space-y-1">
                  {mod.lessons.map((l) => (
                    <li key={l.id}>
                      <Link
                        href={`/courses/${courseId}/lessons/${l.id}`}
                        className={`flex items-center gap-1.5 rounded px-2 py-1 text-sm ${
                          l.id === lessonId
                            ? "bg-blue-50 font-medium text-blue-700"
                            : "text-gray-600 hover:bg-gray-50"
                        }`}
                      >
                        {completedIds.has(l.id) ? (
                          <span className="text-green-500">&#10003;</span>
                        ) : (
                          <span className="text-gray-300">&#9675;</span>
                        )}
                        <span className="truncate">{l.title}</span>
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </nav>
        </aside>

        {/* Main content */}
        <main className="min-w-0 flex-1">
          {error ? (
            <div className="rounded bg-red-50 p-4 text-red-600">{error}</div>
          ) : !lesson ? (
            <p className="text-gray-400">Загрузка...</p>
          ) : (
            <div className="rounded-lg border border-gray-200 bg-white p-6">
              <h1 className="mb-4 text-xl font-bold">{lesson.title}</h1>

              {lesson.video_url && (
                <div className="mb-4 aspect-video">
                  <iframe
                    src={lesson.video_url}
                    className="h-full w-full rounded"
                    allowFullScreen
                  />
                </div>
              )}

              <div className="prose prose-sm mb-6 max-w-none whitespace-pre-wrap text-gray-700">
                {lesson.content}
              </div>

              <div className="flex items-center gap-3 border-t border-gray-100 pt-4">
                {completed ? (
                  <span className="rounded bg-green-100 px-3 py-1.5 text-sm text-green-700">
                    &#10003; Урок завершён
                  </span>
                ) : token ? (
                  <button
                    onClick={handleComplete}
                    disabled={completing}
                    className="rounded bg-green-600 px-3 py-1.5 text-sm text-white hover:bg-green-700 disabled:opacity-50"
                  >
                    {completing ? "Завершаем..." : "Завершить урок"}
                  </button>
                ) : null}

                <div className="ml-auto flex gap-2">
                  {prevLesson && (
                    <Link
                      href={`/courses/${courseId}/lessons/${prevLesson.id}`}
                      className="rounded border border-gray-200 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50"
                    >
                      &larr; Назад
                    </Link>
                  )}
                  {nextLesson ? (
                    <Link
                      href={`/courses/${courseId}/lessons/${nextLesson.id}`}
                      className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700"
                    >
                      Далее &rarr;
                    </Link>
                  ) : completed ? (
                    <Link
                      href={`/courses/${courseId}`}
                      className="rounded bg-green-600 px-3 py-1.5 text-sm text-white hover:bg-green-700"
                    >
                      Курс завершён
                    </Link>
                  ) : null}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
      </div>
    </>
  );
}
