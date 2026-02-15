import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import type { Customer, Vendor } from "../../types";
import { getCustomerProfile } from "../../api/customers";
import { getAllVendors } from "../../api/vendors";
import { clearAuthSession } from "../../utils/authSession";
import placeholder from "../../assets/placeholder.jpg";
import { resolveImageUrl } from "../../utils/imageUrl";

// --- Icons ---
const MapPinIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-3.5 h-3.5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
  </svg>
);

const SearchIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-5 h-5 text-gray-400">
    <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
  </svg>
);

const LogOutIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
  </svg>
);

const FireIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-3 h-3">
    <path fillRule="evenodd" d="M12.963 2.286a.75.75 0 00-1.071-.136 9.742 9.742 0 00-3.539 6.177c-.129.58-.94.961-1.272.26a4.246 4.246 0 01-.13-1.077 5.25 5.25 0 00-3.805 5.188c0 2.9 2.355 5.25 5.25 5.25 1.583 0 3.018-.707 4.01-1.815.728-.813 1.956-.566 2.338.444.208.549.262 1.13.262 1.62h2.25c0-4.085-3.047-7.46-7.14-7.859a1.503 1.503 0 01-1.353-1.637c.026-.255.06-.508.102-.756a7.502 7.502 0 013.295-4.66z" clipRule="evenodd" />
  </svg>
);

type HomeVendor = Vendor & {
  bundle_count: number;
  has_vegan: boolean;
  has_vegetarian: boolean;
};

