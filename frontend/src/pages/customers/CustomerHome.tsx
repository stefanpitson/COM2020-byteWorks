import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import type { Customer, Vendor } from "../../types";
import { getCustomerProfile } from "../../api/customers";
import { getAllVendors } from "../../api/vendors";
import { API_BASE_URL } from "../../api/axiosConfig"; 

export default function CustomerHome() {
  const navigate = useNavigate();

  const [profile, setProfile] = useState<Customer | null>(null);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // validating customer profile
        const customerData = await getCustomerProfile();
        setProfile(customerData);

        // fetching vendors once customer has been validated
        const vendorData = await getAllVendors();
        setVendors(vendorData.vendors);
      } catch (error) {
        console.error("Failed to load profile", error);
        navigate("/login")
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate]);

  function handleLogout() {
    localStorage.clear();
    navigate("/login");
  }

  if (loading) return <div>Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-100 pt-20 p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Welcome {profile?.name}</h1>
        <button
          onClick={handleLogout}
          className="bg-white rounded-xl shadow p-4 text-center flex flex-col items-center"
        >
          Log out
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {vendors.map((vendor) => (
          <div
            key={vendor.vendor_id}
            className="bg-white rounded-xl shadow-lg hover:shadow-xl transition p-4 text-center flex flex-col"
            style={{ minHeight: "320px" }}
          >
             <div className="flex-1 flex justify-center items-center rounded-lg overflow-hidden border border-white bg-white mb-4">
              <img
                src={
                  vendor.photo
                    ? `${API_BASE_URL}/${vendor.photo}` 
                    : `${API_BASE_URL}/static/placeholder.jpg` 
                }
                alt={vendor.name}
                className="max-w-full max-h-full object-contain"
              />
            </div>
            <div className="mt-auto">
              <h2 className="text-lg font-semibold truncate">{vendor.name}</h2>
              <p className="text-gray-600 mt-1">{vendor.bundle_count} bundles remaining</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

