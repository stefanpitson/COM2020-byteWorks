import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { User } from "../types";

import { loginUser } from "../api/auth";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    // Replace with real auth call. For now, accept any non-empty credentials.
    const trimEmail = email.trim();
    const trimPassword = password.trim();

    if (trimEmail && trimPassword) {
      const response = await loginUser({
        email: trimEmail,
        password: trimPassword,
      });

      const token: string = response.access_token;
      const token_type: string = response.token_type;
      const user: User = response.user;

      // const token: Token = mockToken;
      // const tokenType: string = "bearer"
      // const user: User = mockUserCus;

      localStorage.setItem("token", token);
      localStorage.setItem("tokenType", token_type);
      localStorage.setItem("user", JSON.stringify(user));
      localStorage.setItem("role", user.role);

      if (user.role === "customer") {
        navigate("/customer/home");
      } else if (user.role === "vendor") {
        navigate("vendor/dashboard");
      }
    }
  }

  return (
    <div className="h-screen w-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-md bg-white p-8 rounded-xl shadow-lg">
        <form onSubmit={handleSubmit} className="space-y-4">
          <h2 className="text-2xl font-semibold mb-6">Sign in</h2>
          <label className="block mb-4">
            <span className="text-sm text-gray-700">Email</span>
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 p-2"
              placeholder="you@example.com"
            />
          </label>

          <label className="block mb-6">
            <span className="text-sm text-gray-700">Password</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full rounded border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 p-2"
              placeholder="••••••••"
            />
          </label>

          <button
            type="submit"
            className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-800"
          >
            Sign in
          </button>
        </form>
        <div className="mt-6 text-center">
          <p className="text-gray-500 text-sm">
            Don't have an account?{" "}
            <button
              onClick={() => navigate("/customer/signup")}
              className="text-primary font-bold hover:underline hover:text-primaryHover "
            >
              Create new account
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
