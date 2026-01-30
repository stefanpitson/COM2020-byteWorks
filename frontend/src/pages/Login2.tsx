import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Customer, Vendor } from "../types";
import { mockToken, mockCustomer, mockVendor } from "../mocks";

export default function Login2() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<"Customer" | "Vendor">("Customer");

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    // Replace with real auth call. For now, accept any non-empty credentials.
    if (username.trim() && password.trim()) {
      if (isUser) {
        // API call to User

        const token: string = mockToken;
        const customer: Customer = mockCustomer;

        localStorage.setItem("customer", JSON.stringify(customer));
        localStorage.setItem("role", "customer");

        localStorage.setItem("token", token);
        localStorage.setItem("loggedIn", "true");

        navigate("/home");
      } else {
        // API call to vendor

        const token: string = mockToken;
        const vendor: Vendor = mockVendor;

        localStorage.setItem("vendor", JSON.stringify(vendor));
        localStorage.setItem("role", "vendor");

        localStorage.setItem("token", token);
        localStorage.setItem("loggedIn", "true");

        navigate("/vendor/dashboard");
      }
    }
  }

  const isUser = activeTab === "Customer";
  const signupPath = isUser ? "/Customer/SignUp" : "/Vendor/SignUp";

  return (
    <div className="h-screen w-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-md bg-white rounded-xl shadow-2xl overflow-hidden">
        {/* TAB HEADER */}
        <div className="flex border-b">
          <button
            onClick={() => setActiveTab("Customer")}
            className={`flex-1 py-4 font-semibold transition-colors ${
              isUser
                ? "bg-white text-primary border-b-2 border-primary"
                : "bg-grayed text-gray-400"
            }`}
          >
            Customers
          </button>
          <button
            onClick={() => setActiveTab("Vendor")}
            className={`flex-1 py-4 font-semibold transition-colors ${
              !isUser
                ? "bg-white text-primary border-b-2 border-primary"
                : "bg-gray-50 text-gray-400"
            }`}
          >
            Businesses
          </button>
        </div>

        {/* FORM CONTENT */}
        <div className="p-8">
          <h2 className="text-2xl font-bold text-center mb-6">
            {isUser ? "User Login" : "Business Portal"}
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder={isUser ? "Username" : "Business ID"}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-primary outline-none"
            />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-primary outline-none"
            />

            <button
              type="submit"
              className="w-full bg-primary text-white py-3 rounded-lg font-bold hover:bg-primaryHover transition-colors"
            >
              Sign In
            </button>
          </form>

          {/* DYNAMIC FOOTER */}
          <div className="mt-6 text-center">
            <p className="text-gray-500 text-sm">
              Don't have an account?{" "}
              <button
                onClick={() => navigate(signupPath)}
                className="text-primary font-bold hover:underline hover:text-primaryHover "
              >
                Create {activeTab} account
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
