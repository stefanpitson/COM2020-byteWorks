import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getVendorTemplates, getTemplateBundleCount } from "../../api/templates";
import { getVendorProfile } from "../../api/vendors";
import { createBundle } from "../../api/bundles"; 
import type { Template, Vendor } from "../../types";
import { resolveImageUrl } from "../../utils/imageUrl";
import placeholder from "../../assets/placeholder.jpg";

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP' }).format(amount);
};

const formatPercent = (decimal: number) => {
  return `${Math.round(decimal * 100)}%`;
};

// New Plus Icon for adding stock
const PlusIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
  </svg>
);


const BagIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 10.5V6a3.75 3.75 0 10-7.5 0v4.5m11.356-1.993l1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 01-1.12-1.243l1.264-12A1.125 1.125 0 015.513 7.5h12.974c.576 0 1.059.435 1.119 1.007zM8.625 10.5a.375.375 0 11-.75 0 .375.375 0 01.75 0zm7.5 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
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

export default function VendorTemplateManager() {
  const navigate = useNavigate();
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const [vendor, setVendor] = useState<Vendor>();
  const [templates, setTemplates] = useState<TemplateWithCount[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
       
        const vendorData = await getVendorProfile();
        vendorData.carbon_saved = vendorData.carbon_saved ?? 0;
        setVendor(vendorData);
        
        if (!vendorData || vendorData.vendor_id === undefined) {
          console.error("Vendor profile or ID is missing");
          return;
      }

        const templateData = await getVendorTemplates(Number(vendorData.vendor_id));
        const templatesWithCounts = await Promise.all(
          templateData.templates.map(async (template: Template) => {
            const count = await getTemplateBundleCount(template.template_id);
            return { ...template, available_count: count ?? 0 };
          })
        );
        setTemplates(templatesWithCounts);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [navigate, refreshTrigger]);


  const handleAddBundle = async (templateId: number, quantity: number) => {
    try {
      await createBundle({template_id: templateId, amount: quantity});
      
      setRefreshTrigger(prev => prev + 1);
    } catch (error) {
        console.error("Failed to add bundle", error);
        alert("Could not create bundle. Please try again.");
    }
  };

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-[hsl(var(--background))]">
        <div className="animate-spin w-8 h-8 border-4 border-[hsl(var(--primary))] border-t-transparent rounded-full"></div>
    </div>
  );

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

  const TemplateCard = ({ template }: { template: TemplateWithCount }) => {
    const showVegan = template.is_vegan;
    const showVeggie = !template.is_vegan && template.is_vegetarian;
    const isOutOfStock = template.available_count === 0;

    const [addQuantity, setAddQuantity] = useState(1);

    const increment = () => setAddQuantity((prev) => prev + 1);
    const decrement = () => setAddQuantity((prev) => (prev > 1 ? prev - 1 : 1));

    const handleAddStockClick = () => {
      handleAddBundle(template.template_id, addQuantity);
      setAddQuantity(1);
    };

    return (
        <div className="flex flex-col bg-white rounded-3xl overflow-hidden shadow-sm border border-gray-200 transition-all hover:shadow-md">
        <div className="relative h-44 bg-gray-100 overflow-hidden">
            {/* Template Image Placeholder */}
            {template.photo ? (
                <img 
                    src={resolveImageUrl(template.photo) || placeholder} 
                    alt={template.title} 
                    className="w-full h-full object-cover" 
                />
            ) : (
                <div className="absolute inset-0 bg-[hsl(var(--primary)/0.05)] flex items-center justify-center text-[hsl(var(--primary))]">
                    <BagIcon />
                </div>
            )}
            
            <div className={`absolute top-3 right-3 px-2.5 py-1 rounded-full shadow-sm ${isOutOfStock ? 'bg-red-50 text-red-600 border border-red-100' : 'bg-white/95 text-[hsl(var(--accent))]'}`}>
                <span className="text-xs font-bold">
                {template.available_count} in stock
                </span>
            </div>

            <div className="absolute top-3 left-3 flex gap-1">
                {showVegan && <Badge type="VE" />}
                {showVeggie && <Badge type="V" />}
            </div>
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

            <div className="mt-auto flex justify-between items-center border-t border-gray-100 pt-4">
                <span className="block text-gray-800 font-bold text-lg">
                    {formatCurrency(template.cost)}
                </span>
                
                {/* Number Spinner and Add Button Container */}
                <div className="flex items-center gap-2">
                  
                  {/* Number Spinner */}
                  <div className="flex items-center bg-gray-100 rounded-lg p-1">
                    <button
                      onClick={decrement}
                      disabled={addQuantity <= 1}
                      className="w-7 h-7 flex items-center justify-center bg-white rounded shadow-sm text-gray-600 hover:text-black disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <span className="font-bold leading-none">-</span>
                    </button>
                    
                    <span className="w-8 text-center text-sm font-bold text-gray-800">
                      {addQuantity}
                    </span>
                    
                    <button
                      onClick={increment}
                      className="w-7 h-7 flex items-center justify-center bg-white rounded shadow-sm text-gray-600 hover:text-black"
                    >
                      <span className="font-bold leading-none">+</span>
                    </button>
                  </div>

                  {/* Add Stock Button */}
                  <button
                    onClick={handleAddStockClick}
                    className="flex items-center justify-center bg-blue-600 text-white w-10 h-10 rounded-xl shadow-sm hover:bg-blue-700 transition-colors active:scale-95 shrink-0"
                    title="Add Stock"
                  >
                    <PlusIcon />
                  </button>
                </div>
            </div>
        </div>
        </div>
    );
  };

  return (
    <div className="min-h-screen bg-pattern pb-20 ">
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 pt-8 relative z-10">
        
        {/* Vendor Header Area */}
        {vendor && (
          <div className="flex flex-col md:flex-row gap-8 mb-12">
            <div className="md:w-1/3 flex flex-col items-center md:items-start">
                <div className="w-full aspect-[4/3] rounded-3xl overflow-hidden shadow-lg border border-gray-200 mb-4 bg-white">
                    <img
                        src={resolveImageUrl(vendor.photo) || placeholder}
                        alt={vendor.name}
                        className="w-full h-full object-cover"
                    />
                </div>
            </div>

            <div className="md:w-2/3 flex flex-col justify-center">
              <h1 className="text-4xl md:text-5xl font-extrabold text-gray-800 mb-2">My Shop</h1>
              <p className="text-gray-500 mb-6">Manage your templates and daily bundle stock here.</p>

              <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="md:col-span-2 flex items-start gap-3">
                    <div className="p-2.5 bg-orange-50 text-[hsl(var(--accent))] rounded-xl shrink-0">
                        <MapPinIcon />
                    </div>
                    <div>
                        <h3 className="font-bold text-gray-800 text-sm uppercase tracking-wide mb-1">Location</h3>
                        <p className="text-gray-600 font-medium">
                            {vendor.street}, {vendor.city}, {vendor.post_code}
                        </p>
                    </div>
                </div>
              </div>
              <button 
                onClick={() => navigate('/vendor/analytics')}
                className="ml-4 shrink-0 flex items-center gap-2 bg-gray-600 text-white px-4 py-2 rounded-xl hover:bg-black transition-colors"
              >
                <PlusIcon />
                <span className="font-bold text-sm">Analytics</span>
            </button>
            </div>
          </div>
        )}

        {/* Templates Area */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3 flex-1">
                <h2 className="text-2xl font-bold text-gray-800">Your Templates</h2>
                <div className="h-px bg-gray-200 flex-1 ml-4 hidden sm:block"></div>
            </div>
            
            <button 
              onClick={() => navigate('/templates/new')}
              className="ml-4 shrink-0 flex items-center gap-2 bg-gray-800 text-white px-4 py-2 rounded-xl hover:bg-black transition-colors"
            >
              <PlusIcon />
              <span className="font-bold text-sm">New Template</span>
            </button>
          </div>

          {templates.length === 0 ? (
            <div className="text-center py-20 bg-white rounded-3xl border border-dashed border-gray-300">
              <p className="text-gray-500 mb-4">You haven't created any bundle templates yet.</p>
              <button 
                onClick={() => navigate('/templates/new')}
                className="text-blue-600 font-bold hover:underline"
              >
                Create your first template
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {templates.map(template => (
                  <TemplateCard key={template.template_id} template={template} />
                ))}
            </div>
          )}
        </section>

      </div>
    </div>
  );
}