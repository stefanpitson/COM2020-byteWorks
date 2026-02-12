import type { User } from "../types";

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export function saveAuthSession(response: LoginResponse) {
  const { access_token, token_type, user } = response;

  localStorage.setItem("token", access_token);
  localStorage.setItem("tokenType", token_type);
  localStorage.setItem("user", JSON.stringify(user));
  localStorage.setItem("role", user.role);
}

export function clearAuthSession() {
  localStorage.removeItem("token");
  localStorage.removeItem("tokenType");
  localStorage.removeItem("user");
  localStorage.removeItem("role");
}

export function getRedirectPath(role: string): string {
  if (role === "customer") return "/customer/home";
  if (role === "vendor") return "/vendor/dashboard";
  return "/";
}