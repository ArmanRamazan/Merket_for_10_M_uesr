import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { progress as progressApi } from "@/lib/api";

export function useCourseProgress(token: string | null, courseId: string, totalLessons: number) {
  return useQuery({
    queryKey: ["progress", courseId],
    queryFn: () => progressApi.course(token!, courseId, totalLessons),
    enabled: !!token && totalLessons > 0,
  });
}

export function useCompletedLessons(token: string | null, courseId: string) {
  return useQuery({
    queryKey: ["completedLessons", courseId],
    queryFn: () => progressApi.completedLessons(token!, courseId),
    enabled: !!token,
  });
}

export function useCompleteLesson(token: string | null, courseId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (lessonId: string) => progressApi.complete(token!, lessonId, courseId),
    onMutate: async (lessonId) => {
      await queryClient.cancelQueries({ queryKey: ["completedLessons", courseId] });
      const previous = queryClient.getQueryData(["completedLessons", courseId]);
      queryClient.setQueryData(
        ["completedLessons", courseId],
        (old: { course_id: string; completed_lesson_ids: string[] } | undefined) =>
          old
            ? { ...old, completed_lesson_ids: [...old.completed_lesson_ids, lessonId] }
            : undefined,
      );
      return { previous };
    },
    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(["completedLessons", courseId], context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["completedLessons", courseId] });
      queryClient.invalidateQueries({ queryKey: ["progress", courseId] });
    },
  });
}
