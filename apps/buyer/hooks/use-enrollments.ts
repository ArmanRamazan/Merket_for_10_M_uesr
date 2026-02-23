import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { enrollments } from "@/lib/api";

export function useMyEnrollments(token: string | null, params?: { limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ["enrollments", "me", params],
    queryFn: () => enrollments.me(token!, params),
    enabled: !!token,
  });
}

export function useEnrollmentCount(courseId: string) {
  return useQuery({
    queryKey: ["enrollments", "count", courseId],
    queryFn: () => enrollments.courseCount(courseId),
  });
}

export function useEnroll(token: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { course_id: string; payment_id?: string; total_lessons?: number }) =>
      enrollments.create(token!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["enrollments"] });
    },
  });
}
