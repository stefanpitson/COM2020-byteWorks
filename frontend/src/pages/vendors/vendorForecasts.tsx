import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer
} from "recharts";
import type { NameType, ValueType, Payload } from "recharts/types/component/DefaultTooltipContent";
import type { Vendor, ForecastWeekData, ForecastDataPoint} from "../../types";
import { getVendorProfile} from '../../api/vendors';
import { getVendorForecasts } from "../../api/forecasts";


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
          <p className="text-sm flex justify-between italic gap-4 ">Click to see more details</p>
      </div>
    );
  }
  return null;
};

interface CategoricalChartState {
  activePayload?: {
    payload: ForecastDataPoint;
  }[];
  activeLabel?: string | number;
  activeTooltipIndex?: number | string | null;
}

export default function VendorForecasts() {
  const navigate = useNavigate();
  const [data, setData] = useState<ForecastWeekData | null>(null);
  const [loading, setLoading] = useState(true);
  const [dataLoading, setDataLoading] = useState(true)
  const [vendor, setVendor] = useState<Vendor>();
  const [model, setModel] = useState<string>("naive")
  const [graphPage, setGraphPage] = useState<number>(0)
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedDataPoint, setSelectedDataPoint] = useState<ForecastDataPoint | null>(null);

  const models = [
    { id: "naive", label: "Naive" },
    { id: "moving average", label: "Moving Average" },
    { id: "linear regression", label: "Linear Regression" }
  ];

  useEffect(() => {
    const fetchForecasts = async () => {
      try {
        setDataLoading(true);
        const vendorData = await getVendorProfile();
        vendorData.carbon_saved = vendorData.carbon_saved ?? 0;
        setVendor(vendorData);
        
        if (!vendorData || vendorData.vendor_id === undefined) {
            console.error("Vendor profile or ID is missing");
            setDataLoading(false);
            return;
        }

        const result = await getVendorForecasts(model);
        setData(result);
        setGraphPage(0);
        setSelectedDataPoint(null);
      } catch (error) {
        console.error("Failed to load analytics", error);
      } finally {
        setLoading(false);
        setDataLoading(false);
      }
    };
    fetchForecasts();
  }, [model]);

  const dayOfWeek = (inDate?: string) => {
    const dateObject = new Date(inDate || "");
    const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const dayName = daysOfWeek[dateObject.getDay()]
    return dayName;
  }

  const handlePageChange = (newPage: number) => {
    setGraphPage(newPage);
    setSelectedDataPoint(null);
  }

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-pattern">
      <div className="animate-spin w-8 h-8 border-4 border-green-600 border-t-transparent rounded-full"></div>
    </div>
  );

  return (
    <div className="min-h-screen bg-pattern pb-20 pt-10">
      <style>{`
        .recharts-wrapper *:focus {
        outline: none;
        }
      `}</style>
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        
        {/* HEADER */}
        <div className="flex justify-between items-end mb-10">
          <div>
            <h1 className="text-4xl font-extrabold text-gray-800">Business Forecasts</h1>
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
            <h2 className="text-4xl font-black text-green-600">£{vendor?.total_revenue?.toFixed(1) ?? "0.0"}</h2>
          </div>
          <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100">
            <p className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">Waste Prevented</p>
            <h2 className="text-4xl font-black text-orange-500">{vendor?.food_saved?.toFixed(1) ?? "0.0"}kg</h2>
          </div>
          <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100">
            <p className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">CO2e Offset</p>
            <h2 className="text-4xl font-black text-blue-500">{vendor?.carbon_saved?.toFixed(1) ?? "0.0"}kg</h2>
          </div>
        </div>

        {/* Bar charts */}
        <div className="space-y-10">
          <div className="flex items-center justify-between gap-4">
            <h2 className="text-2xl font-bold text-gray-800">Weekly Breakdown</h2>
            <div className="h-px bg-gray-200 flex-1"></div>
            <div className="relative">
              <button 
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="flex items-center gap-4 bg-gray-200 px-6 py-2.5 rounded-xl font-bold min-w-[180px] justify-between"
              >
                <span className="capitalize">{model}</span>
                <svg 
                  className={`w-4 h-4 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} 
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {isDropdownOpen && (
                <>
                  <div 
                    className="fixed inset-0 z-10" 
                    onClick={() => setIsDropdownOpen(false)}
                  ></div>
                  <div className="absolute right-0 mt-0 w-full bg-gray-50 rounded-2xl shadow-xl border border-gray-100 z-20 overflow-hidden">
                    {models.map((m) => (
                      <button
                        key={m.id}
                        onClick={() => {
                          setModel(m.id);
                          setIsDropdownOpen(false);
                        }}
                        className={`w-full text-left px-6 py-3 text-sm font-bold transition-colors hover:bg-gray-50
                          ${model === m.id ? 'bg-gray-200' : ''}
                        `}
                      >
                        {m.label}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>

            <div className="bg-white p-6 md:p-10 rounded-3xl shadow-sm border border-gray-100">
              <div className="flex items-center justify-between mb-8">
                <h3 className="text-xl font-bold text-gray-700 flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                  Week starting {data?.week_date}
                </h3>
                <div className="flex gap-2">
                  <button 
                    onClick={() => handlePageChange(Math.max(0, graphPage - 1))}
                    disabled={graphPage === 0}
                    className="p-2 rounded-xl bg-gray-100 hover:bg-gray-200 disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-gray-600 font-bold"
                  >
                     ← 
                  </button>
                  <button 
                    onClick={() => handlePageChange(Math.min((data?.day_datapoints.length || 1) - 1, graphPage + 1))}
                    disabled={graphPage === (data?.day_datapoints.length|| 1) -1 }
                    className="p-2 rounded-xl bg-gray-100 hover:bg-gray-200 disabled:opacity-30 disabled:cursor-not-allowed transition-colors text-gray-600 font-bold"
                  >
                     → 
                  </button>
                </div>
              </div>
              
              <div className="h-[400px] w-full mb-10">
                {dataLoading ? (
                  <div className="flex flex-col items-center justify-center h-full space-y-4">
                    <div className="animate-spin w-12 h-12 border-4 border-green-600 border-t-transparent rounded-full"></div>
                    <p className="text-gray-500 font-bold animate-pulse">Calculating Forecasts...</p>
                  </div>
                ) : data?.day_datapoints[graphPage]?.datapoints.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-full text-gray-500 space-y-2"> 
                    <p className="text-lg font-medium">No data points available for {dayOfWeek(data?.day_datapoints[graphPage]?.date)}</p> 
                    <p className="text-sm">New analytics will appear once transactions occur.</p>     
                  </div> 
                ):(
                  <div className="h-full flex flex-col"> 
                    <p className="text-lg font-medium mb-4">{dayOfWeek(data?.day_datapoints[graphPage]?.date)} - {data?.day_datapoints[graphPage]?.date}</p>
                    <div className="flex-1 outline-none" tabIndex={-1}>
                      <ResponsiveContainer width="100%" height="100%" style={{ outline: 'none' }}>
                        <BarChart 
                          data={data?.day_datapoints[graphPage]?.datapoints} 
                          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                          style={{ outline: 'none', cursor: 'pointer' }}
                          onClick={(state: CategoricalChartState) => {
                            const index = state?.activeTooltipIndex;
                            if (index !== undefined && index !== null) {
                              const datapoints = data?.day_datapoints[graphPage]?.datapoints;
                              const clickedData = datapoints ? datapoints[Number(index)] : null;
                              if (clickedData) {
                                setSelectedDataPoint(clickedData);
                              }
                            }
                          }}
                        >
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
                          
                          <Bar 
                            name="Predicted Sold" 
                            dataKey="predicted_sales" 
                            fill="#22c55e" 
                            radius={[4, 4, 0, 0]} 
                            barSize={20}
                          />
                          <Bar 
                            name="Predicted No Shows" 
                            dataKey="predicted_no_show" 
                            fill="#ef4444" 
                            radius={[4, 4, 0, 0]} 
                            barSize={20}
                          />
                        </BarChart>
                      </ResponsiveContainer> 
                    </div>
                  </div>
                  )
              }
              </div>

              {/* Detailed Data Point View */}
              {selectedDataPoint && (
                <div className="mt-10 pt-10 border-t border-gray-100 animate-in fade-in slide-in-from-top-4 duration-300">
                  <div className="flex flex-col md:flex-row justify-between items-start gap-8">
                    <div className="flex-1 space-y-6">
                      <div>
                        <h4 className="text-2xl font-black text-gray-800 mb-1">{selectedDataPoint.bundle_name}</h4>
                        <p className="text-sm font-bold text-gray-400 uppercase tracking-widest">Selected Item Analysis</p>
                      </div>

                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                        <div className="bg-gray-50 p-4 rounded-2xl">
                          <p className="text-[10px] font-bold text-gray-400 uppercase mb-1">Predicted Sold</p>
                          <p className="text-xl font-bold text-green-600">{selectedDataPoint.predicted_sales}</p>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-2xl">
                          <p className="text-[10px] font-bold text-gray-400 uppercase mb-1">Predicted No-Shows</p>
                          <p className="text-xl font-bold text-red-500">{selectedDataPoint.predicted_no_show}</p>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-2xl">
                          <p className="text-[10px] font-bold text-gray-400 uppercase mb-1">No-Show Prob.</p>
                          <p className="text-xl font-bold text-purple-600">{(selectedDataPoint.chance_of_no_show * 100).toFixed(1)}%</p>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-2xl">
                          <p className="text-[10px] font-bold text-gray-400 uppercase mb-1">Confidence</p>
                          <p className="text-xl font-bold text-blue-500">{(selectedDataPoint.confidence * 100).toFixed(0)}%</p>
                        </div>
                      </div>

                      {selectedDataPoint.recommendation && (
                        <div className="bg-blue-50 p-6 rounded-3xl border border-blue-100">
                          <div className="flex items-center gap-2 mb-3">
                            <span className="p-1.5 bg-blue-100 rounded-lg text-blue-600">
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                              </svg>
                            </span>
                            <p className="text-xs font-bold text-blue-400 uppercase tracking-widest">Our Recommendation</p>
                          </div>
                          <p className="text-m text-blue-900 leading-relaxed font-medium whitespace-pre-wrap">
                            {selectedDataPoint.recommendation.join("\n")}
                          </p>
                        </div>
                      )}
                      {selectedDataPoint.rationale && (
                        <div className="bg-gray-50 p-6 rounded-3xl border border-gray-100">
                          <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-3">Rationale</p>
                          <p className="text-sm text-gray-600 leading-relaxed italic whitespace-pre-wrap">
                            "{selectedDataPoint.rationale.join("\n")}"
                          </p>
                        </div>
                      )}
                      <button 
                        onClick={() => setSelectedDataPoint(null)}
                        className="w-full py-3 text-sm font-bold text-gray-400 hover:text-gray-800 transition-colors"
                      >
                        Close Details
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
  
        </div>
      </div>
    </div>
  );
}