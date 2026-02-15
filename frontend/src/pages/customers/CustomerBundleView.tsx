import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getTemplateById, getTemplateBundleCount } from "../../api/templates";
import { getVendorById } from "../../api/vendors";
import type { Template, Vendor } from "../../types";
import { resolveImageUrl } from "../../utils/imageUrl";
import placeholder from "../../assets/placeholder.jpg";

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency: "GBP",
  }).format(amount);
};

const formatPercent = (decimal: number) => {
  return `${Math.round(decimal * 100)}%`;
};

const LeafIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-leaf-fill" viewBox="0 0 16 16">
    <path d="M1.4 1.7c.217.289.65.84 1.725 1.274 1.093.44 2.885.774 5.834.528 2.02-.168 3.431.51 4.326 1.556C14.161 6.082 14.5 7.41 14.5 8.5q0 .344-.027.734C13.387 8.252 11.877 7.76 10.39 7.5c-2.016-.288-4.188-.445-5.59-2.045-.142-.162-.402-.102-.379.112.108.985 1.104 1.82 1.844 2.308 2.37 1.566 5.772-.118 7.6 3.071.505.8 1.374 2.7 1.75 4.292.07.298-.066.611-.354.715a.7.7 0 0 1-.161.042 1 1 0 0 1-1.08-.794c-.13-.97-.396-1.913-.868-2.77C12.173 13.386 10.565 14 8 14c-1.854 0-3.32-.544-4.45-1.435-1.124-.887-1.889-2.095-2.39-3.383-1-2.562-1-5.536-.65-7.28L.73.806z"/>
  </svg>
);

type TemplateWithCount = Template & {
  available_count: number;
};

