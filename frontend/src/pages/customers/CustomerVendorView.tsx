import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getVendorTemplates, getTemplateBundleCount } from "../../api/templates";
import { getVendorById } from "../../api/vendors";
import { resolveImageUrl } from "../../utils/imageUrl";
import placeholder from "../../assets/placeholder.jpg";

import type { Template, Vendor } from "../../types";

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
            return {
              ...template,
              available_count: count ?? 0
            };
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

  if (loading) return <div>Loading...</div>;

  const available = templates.filter(t => t.available_count > 0);
  const soldOut = templates.filter(t => t.available_count === 0);

  const TemplateCard = ({ template, isSoldOut }: { template: TemplateWithCount; isSoldOut?: boolean }) => (
    <div
      className={`bg-white rounded-xl shadow-lg transition p-4 flex flex-col aspect-[7/6]
        ${isSoldOut ? "saturate-50 opacity-75 pointer-events-none" : "hover:shadow-xl cursor-pointer"}
      `}
    >
      <div className="flex-1 flex justify-center items-center rounded-lg overflow-hidden border bg-white mb-4">
        <span className="text-gray-400 text-sm">Image Placeholder</span>
        {/* <img
            src={resolveImageUrl(template.photo) || placeholder}
            alt={template.title}
            className="rounded-lg max-w-full max-h-full object-contain"
        /> */}
      </div>

      <div className="mt-auto">
        <h2 className="text-lg font-semibold truncate">
          {template.title}
        </h2>

        <p className={`${isSoldOut ? "text-red-400 font-medium" : "text-gray-600"} mt-1`}>
          {isSoldOut
            ? "Sold Out"
            : `${template.available_count} ${template.available_count === 1 ? "bundle" : "bundles"} remaining`}
        </p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100 pt-20 p-6">
      <button
        onClick={() => navigate(-1)}
        className="mb-6 bg-white rounded-xl shadow p-3"
      >
        Back
      </button>

      {vendor && (
        <div className="flex flex-col items-center justify-center gap-4 mb-8 bg-white p-6 rounded-xl shadow">
            <div className="w-24 h-24 rounded-full overflow-hidden border flex items-center justify-center">
            <img
                src={resolveImageUrl(vendor.photo) || placeholder}
                alt={vendor.name}
                className="w-full h-full object-cover"
            />
            </div>
            <h1 className="text-3xl font-bold text-center">{vendor.name}</h1>
        </div>
        )}

      {available.length > 0 && (
        <>
          <h2 className="text-xl font-bold mb-6">Available Bundles</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {available.map(template => (
              <TemplateCard key={template.template_id} template={template} />
            ))}
          </div>
        </>
      )}

      {soldOut.length > 0 && (
        <>
          <div className="w-11/12 mx-auto border-t-2 border-gray-300 my-12" />
          <h2 className="text-xl font-bold text-gray-400 mb-6">Sold Out</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {soldOut.map(template => (
              <TemplateCard key={template.template_id} template={template} isSoldOut />
            ))}
          </div>
        </>
      )}
    </div>
  );
}