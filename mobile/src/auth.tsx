import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { ApiError, api, login as apiLogin, logout as apiLogout, storedToken, User } from './api';

type AuthValue = { user: User | null; loading: boolean; mustChangePassword: boolean; signIn: (email: string, password: string) => Promise<boolean>; signOut: () => Promise<void>; refreshUser: () => Promise<User | null> };
const AuthContext = createContext<AuthValue | null>(null);
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const refreshUser = async () => {
    try { const current = await api.me(); setUser(current); return current; }
    catch (error) { if (error instanceof ApiError && error.status === 401) setUser(null); return null; }
  };
  useEffect(() => { storedToken().then(token => token ? refreshUser() : null).finally(() => setLoading(false)); }, []);
  const value = useMemo<AuthValue>(() => ({ user, loading, mustChangePassword: Boolean(user?.must_change_password), signIn: async (email, password) => { const token = await apiLogin(email.trim(), password); const current = await api.me(); setUser({ ...current, must_change_password: token.must_change_password }); return token.must_change_password; }, signOut: async () => { await apiLogout(); setUser(null); }, refreshUser }), [user, loading]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
export function useAuth() { const value = useContext(AuthContext); if (!value) throw new Error('useAuth must be used inside AuthProvider'); return value; }