export default function BundleDetailsPage() {
  const { templateId } = useParams();
  const navigate = useNavigate();

  const [bundle, setBundle] = useState<TemplateWithCount | null>(null);
  const [vendor, setVendor] = useState<Vendor | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBundle = async () => {
      try {
        if (!templateId) return;

        const template = await getTemplateById(Number(templateId));
        const count = await getTemplateBundleCount(Number(templateId));

        let vendorData = null;
        if (template.vendor) {
          vendorData = await getVendorById(template.vendor);
          setVendor(vendorData);
        }

        setBundle({
          ...template,
          available_count: count ?? 0,
        });
      } catch (error) {
        console.error(error);
        navigate("/login");
      } finally {
        setLoading(false);
      }
    };

    fetchBundle();
  }, [templateId, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[hsl(var(--background))]">
        <div className="animate-spin w-8 h-8 border-4 border-[hsl(var(--primary))] border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (!bundle) return null;

  const isSoldOut = bundle.available_count === 0;

  const Badge = ({ type }: { type: "VE" | "V" }) => (
    <span
      className={`text-xs font-bold px-3 py-1 rounded-full border shadow-sm
        ${
          type === "VE"
            ? "bg-green-100 text-green-800 border-green-200"
            : "bg-emerald-50 text-emerald-800 border-emerald-200"
        }`}
    >
      {type === "VE" ? "Vegan" : "Vegetarian"}
    </span>
  );

  return (
    <div className="min-h-screen bg-pattern pb-32">
      <div className="max-w-6xl mx-auto px-6 pt-12">
        {bundle && 
          <div className="mb-8">
            <h1 className="text-4xl md:text-5xl font-extrabold text-black drop-shadow-md px-4 py-2 rounded-lg inline-block bg-white/5">
              {vendor?.name}
            </h1>
          </div>
        }

        <div className="grid lg:grid-cols-2 gap-12">

          {/* Image Placeholder + Environmental Impact */}
          <div className="space-y-6">

            <div className="relative h-[420px] rounded-3xl overflow-hidden shadow-xl border border-gray-100 bg-gray-100">
              <div className="w-full h-full bg-[hsl(var(--primary)/0.05)] flex items-center justify-center text-[hsl(var(--primary))] text-5xl font-bold">
                {bundle.title.charAt(0)}
              </div>

              {!isSoldOut && (
                <div className="absolute top-6 right-6 bg-white px-5 py-2 rounded-full shadow-md text-sm font-bold text-[hsl(var(--accent))]">
                  {bundle.available_count} left today
                </div>
              )}
            </div>

            {bundle.carbon_saved > 0 && (
              <div className="bg-[hsl(var(--primary)/0.08)] border border-[hsl(var(--primary)/0.15)] rounded-2xl p-6">
                <div className="flex items-center gap-3 text-[hsl(var(--primary-dark))] font-semibold mb-2">
                  <LeafIcon />
                  Environmental Impact
                </div>
                <p className="text-gray-600 text-sm">
                  Reserving this bundle prevents approximately{" "}
                  <span className="font-semibold text-gray-800">
                    {bundle.carbon_saved}kg of CO₂e
                  </span>{" "}
                  from being wasted.
                </p>
              </div>
            )}
          </div>

          {/* Bundle Info */}
          <div className="flex flex-col">

            <div className="flex flex-wrap gap-2 mb-4">
              {bundle.is_vegan && <Badge type="VE" />}
              {!bundle.is_vegan && bundle.is_vegetarian && <Badge type="V" />}
            </div>

            <h1 className="text-4xl font-extrabold text-gray-900 mb-4">
              {bundle.title}
            </h1>

            <p className="text-gray-600 leading-relaxed mb-8 text-lg">
              {bundle.description}
            </p>

            {/* Composition Section */}
            {(bundle.meat_percent > 0 ||
              bundle.veg_percent > 0 ||
              bundle.carb_percent > 0) && (
              <div className="mb-8">
                <h3 className="text-sm uppercase tracking-wide text-gray-400 font-semibold mb-3">
                  Estimated Composition
                </h3>
                <div className="flex gap-6 text-sm font-medium text-gray-700">
                  {bundle.meat_percent > 0 && (
                    <span>{formatPercent(bundle.meat_percent)} Meat</span>
                  )}
                  {bundle.veg_percent > 0 && (
                    <span>{formatPercent(bundle.veg_percent)} Vegetables</span>
                  )}
                  {bundle.carb_percent > 0 && (
                    <span>{formatPercent(bundle.carb_percent)} Carbohydrates</span>
                  )}
                </div>
              </div>
            )}

            {/* Allergen Section */}
            <div className="mb-10">
              <h3 className="text-sm uppercase tracking-wide text-gray-400 font-semibold mb-3">
                Allergens
              </h3>

              {bundle.allergens && bundle.allergens.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {bundle.allergens.map((allergen) => (
                    <span
                      key={allergen.allergen_id}
                      className="px-3 py-1 text-xs font-semibold bg-red-50 text-red-600 border border-red-200 rounded-full"
                    >
                      {allergen.title}
                    </span>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500">
                  No known allergens listed for this bundle.
                </p>
              )}
            </div>

            {/* Pricing + Reserve Button */}
            <div className="mt-auto border-t border-gray-100 pt-8">

              <div className="flex items-center justify-between mb-6">
                <div>
                  <div className="text-sm text-gray-400 uppercase tracking-wide">
                    Price
                  </div>
                  <div className="text-3xl font-bold text-[hsl(var(--primary))]">
                    {formatCurrency(bundle.cost)}
                  </div>
                </div>
              </div>

              <button
                disabled={isSoldOut}
                className={`w-full py-5 rounded-2xl font-bold text-lg transition-all
                  ${
                    isSoldOut
                      ? "bg-gray-200 text-gray-400"
                      : "bg-[hsl(var(--primary))] text-white hover:bg-[hsl(var(--primary-dark))] shadow-lg shadow-green-100 active:scale-95"
                  }`}
              >
                {isSoldOut ? "Sold Out" : "Reserve Bundle"}
              </button>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}