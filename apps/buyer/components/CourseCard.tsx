import Link from "next/link";
import type { Course } from "@/lib/api";

interface CourseCardProps {
  course: Course;
}

const LEVEL_LABELS: Record<string, string> = {
  beginner: "Начальный",
  intermediate: "Средний",
  advanced: "Продвинутый",
};

const LEVEL_COLORS: Record<string, string> = {
  beginner: "bg-green-100 text-green-700",
  intermediate: "bg-yellow-100 text-yellow-700",
  advanced: "bg-red-100 text-red-700",
};

export function CourseCard({ course }: CourseCardProps) {
  return (
    <Link
      href={`/courses/${course.id}`}
      className="block rounded-lg border border-gray-200 bg-white p-4 transition hover:shadow-md"
    >
      <div className="mb-2 flex items-center gap-2">
        <span className={`rounded px-2 py-0.5 text-xs ${LEVEL_COLORS[course.level] || ""}`}>
          {LEVEL_LABELS[course.level] || course.level}
        </span>
        {course.is_free ? (
          <span className="rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-700">
            Бесплатно
          </span>
        ) : (
          <span className="text-xs font-medium text-gray-600">
            ${course.price}
          </span>
        )}
      </div>
      <h3 className="mb-1 font-semibold leading-tight">{course.title}</h3>
      <p className="mb-2 line-clamp-2 text-sm text-gray-500">
        {course.description}
      </p>
      {course.duration_minutes > 0 && (
        <span className="text-xs text-gray-400">
          {course.duration_minutes} мин.
        </span>
      )}
    </Link>
  );
}
