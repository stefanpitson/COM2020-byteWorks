import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import type { Customer, Vendor } from "../../types";
import { getCustomerProfile } from "../../api/customers";
import { getAllVendors } from "../../api/vendors";
import { API_BASE_URL } from "../../api/axiosConfig"; 
import { clearAuthSession } from "../../utils/authSession";

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
    clearAuthSession();
    navigate("/login");
  }

  const availableVendors = vendors.filter((v) => v.bundle_count > 0);
  const soldOutVendors = vendors.filter((v) => v.bundle_count === 0);

  const VendorCard = ({ vendor, isSoldOut }: { vendor: Vendor; isSoldOut?: boolean }) => (
    <div
      key={vendor.vendor_id}
      className={`bg-white rounded-xl shadow-lg transition p-4 text-left flex flex-col aspect-[7/6]
        ${isSoldOut ? "saturate-50 opacity-75 pointer-events-none" : "hover:shadow-xl"}
      `}
    >
      <div className="flex-1 flex justify-center items-center rounded-lg overflow-hidden border border-white bg-white mb-4">
        <img
          src={
            vendor.photo
              ? `${API_BASE_URL}/${vendor.photo}`
              : `${API_BASE_URL}/static/placeholder.jpg`
          }
          alt={vendor.name}
          className="rounded-lg max-w-full max-h-full object-contain"
        />
      </div>
      <div className="mt-auto">
        <div className="flex justify-between items-start gap-2">
          <h2 className="text-lg font-semibold truncate">{vendor.name}</h2>

          <div className="flex gap-1 shrink-0">
            {vendor.has_vegan && (
              <span className="bg-green-100 text-green-700 text-[10px] font-bold px-1.5 py-0.5 rounded border border-green-200">
                VE
              </span>
            )}
            {vendor.has_vegetarian && (
              <span className="bg-emerald-50 text-emerald-600 text-[10px] font-bold px-1.5 py-0.5 rounded border border-emerald-200">
                V
              </span>
            )}
          </div>
        </div>
        <p className={`${isSoldOut ? "text-red-400 font-medium" : "text-gray-600"} mt-1`}>
          {isSoldOut
            ? "Sold Out"
            : `${vendor.bundle_count} ${vendor.bundle_count === 1 ? "bundle" : "bundles"} remaining`}
        </p>
      </div>
    </div>
  );

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
      {availableVendors.length > 0 && (
        <>
          <h2 className="text-xl font-bold text-black mb-6 pl-2">Available Bundles</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {availableVendors.map((vendor) => (
              <VendorCard key={vendor.vendor_id} vendor={vendor} />
            ))}
          </div>
        </>
      )}

      {soldOutVendors.length > 0 && (
        <>
          {availableVendors.length > 0 && (
            <div className="w-11/12 mx-auto border-t-2 border-gray-300 my-12" />
          )} 

          <h2 className="text-xl font-bold text-gray-400 mb-6 pl-2">Sold Out</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {soldOutVendors.map((vendor) => (
              <VendorCard key={vendor.vendor_id} vendor={vendor} isSoldOut={true} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

