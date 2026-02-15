import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getVendorTemplates, getTemplateBundleCount } from "../../api/templates";
import { getVendorById } from "../../api/vendors";
import type { Template, Vendor } from "../../types";
import { resolveImageUrl } from "../../utils/imageUrl";
import placeholder from "../../assets/placeholder.jpg";

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP' }).format(amount);
};

const formatPercent = (decimal: number) => {
  return `${Math.round(decimal * 100)}%`;
};

const BagIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 10.5V6a3.75 3.75 0 10-7.5 0v4.5m11.356-1.993l1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 01-1.12-1.243l1.264-12A1.125 1.125 0 015.513 7.5h12.974c.576 0 1.059.435 1.119 1.007zM8.625 10.5a.375.375 0 11-.75 0 .375.375 0 01.75 0zm7.5 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
  </svg>
);

const LeafIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-3.5 h-3.5">
    <path fillRule="evenodd" d="M12.963 2.286a.75.75 0 00-1.071-.136 9.742 9.742 0 00-3.539 6.177c-.129.58-.94.961-1.272.26a4.246 4.246 0 01-.13-1.077 5.25 5.25 0 00-3.805 5.188c0 2.9 2.355 5.25 5.25 5.25 1.583 0 3.018-.707 4.01-1.815.728-.813 1.956-.566 2.338.444.208.549.262 1.13.262 1.62h2.25c0-4.085-3.047-7.46-7.14-7.859a1.503 1.503 0 01-1.353-1.637c.026-.255.06-.508.102-.756a7.502 7.502 0 013.295-4.66z" clipRule="evenodd" />
  </svg>
);

const PhoneIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
        <path fillRule="evenodd" d="M1.5 4.5a3 3 0 013-3h1.372c.86 0 1.61.586 1.819 1.42l1.105 4.423a1.875 1.875 0 01-.694 1.955l-1.293.97c-.135.101-.164.249-.126.352a11.285 11.285 0 006.697 6.697c.103.038.25.009.352-.126l.97-1.293a1.875 1.875 0 011.955-.694l4.423 1.105c.834.209 1.42.959 1.42 1.82V19.5a3 3 0 01-3 3h-2.25C8.552 22.5 1.5 15.448 1.5 4.5V4.5z" clipRule="evenodd" />
    </svg>
);

const ClockIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
        <path fillRule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zM12.75 6a.75.75 0 00-1.5 0v6c0 .414.336.75.75.75h4.5a.75.75 0 000-1.5h-3.75V6z" clipRule="evenodd" />
    </svg>
);

const MapPinIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
        <path fillRule="evenodd" d="M11.54 22.351l.07.04.028.016a.76.76 0 00.723 0l.028-.015.071-.041a16.975 16.975 0 001.144-.742 19.58 19.58 0 002.683-2.282c1.944-1.99 3.963-4.98 3.963-8.827a8.25 8.25 0 00-16.5 0c0 3.846 2.02 6.837 3.963 8.827a19.58 19.58 0 002.682 2.282 16.975 16.975 0 001.145.742zM12 13.5a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
    </svg>
);

type TemplateWithCount = Template & {
  available_count: number;
};

