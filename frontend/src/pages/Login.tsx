import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { User } from "../types";
import EyeIcon from "../assets/icons/eye.svg?react";
import EyeOffIcon from "../assets/icons/eye-off.svg?react";

import { loginUser } from "../api/auth";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [shakeKey, setShakeKey] = useState(0);
  const [showPassword, setShowPassword] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    
    const trimEmail = email.trim().toLowerCase();
    const trimPassword = password.trim();

    if (trimEmail && trimPassword) {
      setIsLoading(true);
      try {
        const response = await loginUser({
          email: trimEmail,
          password: trimPassword,
        });

        const token: string = response.access_token;
        const token_type: string = response.token_type;
        const user: User = response.user;

        localStorage.setItem("token", token);
        localStorage.setItem("tokenType", token_type);
        localStorage.setItem("user", JSON.stringify(user));
        localStorage.setItem("role", user.role);

        if (user.role === "customer") {
          navigate("/customer/home");
        } else if (user.role === "vendor") {
          navigate("/vendor/dashboard");
        }
      } catch (error) {
        console.error("Login failed:", error);
        setLoginError(true);
        setShakeKey(prev => prev + 1);
      } finally {
        setIsLoading(false);
      }
    }
  }

    const getInputClass = () => { return `
      mt-1 block w-full rounded shadow-sm p-2
      border border-transparent
      ring-0 focus:ring-2 focus:ring-primary focus:outline-none
    `;
  };

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
              className={getInputClass()}
              placeholder="name@domain.com"
            />
          </label>

          <label className="block mb-6">
            <span className="text-sm text-gray-700">Password</span>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={getInputClass()}
                placeholder="••••••••"
              />
              <button
                type="button"
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => setShowPassword(prev => !prev)}
                className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-500 hover:text-gray-700"
              >
                {showPassword ? <EyeOffIcon/> : <EyeIcon/>}
              </button>
            </div>
          </label>

          {loginError && (
            <div 
              key={shakeKey}
              className="p-3 rounded bg-red-50 border border-red-200 animate-shake">
              <span className="text-red-700 text-sm font-medium">
                Invalid email or password. Please try again.
              </span>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-primary text-white py-2 rounded hover:bg-primaryHover"
          >
            {isLoading ? "Signing in..." : "Sign in"}
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
