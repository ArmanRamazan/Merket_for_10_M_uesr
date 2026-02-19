"use client";

import { useState, useEffect } from "react";
import { courses, type Course } from "@/lib/api";
import { Header } from "@/components/Header";
import { CourseCard } from "@/components/CourseCard";

export default function HomePage() {
  const [items, setItems] = useState<Course[]>([]);
  const [total, setTotal] = useState(0);
  const [query, setQuery] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");
    courses
      .list({ q: search || undefined, limit: 20 })
      .then((res) => {
        setItems(res.items);
        setTotal(res.total);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [search]);

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    setSearch(query);
  }

  return (
    <>
      <Header />
      <main className="mx-auto max-w-6xl px-4 py-6">
        <form onSubmit={handleSearch} className="mb-6 flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Поиск курсов..."
            className="flex-1 rounded-lg border border-gray-300 px-4 py-2 focus:border-blue-500 focus:outline-none"
          />
          <button
            type="submit"
            className="rounded-lg bg-blue-600 px-6 py-2 text-white hover:bg-blue-700"
          >
            Найти
          </button>
        </form>

        {error && (
          <div className="mb-4 rounded bg-red-50 p-3 text-sm text-red-600">
            {error}
          </div>
        )}

        {loading ? (
          <p className="text-center text-gray-400">Загрузка...</p>
        ) : items.length === 0 ? (
          <p className="text-center text-gray-400">Курсы не найдены</p>
        ) : (
          <>
            <p className="mb-4 text-sm text-gray-500">
              Найдено: {total}
            </p>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {items.map((c) => (
                <CourseCard key={c.id} course={c} />
              ))}
            </div>
          </>
        )}
      </main>
    </>
  );
}
