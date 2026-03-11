import { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import type { Customer, Vendor } from "../../types";
import { getCustomerProfile } from "../../api/customers";
import { getAllVendors } from "../../api/vendors";
import placeholder from "../../assets/placeholder.jpg";
import { resolveImageUrl } from "../../utils/imageUrl";

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

const FireIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-fire" viewBox="0 0 16 16">
    <path d="M8 16c3.314 0 6-2 6-5.5 0-1.5-.5-4-2.5-6 .25 1.5-1.25 2-1.25 2C11 4 9 .5 6 0c.357 2 .5 4-2 6-1.25 1-2 2.729-2 4.5C2 14 4.686 16 8 16m0-1c-1.657 0-3-1-3-2.75 0-.75.25-2 1.25-3C6.125 10 7 10.5 7 10.5c-.375-1.25.5-3.25 2-3.5-.179 1-.25 2 1 3 .625.5 1 1.364 1 2.25C11 14 9.657 15 8 15"/>
  </svg>
);

const LeafIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-leaf-fill" viewBox="0 0 16 16">
    <path d="M1.4 1.7c.217.289.65.84 1.725 1.274 1.093.44 2.885.774 5.834.528 2.02-.168 3.431.51 4.326 1.556C14.161 6.082 14.5 7.41 14.5 8.5q0 .344-.027.734C13.387 8.252 11.877 7.76 10.39 7.5c-2.016-.288-4.188-.445-5.59-2.045-.142-.162-.402-.102-.379.112.108.985 1.104 1.82 1.844 2.308 2.37 1.566 5.772-.118 7.6 3.071.505.8 1.374 2.7 1.75 4.292.07.298-.066.611-.354.715a.7.7 0 0 1-.161.042 1 1 0 0 1-1.08-.794c-.13-.97-.396-1.913-.868-2.77C12.173 13.386 10.565 14 8 14c-1.854 0-3.32-.544-4.45-1.435-1.124-.887-1.889-2.095-2.39-3.383-1-2.562-1-5.536-.65-7.28L.73.806z"/>
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
         
          {/* Diet Badges */}
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
          {profile && (
            <>
              <h2 className="text-3xl md:text-4xl font-extrabold text-[hsl(var(--text-main))] mb-6 leading-tight">
                Welcome back, {profile.name}!
              </h2>

              <div className="mb-8 flex justify-center">
                <div className="bg-white rounded-2xl shadow-md border border-green-100 px-6 py-4 flex items-center gap-4 max-w-md w-full">
                  <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-600">
                    <LeafIcon />
                  </div>

                  <div className="text-left">
                    <p className="text-sm text-gray-500">Your impact so far</p>
                    <p className="text-lg font-bold text-green-700">
                      {profile.carbon_saved?.toFixed(1) ?? "0.0"} kg CO₂e saved
                    </p>
                  </div>
                </div>
              </div>
            </>
          )}
    
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