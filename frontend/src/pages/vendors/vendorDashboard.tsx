import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Vendor } from "../../types";

export default function VendorDashboard() {
  const navigate = useNavigate();

  const vendorString = localStorage.getItem("vendor");
  const vendor = vendorString ? (JSON.parse(vendorString) as Vendor) : null;

  const [name] = useState(vendor?.name);

  function handleLogout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    localStorage.removeItem("loggedIn");
    localStorage.clear();
    navigate("/login");
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="w-full max-w-md bg-white p-10 rounded-xl shadow-lg text-center mx-4">
        <h1 className="text-3xl font-bold mb-4">Vendor Dashboard</h1>
        <p className="text-black mb-2">Hello {name}</p>
        <p className="text-gray-700 mb-8">
          You are signed in. This is the dashbaord.
        </p>
        <button
          onClick={handleLogout}
          className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
        >
          Log out
        </button>
      </div>
    </div>
  );
}
