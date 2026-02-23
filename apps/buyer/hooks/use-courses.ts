import { useQuery } from "@tanstack/react-query";
import { courses, categories as categoriesApi } from "@/lib/api";

export function useCourseList(params?: {
  q?: string;
  limit?: number;
  offset?: number;
  category_id?: string;
  level?: string;
  is_free?: boolean;
  sort_by?: string;
}) {
  return useQuery({
    queryKey: ["courses", params],
    queryFn: () => courses.list(params),
  });
}

export function useCourse(id: string) {
  return useQuery({
    queryKey: ["courses", id],
    queryFn: () => courses.get(id),
  });
}

export function useCurriculum(id: string) {
  return useQuery({
    queryKey: ["curriculum", id],
    queryFn: () => courses.curriculum(id),
  });
}

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: () => categoriesApi.list(),
  });
}
