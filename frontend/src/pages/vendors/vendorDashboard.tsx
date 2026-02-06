import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import type { Vendor } from "../../types";
import { getVendorProfile } from "../../api/vendors";
import { API_BASE_URL } from "../../api/axiosConfig";

export default function VendorDashboard() {
  const navigate = useNavigate();

  const vendorString = localStorage.getItem("vendor");
  const vendor = vendorString ? (JSON.parse(vendorString) as Vendor) : null;

  const [name] = useState(vendor?.name);

  const [profile, setProfile] = useState<Vendor | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchVendorProfile = async () => {
      try {
        const data = await getVendorProfile();
        setProfile(data);
      } catch (error) {
        console.error("Failed to load profile", error);
      } finally {
        setLoading(false);
      }
    };

    fetchVendorProfile();
  }, []);

  function handleLogout() {
    localStorage.clear();
    navigate("/login");
  }
  

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="w-full max-w-md bg-white p-10 rounded-xl shadow-lg text-center mx-4">
        <h1 className="text-3xl font-bold mb-4">Vendor Dashboard</h1>
        <p className="text-black mb-2">Hello {name}</p>
        <p className="text-gray-700 mb-8">
          You are signed in. This is the dashboard.
        </p>
        <div className="w-52 h-32 rounded-3xl overflow-hidden border-2 border-gray-300 relative">
          {profile?.photo ? (
            <img src={`${API_BASE_URL}/${profile.photo}`} alt="imagePreview" className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full bg-gray-100 flex items-center justify-center text-gray-400">
              No Image
            </div>
          )}
        </div>
        
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


