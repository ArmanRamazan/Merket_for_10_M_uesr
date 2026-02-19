const IDENTITY_URL = "/api/identity";
const CATALOG_URL = "/api/catalog";

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface Product {
  id: string;
  seller_id: string;
  title: string;
  description: string;
  price: number;
  stock: number;
  created_at: string;
}

export interface ProductList {
  items: Product[];
  total: number;
}

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
}

export const identity = {
  register(email: string, password: string, name: string) {
    return request<TokenResponse>(`${IDENTITY_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, name }),
    });
  },
  login(email: string, password: string) {
    return request<TokenResponse>(`${IDENTITY_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
  },
  me(token: string) {
    return request<User>(`${IDENTITY_URL}/me`, {
      headers: authHeaders(token),
    });
  },
};

export const catalog = {
  list(params?: { q?: string; limit?: number; offset?: number }) {
    const sp = new URLSearchParams();
    if (params?.q) sp.set("q", params.q);
    if (params?.limit) sp.set("limit", String(params.limit));
    if (params?.offset) sp.set("offset", String(params.offset));
    const qs = sp.toString();
    return request<ProductList>(`${CATALOG_URL}/products${qs ? `?${qs}` : ""}`);
  },
  get(id: string) {
    return request<Product>(`${CATALOG_URL}/products/${id}`);
  },
  create(token: string, data: { title: string; description: string; price: number; stock: number }) {
    return request<Product>(`${CATALOG_URL}/products`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(data),
    });
  },
};
