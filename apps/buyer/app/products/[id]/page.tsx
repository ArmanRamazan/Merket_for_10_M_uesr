"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import { catalog, type Product } from "@/lib/api";
import { Header } from "@/components/Header";

export default function ProductPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [product, setProduct] = useState<Product | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    catalog
      .get(id)
      .then(setProduct)
      .catch((e) => setError(e.message));
  }, [id]);

  return (
    <>
      <Header />
      <main className="mx-auto max-w-3xl px-4 py-6">
        <Link href="/" className="mb-4 inline-block text-sm text-blue-600 hover:underline">
          &larr; Назад к каталогу
        </Link>

        {error ? (
          <div className="rounded bg-red-50 p-4 text-red-600">{error}</div>
        ) : !product ? (
          <p className="text-gray-400">Загрузка...</p>
        ) : (
          <div className="rounded-lg border border-gray-200 bg-white p-6">
            <h1 className="mb-2 text-2xl font-bold">{product.title}</h1>
            <p className="mb-4 text-gray-600">{product.description}</p>
            <div className="flex items-center gap-6">
              <span className="text-3xl font-bold">${product.price}</span>
              <span className="text-sm text-gray-400">
                В наличии: {product.stock} шт.
              </span>
            </div>
            <p className="mt-4 text-xs text-gray-400">
              Добавлен: {new Date(product.created_at).toLocaleDateString("ru")}
            </p>
          </div>
        )}
      </main>
    </>
  );
}