export default function CustomerHome() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<Customer | null>(null);
  const [vendors, setVendors] = useState<HomeVendor[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [customerData, vendorData] = await Promise.all([
          getCustomerProfile(),
          getAllVendors()
        ]);
        setProfile(customerData);
        setVendors(vendorData.vendors);
      } catch (error) {
        console.error("Failed to load data", error);
        navigate("/login");
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

  // Filter vendors based on search term
  const filteredVendors = useMemo(() => {
    return vendors.filter(v => 
      v.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [vendors, searchTerm]);

  const availableVendors = filteredVendors.filter((v) => v.bundle_count > 0);
  const soldOutVendors = filteredVendors.filter((v) => v.bundle_count === 0);

  const Badge = ({ type }: { type: 'VE' | 'V' }) => (
    <span className={`
      text-[10px] font-bold px-2 py-1 rounded-full border shadow-sm backdrop-blur-md
      ${type === 'VE' 
        ? "bg-green-100/90 text-green-800 border-green-200" 
        : "bg-emerald-50/90 text-emerald-700 border-emerald-200"}
    `}>
      {type === 'VE' ? "Vegan" : "Veggie"}
    </span>
  );

  const VendorCard = ({ vendor, isSoldOut }: { vendor: HomeVendor; isSoldOut?: boolean }) => {
    // If < 5 items, show orange "Fire" badge
    const isLowStock = vendor.bundle_count > 0 && vendor.bundle_count < 5;

    return (
      <div
        onClick={() => !isSoldOut && navigate(`/vendor/${vendor.vendor_id}`)}
        className={`
          group relative flex flex-col bg-white rounded-3xl overflow-hidden transition-all duration-300 border border-transparent
          ${isSoldOut 
            ? "opacity-60 grayscale cursor-not-allowed" 
            : "hover:-translate-y-1 hover:shadow-xl hover:border-orange-100 cursor-pointer shadow-sm"}
        `}
      >
        {/* Image Section */}
        <div className="relative h-40 bg-gray-100 overflow-hidden">
          {vendor.photo ? (
            <img
              src={resolveImageUrl(vendor.photo) || placeholder}
              alt={vendor.name}
              className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
            />
          ) : (
            <div className="w-full h-full bg-[hsl(var(--primary)/0.1)] flex items-center justify-center text-[hsl(var(--primary))] font-bold text-2xl">
                {vendor.name.charAt(0)}
            </div>
          )}
         
          {/* Diet Badges - Cleaner logic: Vegan implies Veggie */}
          <div className="absolute top-3 left-3 flex gap-1">
            {vendor.has_vegan && <Badge type="VE" />}
            {vendor.has_vegetarian && !vendor.has_vegan && <Badge type="V" />}
          </div>

          {/* Urgency Badge */}
          {!isSoldOut && (
             <div className={`
               absolute bottom-3 right-3 text-white text-xs font-bold px-2.5 py-1 rounded-full shadow-md flex items-center gap-1
               ${isLowStock ? "bg-[hsl(var(--accent))]" : "bg-[hsl(var(--primary))]"}
             `}>
               {isLowStock && <FireIcon />}
               {vendor.bundle_count} left
             </div>
          )}
        </div>

        {/* Info Section */}
        <div className="p-4 flex flex-col flex-1">
          <div className="flex justify-between items-start mb-1">
              <h2 className="text-lg font-bold text-gray-800 leading-tight truncate w-full group-hover:text-[hsl(var(--primary))] transition-colors">
                {vendor.name}
              </h2>
          </div>
          
          {/* Location */}
          <div className="flex items-center gap-1 text-gray-400 text-xs mb-4">
              <span className="text-[hsl(var(--accent))]"><MapPinIcon /></span>
              <span>0.8 miles away</span>
          </div>

          <div className="mt-auto border-t border-gray-100 pt-3 flex justify-between items-center">
             {isSoldOut ? (
                <span className="text-red-400 text-xs font-bold uppercase tracking-wider">Sold Out</span>
             ) : (
                <>
                    <span className="text-gray-400 text-xs">Collect today</span>
                    <span className="w-6 h-6 rounded-full bg-orange-50 flex items-center justify-center text-[hsl(var(--accent))] group-hover:bg-[hsl(var(--accent))] group-hover:text-white transition-colors">
                        &rarr;
                    </span>
                </>
             )}
          </div>
        </div>
      </div>
    );
  };

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-[hsl(var(--background))]">
        <div className="animate-spin w-8 h-8 border-4 border-[hsl(var(--primary))] border-t-transparent rounded-full"></div>
    </div>
  );

  return (
    <div className="min-h-screen bg-pattern pb-12">

      <div className="max-w-7xl mx-auto px-4 sm:px-6 pt-10">
        
        {/* Search Header */}
        <div className="mb-10 text-center max-w-2xl mx-auto">
            <h1 className="text-3xl md:text-4xl font-extrabold text-[hsl(var(--text-main))] mb-6 leading-tight">
                Save food, <span className="text-[hsl(var(--accent))] underline decoration-4 decoration-[hsl(var(--accent)/0.3)]">save money.</span>
            </h1>
            
            {/* Functional Search Bar */}
            <div className="relative group shadow-lg rounded-2xl">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <SearchIcon />
                </div>
                <input 
                    type="text" 
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search for cafes, bakeries..." 
                    className="block w-full pl-11 pr-4 py-4 border-none rounded-2xl leading-5 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[hsl(var(--accent))] transition-all"
                />
            </div>
        </div>

        {/* Content Grid */}
        <div className="space-y-12">
          {availableVendors.length > 0 && (
            <section>
              <div className="flex items-center justify-between mb-6 px-1">
                  <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                    Available Now <span className="text-xs font-normal text-gray-500 bg-white px-2 py-1 rounded-full shadow-sm">({availableVendors.length})</span>
                  </h2>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {availableVendors.map((vendor) => (
                  <VendorCard key={vendor.vendor_id} vendor={vendor} />
                ))}
              </div>
            </section>
          )}

          {soldOutVendors.length > 0 && (
            <section>
              <div className="flex items-center gap-4 mb-6 px-1">
                  <h2 className="text-xl font-bold text-gray-400">Sold Out Today</h2>
                  <div className="h-px bg-gray-200 flex-1"></div>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {soldOutVendors.map((vendor) => (
                  <VendorCard key={vendor.vendor_id} vendor={vendor} isSoldOut={true} />
                ))}
              </div>
            </section>
          )}

          {/* Empty State */}
          {filteredVendors.length === 0 && !loading && (
              <div className="text-center py-20">
                  <div className="text-4xl mb-4">🥕</div>
                  <h3 className="text-lg font-bold text-gray-800">No places found</h3>
                  <p className="text-gray-500">Try adjusting your search term.</p>
              </div>
          )}
        </div>

      </div>
    </div>
  );
}