"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import {
  courses,
  enrollments,
  payments,
  notifications,
  reviews as reviewsApi,
  progress as progressApi,
  type Course,
  type CurriculumModule,
  type Review,
  type CourseProgress,
} from "@/lib/api";
import { Header } from "@/components/Header";
import { useAuth } from "@/hooks/use-auth";

const LEVEL_LABELS: Record<string, string> = {
  beginner: "Начальный",
  intermediate: "Средний",
  advanced: "Продвинутый",
};

function Stars({ rating }: { rating: number }) {
  return (
    <span className="text-yellow-500">
      {"★".repeat(Math.round(rating))}
      {"☆".repeat(5 - Math.round(rating))}
    </span>
  );
}

export default function CoursePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { user, token } = useAuth();
  const [course, setCourse] = useState<Course | null>(null);
  const [curriculum, setCurriculum] = useState<CurriculumModule[]>([]);
  const [totalLessons, setTotalLessons] = useState(0);
  const [courseReviews, setCourseReviews] = useState<Review[]>([]);
  const [reviewTotal, setReviewTotal] = useState(0);
  const [courseProgress, setCourseProgress] = useState<CourseProgress | null>(null);
  const [completedLessonIds, setCompletedLessonIds] = useState<Set<string>>(new Set());
  const [error, setError] = useState("");
  const [enrolled, setEnrolled] = useState(false);
  const [enrollCount, setEnrollCount] = useState(0);
  const [enrolling, setEnrolling] = useState(false);
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewComment, setReviewComment] = useState("");
  const [reviewSubmitting, setReviewSubmitting] = useState(false);
  const [reviewError, setReviewError] = useState("");

  useEffect(() => {
    courses.get(id).then(setCourse).catch((e) => setError(e.message));
    courses.curriculum(id).then((r) => {
      setCurriculum(r.modules);
      setTotalLessons(r.total_lessons);
    }).catch(() => {});
    enrollments.courseCount(id).then((r) => setEnrollCount(r.count)).catch(() => {});
    reviewsApi.byCourse(id).then((r) => {
      setCourseReviews(r.items);
      setReviewTotal(r.total);
    }).catch(() => {});
  }, [id]);

  useEffect(() => {
    if (!token) return;
    enrollments.me(token, { limit: 100 }).then((r) => {
      if (r.items.some((e) => e.course_id === id)) setEnrolled(true);
    }).catch(() => {});
  }, [token, id]);

  useEffect(() => {
    if (!token || !enrolled || totalLessons === 0) return;
    progressApi.course(token, id, totalLessons).then(setCourseProgress).catch(() => {});
    progressApi.completedLessons(token, id).then((r) => {
      setCompletedLessonIds(new Set(r.completed_lesson_ids));
    }).catch(() => {});
  }, [token, enrolled, id, totalLessons]);

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

  async function handleReviewSubmit() {
    if (!token) return;
    setReviewSubmitting(true);
    setReviewError("");
    try {
      const r = await reviewsApi.create(token, {
        course_id: id,
        rating: reviewRating,
        comment: reviewComment,
      });
      setCourseReviews((prev) => [r, ...prev]);
      setReviewTotal((t) => t + 1);
      setReviewComment("");
    } catch (e) {
      setReviewError(e instanceof Error ? e.message : "Ошибка");
    } finally {
      setReviewSubmitting(false);
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
          <>
            <div className="rounded-lg border border-gray-200 bg-white p-6">
              <h1 className="mb-2 text-2xl font-bold">{course.title}</h1>
              <div className="mb-4 flex flex-wrap items-center gap-3">
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
                {course.avg_rating != null && (
                  <span className="flex items-center gap-1 text-sm">
                    <Stars rating={course.avg_rating} />
                    <span className="text-gray-500">
                      {course.avg_rating} ({course.review_count})
                    </span>
                  </span>
                )}
              </div>
              <p className="mb-4 text-gray-600">{course.description}</p>

              {enrolled && courseProgress && (
                <div className="mb-4">
                  <div className="mb-1 flex justify-between text-sm text-gray-500">
                    <span>Прогресс</span>
                    <span>{courseProgress.completed_lessons}/{courseProgress.total_lessons} уроков ({courseProgress.percentage}%)</span>
                  </div>
                  <div className="h-2 w-full rounded-full bg-gray-200">
                    <div
                      className="h-2 rounded-full bg-green-500 transition-all"
                      style={{ width: `${courseProgress.percentage}%` }}
                    />
                  </div>
                </div>
              )}

              <div className="mb-4 flex flex-wrap items-center gap-3">
                {!user ? (
                  <Link
                    href="/login"
                    className="inline-block rounded bg-gray-200 px-4 py-2 text-sm text-gray-700 hover:bg-gray-300"
                  >
                    Войдите для записи
                  </Link>
                ) : enrolled ? (
                  <>
                    <span className="inline-block rounded bg-green-100 px-4 py-2 text-sm text-green-700">
                      Вы записаны
                    </span>
                    {curriculum.length > 0 && curriculum[0].lessons.length > 0 && (
                      <Link
                        href={`/courses/${id}/lessons/${curriculum[0].lessons[0].id}`}
                        className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
                      >
                        Начать обучение
                      </Link>
                    )}
                  </>
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

              {user && user.id === course.teacher_id && (
                <div className="mb-4">
                  <Link
                    href={`/courses/${id}/edit`}
                    className="rounded border border-gray-200 px-4 py-2 text-sm text-gray-600 hover:bg-gray-50"
                  >
                    Редактировать курс
                  </Link>
                </div>
              )}

              <p className="text-xs text-gray-400">
                Добавлен: {new Date(course.created_at).toLocaleDateString("ru")}
              </p>
            </div>

            {/* Curriculum */}
            {curriculum.length > 0 && (
              <div className="mt-6 rounded-lg border border-gray-200 bg-white p-6">
                <h2 className="mb-4 text-lg font-bold">
                  Программа курса ({totalLessons} уроков)
                </h2>
                {curriculum.map((mod) => (
                  <div key={mod.id} className="mb-4">
                    <h3 className="mb-2 font-semibold text-gray-800">{mod.title}</h3>
                    <ul className="space-y-1">
                      {mod.lessons.map((lesson) => (
                        <li key={lesson.id} className="flex items-center gap-2 text-sm">
                          {completedLessonIds.has(lesson.id) ? (
                            <span className="text-green-500">&#10003;</span>
                          ) : (
                            <span className="text-gray-300">&#9675;</span>
                          )}
                          {enrolled ? (
                            <Link
                              href={`/courses/${id}/lessons/${lesson.id}`}
                              className="text-blue-600 hover:underline"
                            >
                              {lesson.title}
                            </Link>
                          ) : (
                            <span className="text-gray-600">{lesson.title}</span>
                          )}
                          {lesson.duration_minutes > 0 && (
                            <span className="text-xs text-gray-400">
                              {lesson.duration_minutes} мин.
                            </span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            )}

            {/* Reviews */}
            <div className="mt-6 rounded-lg border border-gray-200 bg-white p-6">
              <h2 className="mb-4 text-lg font-bold">
                Отзывы ({reviewTotal})
              </h2>

              {enrolled && user?.role === "student" && (
                <div className="mb-4 border-b border-gray-100 pb-4">
                  <div className="mb-2 flex items-center gap-2">
                    <span className="text-sm text-gray-500">Оценка:</span>
                    {[1, 2, 3, 4, 5].map((n) => (
                      <button
                        key={n}
                        onClick={() => setReviewRating(n)}
                        className={`text-lg ${n <= reviewRating ? "text-yellow-500" : "text-gray-300"}`}
                      >
                        ★
                      </button>
                    ))}
                  </div>
                  <textarea
                    value={reviewComment}
                    onChange={(e) => setReviewComment(e.target.value)}
                    placeholder="Ваш комментарий..."
                    className="mb-2 w-full rounded border border-gray-200 p-2 text-sm"
                    rows={2}
                  />
                  {reviewError && (
                    <p className="mb-2 text-sm text-red-500">{reviewError}</p>
                  )}
                  <button
                    onClick={handleReviewSubmit}
                    disabled={reviewSubmitting}
                    className="rounded bg-blue-600 px-3 py-1 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
                  >
                    {reviewSubmitting ? "Отправка..." : "Оставить отзыв"}
                  </button>
                </div>
              )}

              {courseReviews.length === 0 ? (
                <p className="text-sm text-gray-400">Пока нет отзывов</p>
              ) : (
                <ul className="space-y-3">
                  {courseReviews.map((r) => (
                    <li key={r.id} className="border-b border-gray-50 pb-3 last:border-0">
                      <div className="flex items-center gap-2">
                        <Stars rating={r.rating} />
                        <span className="text-xs text-gray-400">
                          {new Date(r.created_at).toLocaleDateString("ru")}
                        </span>
                      </div>
                      {r.comment && (
                        <p className="mt-1 text-sm text-gray-600">{r.comment}</p>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </>
        )}
      </main>
    </>
  );
}
