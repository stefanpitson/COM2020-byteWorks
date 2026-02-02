import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import type { Customer } from "../../types";
import { getCustomerProfile } from "../../api/customers";

export default function CustomerHome() {
  const navigate = useNavigate();

  const [profile, setProfile] = useState<Customer | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchCustomerProfile = async () => {
      try {
        const data = await getCustomerProfile();
        setProfile(data);
      } catch (error) {
        console.error("Failed to load profile", error);
      } finally {
        setLoading(false);
      }
    };

    fetchCustomerProfile();
  }, []);

  function handleLogout() {
    localStorage.clear();
    navigate("/login");
  }

  if (loading) return <div>Loading...</div>;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="w-full max-w-md bg-white p-10 rounded-xl shadow-lg text-center mx-4">
        <h1 className="text-3xl font-bold mb-4">Welcome</h1>
        <p className="text-black mb-2">Hello {profile?.name}</p>
        <p className="text-gray-700 mb-8">
          You are signed in. This is the home page.
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


