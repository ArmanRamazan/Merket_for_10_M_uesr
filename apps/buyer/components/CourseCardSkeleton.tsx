export function CourseCardSkeleton() {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="mb-3 h-5 w-3/4 animate-pulse rounded bg-gray-200" />
      <div className="mb-2 h-4 w-full animate-pulse rounded bg-gray-100" />
      <div className="mb-3 h-4 w-2/3 animate-pulse rounded bg-gray-100" />
      <div className="flex gap-2">
        <div className="h-5 w-16 animate-pulse rounded bg-gray-200" />
        <div className="h-5 w-20 animate-pulse rounded bg-gray-200" />
      </div>
    </div>
  );
}