export default function VendorPage() {
  const { vendorId } = useParams();
  const navigate = useNavigate();

  const [vendor, setVendor] = useState<Vendor | null>(null);
  const [templates, setTemplates] = useState<TemplateWithCount[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (!vendorId) return;

        const vendorData = await getVendorById(Number(vendorId));
        setVendor(vendorData);

        const templateData = await getVendorTemplates(Number(vendorId));
        const templatesWithCounts = await Promise.all(
          templateData.templates.map(async (template: Template) => {
            const count = await getTemplateBundleCount(template.template_id);
            return { ...template, available_count: count ?? 0 };
          })
        );
        setTemplates(templatesWithCounts);
      } catch (err) {
        console.error(err);
        navigate("/login");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [vendorId, navigate]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-[hsl(var(--background))]">
        <div className="animate-spin w-8 h-8 border-4 border-[hsl(var(--primary))] border-t-transparent rounded-full"></div>
    </div>
  );

  const available = templates.filter(t => t.available_count > 0);
  const soldOut = templates.filter(t => t.available_count === 0);

  const Badge = ({ type }: { type: 'VE' | 'V' }) => {
    const isVegan = type === 'VE';
    return (
      <span className={`
        text-[10px] font-bold px-2 py-1 rounded-lg backdrop-blur-md shadow-sm border
        ${isVegan 
          ? "bg-green-100/90 text-green-800 border-green-200" 
          : "bg-emerald-50/90 text-emerald-800 border-emerald-200"}
      `}>
        {isVegan ? "Vegan" : "Vegetarian"}
      </span>
    );
  };

  const TemplateCard = ({ template, isSoldOut }: { template: TemplateWithCount; isSoldOut?: boolean }) => {
    const showVegan = template.is_vegan;
    const showVeggie = !template.is_vegan && template.is_vegetarian;

    return (
        <div 
            onClick={() => {
                if (!isSoldOut) {
                navigate(`/bundle/${template.template_id}`);
                }
            }}
            className={`
            group flex flex-col bg-white rounded-3xl overflow-hidden transition-all duration-300 border border-gray-100
            ${isSoldOut 
                ? "opacity-60 grayscale" 
                : "hover:shadow-xl hover:-translate-y-1 cursor-pointer shadow-sm"}
        `}>
        <div className="relative h-44 bg-gray-100 overflow-hidden">
            {/* {template.photo ? (
                <img
                    src={resolveImageUrl(template.photo)}
                    alt={template.title}
                    className="w-full h-full object-cover"
                />
            ) : ( */}
            {
                <div className="absolute inset-0 bg-[hsl(var(--primary)/0.05)] flex items-center justify-center text-[hsl(var(--primary))]">
                    <BagIcon />
                </div>
            }
            
            {!isSoldOut && (
            <div className="absolute top-3 right-3 bg-white/95 px-2.5 py-1 rounded-full shadow-sm">
                <span className="text-xs font-bold text-[hsl(var(--accent))]">
                {template.available_count} left
                </span>
            </div>
            )}

            <div className="absolute top-3 left-3 flex gap-1">
                {showVegan && <Badge type="VE" />}
                {showVeggie && <Badge type="V" />}
            </div>

            {isSoldOut && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/5">
                    <span className="bg-white px-3 py-1 -rotate-6 rounded text-xs font-black text-red-400 uppercase tracking-widest border border-red-100">Sold Out</span>
                </div>
            )}
        </div>

        <div className="p-4 flex flex-col flex-1">
            <h2 className="text-base font-bold text-gray-800 leading-tight mb-1">
            {template.title}
            </h2>

            <p className="text-sm text-gray-500 line-clamp-2 leading-relaxed mb-3">
                {template.description}
            </p>

            {(template.meat_percent > 0 || template.veg_percent > 0 || template.carb_percent > 0) && (
                <div className="text-[10px] font-medium text-gray-400 mb-3 flex gap-2 items-center bg-gray-50 p-2 rounded-lg">
                    {template.meat_percent > 0 && <span>{formatPercent(template.meat_percent)} Meat</span>}
                    {template.meat_percent > 0 && (template.veg_percent > 0 || template.carb_percent > 0) && <span className="text-gray-300">•</span>}
                    {template.veg_percent > 0 && <span>{formatPercent(template.veg_percent)} Veg</span>}
                    {template.veg_percent > 0 && template.carb_percent > 0 && <span className="text-gray-300">•</span>}
                    {template.carb_percent > 0 && <span>{formatPercent(template.carb_percent)} Carb</span>}
                </div>
            )}

            <div className="mt-auto flex justify-between items-center border-t border-gray-100 pt-3">
                <div>
                    <span className="block text-[hsl(var(--primary))] font-bold text-lg">
                        {formatCurrency(template.cost)}
                    </span>
                    {template.carbon_saved > 0 && (
                        <span className="text-[10px] text-gray-400 flex items-center gap-1">
                            <LeafIcon /> {template.carbon_saved}kg CO2e
                        </span>
                    )}
                </div>
                
                {!isSoldOut && (
                    <button className="bg-[hsl(var(--primary))] text-white p-2.5 rounded-full shadow-md shadow-green-100 hover:bg-[hsl(var(--primary-dark))] transition-all active:scale-95">
                        <BagIcon />
                    </button>
                )}
            </div>
        </div>
        </div>
    );
  };

  return (
    <div className="min-h-screen bg-pattern pb-20">
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 pt-8 relative z-10">
        
        {vendor && (
          <div className="flex flex-col md:flex-row gap-8 mb-12">

            <div className="md:w-1/3 flex flex-col items-center md:items-start">
                <div className="w-full aspect-[4/3] rounded-3xl overflow-hidden shadow-2xl border-4 border-white mb-4">
                    <img
                        src={resolveImageUrl(vendor.photo) || placeholder}
                        alt={vendor.name}
                        className="w-full h-full object-cover"
                    />
                </div>
            </div>

            <div className="md:w-2/3 flex flex-col justify-center">
                 <h1 className="text-4xl md:text-5xl font-extrabold text-gray-800 mb-6">{vendor.name}</h1>

                 <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 grid grid-cols-1 md:grid-cols-2 gap-6">

                    <div className="md:col-span-2 flex items-start gap-3">
                        <div className="p-2.5 bg-orange-50 text-[hsl(var(--accent))] rounded-xl shrink-0">
                            <MapPinIcon />
                        </div>
                        <div>
                            <h3 className="font-bold text-gray-800 text-sm uppercase tracking-wide mb-1">Address</h3>
                            <p className="text-gray-600 font-medium">
                                {vendor.street}<br/>
                                {vendor.city}, {vendor.post_code}
                            </p>
                        </div>
                    </div>

                    {vendor.opening_hours && (
                        <div className="flex items-start gap-3">
                            <div className="p-2.5 bg-blue-50 text-blue-500 rounded-xl shrink-0">
                                <ClockIcon />
                            </div>
                            <div>
                                <h3 className="font-bold text-gray-800 text-sm uppercase tracking-wide mb-1">Open Hours</h3>
                                <p className="text-gray-600 font-medium">{vendor.opening_hours}</p>
                            </div>
                        </div>
                    )}

                    {vendor.phone_number && (
                        <div className="flex items-start gap-3">
                            <div className="p-2.5 bg-green-50 text-green-600 rounded-xl shrink-0">
                                <PhoneIcon />
                            </div>
                            <div>
                                <h3 className="font-bold text-gray-800 text-sm uppercase tracking-wide mb-1">Contact</h3>
                                <p className="text-gray-600 font-medium">{vendor.phone_number}</p>
                            </div>
                        </div>
                    )}
                 </div>

                 {vendor.carbon_saved > 0 && (
                     <div className="mt-6 inline-flex items-center gap-2 bg-[hsl(var(--primary)/0.1)] text-[hsl(var(--primary-dark))] px-5 py-3 rounded-2xl font-bold self-start border border-[hsl(var(--primary)/0.2)]">
                         <LeafIcon />
                         <span>This vendor has saved {vendor.carbon_saved}kg of CO2e!</span>
                     </div>
                 )}
            </div>
          </div>
        )}

        <div className="space-y-12">
            {available.length > 0 && (
                <section>
                <div className="flex items-center gap-3 mb-6">
                     <h2 className="text-2xl font-bold text-gray-800">Grab a bag</h2>
                     <div className="h-px bg-gray-200 flex-1"></div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {available.map(template => (
                    <TemplateCard key={template.template_id} template={template} />
                    ))}
                </div>
                </section>
            )}

            {soldOut.length > 0 && (
                <section>
                <div className="flex items-center gap-4 mb-6">
                    <h2 className="text-xl font-bold text-gray-400">Sold Out</h2>
                    <div className="h-px bg-gray-200 flex-1"></div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {soldOut.map(template => (
                    <TemplateCard key={template.template_id} template={template} isSoldOut />
                    ))}
                </div>
                </section>
            )}
        </div>
      </div>
    </div>
  );
}