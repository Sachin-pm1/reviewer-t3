"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, ApiResponseError, getToken, setToken } from "./api";
import type { User } from "./types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    if (!getToken()) {
      setLoading(false);
      return;
    }
    api.auth
      .me()
      .then((u) => {
        if (!cancelled) setUser(u);
      })
      .catch(() => {
        // Token expired/invalid — quietly drop it rather than looping forever.
        setToken(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    const res = await api.auth.signin(email, password);
    setToken(res.access_token);
    setUser(res.user);
  }, []);

  const signUp = useCallback(async (email: string, password: string) => {
    const res = await api.auth.signup(email, password);
    setToken(res.access_token);
    setUser(res.user);
  }, []);

  const signOut = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signUp, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export function authErrorMessage(err: unknown): string {
  if (err instanceof ApiResponseError) {
    if (err.status === 409) return "An account with this email already exists.";
    if (err.status === 401) return "Invalid email or password.";
    if (err.status === 422) return "Check your email and password (8+ characters).";
    return err.message;
  }
  return "Something went wrong. Try again.";
}
