"use client";

import { useState, useEffect, useCallback } from "react";
import { identity, type User } from "@/lib/api";

interface AuthState {
  token: string | null;
  user: User | null;
  loading: boolean;
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    token: null,
    user: null,
    loading: true,
  });

  useEffect(() => {
    const saved = localStorage.getItem("token");
    if (!saved) {
      setState({ token: null, user: null, loading: false });
      return;
    }
    identity
      .me(saved)
      .then((user) => setState({ token: saved, user, loading: false }))
      .catch(() => {
        localStorage.removeItem("token");
        setState({ token: null, user: null, loading: false });
      });
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await identity.login(email, password);
    localStorage.setItem("token", res.access_token);
    const user = await identity.me(res.access_token);
    setState({ token: res.access_token, user, loading: false });
  }, []);

  const register = useCallback(async (email: string, password: string, name: string, role: string = "student") => {
    const res = await identity.register(email, password, name, role);
    localStorage.setItem("token", res.access_token);
    const user = await identity.me(res.access_token);
    setState({ token: res.access_token, user, loading: false });
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setState({ token: null, user: null, loading: false });
  }, []);

  return { ...state, login, register, logout };
}
