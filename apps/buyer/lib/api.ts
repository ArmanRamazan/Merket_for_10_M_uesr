const IDENTITY_URL = "/api/identity";
const COURSE_URL = "/api/course";
const ENROLLMENT_URL = "/api/enrollment";
const PAYMENT_URL = "/api/payment";
const NOTIFICATION_URL = "/api/notification";

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: "student" | "teacher";
  is_verified: boolean;
  created_at: string;
}

export interface Course {
  id: string;
  teacher_id: string;
  title: string;
  description: string;
  is_free: boolean;
  price: number | null;
  duration_minutes: number;
  level: "beginner" | "intermediate" | "advanced";
  created_at: string;
}

export interface CourseList {
  items: Course[];
  total: number;
}

export interface Enrollment {
  id: string;
  student_id: string;
  course_id: string;
  payment_id: string | null;
  status: "enrolled" | "in_progress" | "completed";
  enrolled_at: string;
}

export interface EnrollmentList {
  items: Enrollment[];
  total: number;
}

export interface Payment {
  id: string;
  student_id: string;
  course_id: string;
  amount: string;
  status: "pending" | "completed" | "failed" | "refunded";
  created_at: string;
}

export interface PaymentList {
  items: Payment[];
  total: number;
}

export interface Notification {
  id: string;
  user_id: string;
  type: "registration" | "enrollment" | "payment";
  title: string;
  body: string;
  is_read: boolean;
  created_at: string;
}

export interface NotificationList {
  items: Notification[];
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
  register(email: string, password: string, name: string, role: string = "student") {
    return request<TokenResponse>(`${IDENTITY_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, name, role }),
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

export const courses = {
  list(params?: { q?: string; limit?: number; offset?: number }) {
    const sp = new URLSearchParams();
    if (params?.q) sp.set("q", params.q);
    if (params?.limit) sp.set("limit", String(params.limit));
    if (params?.offset) sp.set("offset", String(params.offset));
    const qs = sp.toString();
    return request<CourseList>(`${COURSE_URL}/courses${qs ? `?${qs}` : ""}`);
  },
  get(id: string) {
    return request<Course>(`${COURSE_URL}/courses/${id}`);
  },
  create(token: string, data: {
    title: string;
    description: string;
    is_free: boolean;
    price?: number;
    duration_minutes: number;
    level: string;
  }) {
    return request<Course>(`${COURSE_URL}/courses`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(data),
    });
  },
};

export const enrollments = {
  create(token: string, data: { course_id: string; payment_id?: string }) {
    return request<Enrollment>(`${ENROLLMENT_URL}/enrollments`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(data),
    });
  },
  me(token: string, params?: { limit?: number; offset?: number }) {
    const sp = new URLSearchParams();
    if (params?.limit) sp.set("limit", String(params.limit));
    if (params?.offset) sp.set("offset", String(params.offset));
    const qs = sp.toString();
    return request<EnrollmentList>(`${ENROLLMENT_URL}/enrollments/me${qs ? `?${qs}` : ""}`, {
      headers: authHeaders(token),
    });
  },
  courseCount(courseId: string) {
    return request<{ course_id: string; count: number }>(
      `${ENROLLMENT_URL}/enrollments/course/${courseId}/count`,
    );
  },
};

export const payments = {
  create(token: string, data: { course_id: string; amount: number }) {
    return request<Payment>(`${PAYMENT_URL}/payments`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(data),
    });
  },
  get(token: string, id: string) {
    return request<Payment>(`${PAYMENT_URL}/payments/${id}`, {
      headers: authHeaders(token),
    });
  },
  me(token: string, params?: { limit?: number; offset?: number }) {
    const sp = new URLSearchParams();
    if (params?.limit) sp.set("limit", String(params.limit));
    if (params?.offset) sp.set("offset", String(params.offset));
    const qs = sp.toString();
    return request<PaymentList>(`${PAYMENT_URL}/payments/me${qs ? `?${qs}` : ""}`, {
      headers: authHeaders(token),
    });
  },
};

export const notifications = {
  create(token: string, data: { type: string; title: string; body?: string }) {
    return request<Notification>(`${NOTIFICATION_URL}/notifications`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(data),
    });
  },
  me(token: string, params?: { limit?: number; offset?: number }) {
    const sp = new URLSearchParams();
    if (params?.limit) sp.set("limit", String(params.limit));
    if (params?.offset) sp.set("offset", String(params.offset));
    const qs = sp.toString();
    return request<NotificationList>(`${NOTIFICATION_URL}/notifications/me${qs ? `?${qs}` : ""}`, {
      headers: authHeaders(token),
    });
  },
  markRead(token: string, id: string) {
    return request<Notification>(`${NOTIFICATION_URL}/notifications/${id}/read`, {
      method: "PATCH",
      headers: authHeaders(token),
    });
  },
};
