import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notifications, type Notification } from "@/lib/api";

export function useMyNotifications(token: string | null, params?: { limit?: number; offset?: number }) {
  return useQuery({
    queryKey: ["notifications", "me", params],
    queryFn: () => notifications.me(token!, params),
    enabled: !!token,
  });
}

export function useMarkRead(token: string | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => notifications.markRead(token!, id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: ["notifications", "me"] });
      const key = ["notifications", "me", { limit: 50 }];
      const previous = queryClient.getQueryData(key);
      queryClient.setQueryData(
        key,
        (old: { items: Notification[]; total: number } | undefined) =>
          old
            ? { ...old, items: old.items.map((n) => (n.id === id ? { ...n, is_read: true } : n)) }
            : undefined,
      );
      return { previous, key };
    },
    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(context.key, context.previous);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}
