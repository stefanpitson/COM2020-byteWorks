import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer
} from "recharts";
import type { NameType, ValueType, Payload } from "recharts/types/component/DefaultTooltipContent";
import { getVendorAnalytics } from "../../api/analytics";
import type { Vendor, ForecastWeekData, ForecastDataPoint} from "../../types";
import { getVendorProfile } from "../../api/vendors";


interface CustomTooltipProps {
  active?: boolean;
  payload?: Payload<ValueType, NameType>[];
  label?: string;
}

const CustomTooltip = ({ active, payload, label }: CustomTooltipProps) => {
  if (active && payload && payload.length) {
    // Access the raw data point from the first item in the payload array
    const templateDatapoint = payload[0].payload as ForecastDataPoint;

    return (
      <div className="bg-white p-4 shadow-xl rounded-2xl border border-gray-100 max-w-sm">
        <p className="font-bold text-gray-800 mb-2">{label}</p>
        
        {/* Render the standard bars (Predicted Sold, No Shows) */}
        <div className="space-y-1 mb-3 border-b border-gray-50 pb-3">
          {payload.map((entry: Payload<ValueType, NameType>, index: number) => (
            <p key={index} className="text-sm flex justify-between gap-4" style={{ color: entry.color }}>
              <span className="capitalize">{entry.name}:</span>
              <span className="font-mono font-bold">{entry.value}</span>
            </p>
          ))}
          <p className="text-sm flex justify-between gap-4 text-purple-600">
            <span>No Show Prob:</span>
            <span className="font-mono font-bold">{(templateDatapoint.chance_of_no_show * 100).toFixed(1)}%</span>
          </p>
        </div>

        {/* Render the Recommendation if it exists */}
        {templateDatapoint.recommendation && (
          <div className="bg-blue-50 p-2.5 rounded-xl mb-2">
            <p className="text-[10px] font-bold text-blue-400 uppercase tracking-widest mb-1">
              Recommendation
            </p>
            <p className="text-xs text-blue-700 leading-relaxed">
              {templateDatapoint.recommendation}
            </p>
          </div>
        )}

        {/* Render the Rationale if it exists */}
        {templateDatapoint.rationale && (
          <div className="bg-gray-50 p-2.5 rounded-xl mb-2">
            <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">
              Rationale
            </p>
            <p className="text-xs text-gray-600 leading-relaxed italic">
              {templateDatapoint.rationale}
            </p>
          </div>
        )}

        {/* Render the Confidence if it exists */}
        {templateDatapoint.confidence && (
          <div className="bg-gray-50 p-2.5 rounded-xl">
            <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">
              Confidence
            </p>
            <p className="text-xs text-gray-600 leading-relaxed italic">
              {templateDatapoint.confidence}
            </p>
          </div>
        )}
      </div>
    );
  }
  return null;
};

export default function VendorAnalytics() {
  const navigate = useNavigate();
  const [data, setData] = useState<ForecastWeekData | null>(null);
  const [loading, setLoading] = useState(true);
    const [vendor, setVendor] = useState<Vendor>();

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {

        const vendorData = await getVendorProfile();
        vendorData.carbon_saved = vendorData.carbon_saved ?? 0;
        setVendor(vendorData);
        
        if (!vendorData || vendorData.vendor_id === undefined) {
            console.error("Vendor profile or ID is missing");
            return;
        }

        const result = await getVendorAnalytics();
        setData(result);
      } catch (error) {
        console.error("Failed to load analytics", error);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-pattern">
      <div className="animate-spin w-8 h-8 border-4 border-green-600 border-t-transparent rounded-full"></div>
    </div>
  );

  return (
    <div className="min-h-screen bg-pattern pb-20 pt-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        
        {/* HEADER */}
        <div className="flex justify-between items-end mb-10">
          <div>
            <h1 className="text-4xl font-extrabold text-gray-800">Business Analytics</h1>
            <p className="text-gray-500 mt-2">Track your impact and sales performance</p>
          </div>
          <button 
            onClick={() => navigate(-1)}
            className="text-sm font-bold text-gray-500 hover:text-gray-800 transition-colors"
          >
            ← Back to Dashboard
          </button>
        </div>

        {/* Big stats from vendor */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100">
            <p className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">Lifetime Revenue</p>
            <h2 className="text-4xl font-black text-green-600">£{vendor?.total_revenue?.toLocaleString()}</h2>
          </div>
          <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100">
            <p className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">Waste Prevented</p>
            <h2 className="text-4xl font-black text-orange-500">{vendor?.food_saved}kg</h2>
          </div>
          <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100">
            <p className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">CO2e Offset</p>
            <h2 className="text-4xl font-black text-blue-500">{vendor?.carbon_saved}kg</h2>
          </div>
        </div>

        {/* Bar charts */}
        <div className="space-y-10">
          <div className="flex items-center gap-4">
            <h2 className="text-2xl font-bold text-gray-800">Weekly Breakdown</h2>
            <div className="h-px bg-gray-200 flex-1"></div>
          </div>

            <div className="bg-white p-6 md:p-10 rounded-3xl shadow-sm border border-gray-100">
              <h3 className="text-lg font-bold text-gray-700 mb-8 flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                Week of {data?.week_date}
              </h3>
              
              <div className="h-[350px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data?.datapoints} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                    <XAxis 
                      dataKey="bundle_name" 
                      axisLine={false} 
                      tickLine={false} 
                      tick={{ fill: '#9ca3af', fontSize: 12 }} 
                      dy={10}
                    />
                    <YAxis axisLine={false} tickLine={false} tick={{ fill: '#9ca3af', fontSize: 12 }} />
                    <Tooltip content={<CustomTooltip />} cursor={{ fill: '#f9fafb' }} />
                    <Legend verticalAlign="top" align="right" iconType="circle" wrapperStyle={{ paddingBottom: '20px' }} />
                    
                    <Bar name="Predicted Sold" dataKey="predicted_sales" fill="#22c55e" radius={[4, 4, 0, 0]} barSize={20} />
                    <Bar name="Predicted No Shows" dataKey="no_show" fill="#ef4444" radius={[4, 4, 0, 0]} barSize={20} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
  
        </div>
      </div>
    </div>
  );
}