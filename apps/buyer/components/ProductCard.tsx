import Link from "next/link";
import type { Product } from "@/lib/api";

interface ProductCardProps {
  product: Product;
}

export function ProductCard({ product }: ProductCardProps) {
  return (
    <Link
      href={`/products/${product.id}`}
      className="block rounded-lg border border-gray-200 bg-white p-4 transition hover:shadow-md"
    >
      <h3 className="mb-1 font-semibold leading-tight">{product.title}</h3>
      <p className="mb-2 line-clamp-2 text-sm text-gray-500">
        {product.description}
      </p>
      <div className="flex items-center justify-between">
        <span className="text-lg font-bold">${product.price}</span>
        <span className="text-xs text-gray-400">
          В наличии: {product.stock}
        </span>
      </div>
    </Link>
  );
}
