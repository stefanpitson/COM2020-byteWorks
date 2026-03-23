import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line
} from "recharts";
import type { 
  AnalyticSellThrough, AnalyticsDiscountData, 
  AnalyticsPostingData, AnalyticsBestBundles, AnalyticsWaste 
} from "../../types";
import { 
  getSellThrough, getPricingEffectiveness, 
  getPostingWindows, getBestSellers, getWasteProxy 
} from "../../api/analytics";

const COLORS = ['#22c55e', '#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6'];

export default function VendorAnalytics() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [sellView, setSellView] = useState<string>("weekly_proportions")
  const [sellThroughLabel, setSellThroughLabel] = useState<string>("")
  
  const [sellThrough, setSellThrough] = useState<AnalyticSellThrough | null>(null);
  const [pricingEffectiveness, setPricingEffectiveness] = useState<AnalyticsDiscountData | null>(null);
  const [postingWindows, setPostingWindows] = useState<AnalyticsPostingData| null>(null);
  const [bestSellers, setBestSellers] = useState<AnalyticsBestBundles | null>(null);
  const [waste, setWaste] = useState<AnalyticsWaste | null>(null);
  const [sellThroughPieChartData, setSellThroughPieChartData] = useState<Array<{ name: string; value: number }>>([])

  useEffect(() => {
    const fetchAllData = async () => {
      try {
        const [
            sellThroughData,
            pricingData,
            postingWindowData,
            bestSellersData,
            wasteData
        ] = await Promise.all([
          getSellThrough(),
          getPricingEffectiveness(),
          getPostingWindows(),
          getBestSellers(),
          getWasteProxy()
        ]);
        setSellThrough(sellThroughData);
        setPricingEffectiveness(pricingData);
        setPostingWindows(postingWindowData);
        setBestSellers(bestSellersData);
        setWaste(wasteData);
        if (sellThroughData) {
          setSellThroughPieChartData([
          { name: 'Collected', value: sellThroughData.weekly_proportions.collected },
          { name: 'No-Shows', value: sellThroughData.weekly_proportions.no_show },
          { name: 'Expired', value: sellThroughData.weekly_proportions.expired },
          ])
          const weekDate = sellThroughData.weekly_proportions.week_start_date
          setSellThroughLabel(`Week Starting ${dayOfWeek(weekDate)} ${weekDate}`)
        }
      } catch (error) {
        console.error("Failed to load analytics data", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, []);

  const handleViewChange = () => {
    if (sellView === "weekly_proportions") {
      setSellView("all_time_proportions")
      if (sellThrough) {
        setSellThroughPieChartData([
        { name: 'Collected', value: sellThrough.all_time_proportions.collected },
        { name: 'No-Shows', value: sellThrough.all_time_proportions.no_show },
        { name: 'Expired', value: sellThrough.all_time_proportions.expired },
        ])
        setSellThroughLabel(`All Time`)
      }
    } else {
      setSellView("weekly_proportions")
      if (sellThrough) {
        setSellThroughPieChartData([
        { name: 'Collected', value: sellThrough.weekly_proportions.collected },
        { name: 'No-Shows', value: sellThrough.weekly_proportions.no_show },
        { name: 'Expired', value: sellThrough.weekly_proportions.expired },
        ])
        const weekDate = sellThrough.weekly_proportions.week_start_date
        setSellThroughLabel(`Week Starting ${dayOfWeek(weekDate)} ${weekDate}`)
      }
    }
  }

  const dayOfWeek = (inDate?: string) => {
    const dateObject = new Date(inDate || "");
    const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const dayName = daysOfWeek[dateObject.getDay()]
    return dayName;
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
            <h1 className="text-4xl font-extrabold text-gray-800">Business Analytics</h1>
            <p className="text-gray-500 mt-2">Deep dive into your shop's performance</p>
          </div>
          <button 
            onClick={() => navigate(-1)}
            className="text-sm font-bold text-gray-500 hover:text-gray-800 transition-colors"
          >
            ← Back to Dashboard
          </button>
        </div>

        {/* QUICK STATS */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 transition-all hover:shadow-md">
            <p className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">Top Selling Bundle</p>
            <h2 className="text-2xl font-black text-blue-600 truncate">{bestSellers?.top_bundle || "N/A"}</h2>
          </div>
          <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 transition-all hover:shadow-md">
            <p className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">Avg. Bundle Weight</p>
            <h2 className="text-4xl font-black text-orange-500">{waste?.average_bundle_weight?.toFixed(1) ?? "0.0"}kg</h2>
          </div>
          <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 transition-all hover:shadow-md">
            <p className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">Total Waste Saved</p>
            <h2 className="text-4xl font-black text-green-600">{waste?.total_waste_avoided?.toFixed(1) ?? "0.0"}kg</h2>
          </div>
          <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 transition-all hover:shadow-md">
            <p className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">Best Posting Window</p>
            <h2 className="text-2xl font-black text-purple-600">{postingWindows?.top_post_window || "N/A"}</h2>
          </div>
        </div>

        {/* ANALYTICS GRID */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          
          {/* Sell-Through Proportion */}
          <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 flex flex-col">
            <h3 className="text-xl font-bold text-gray-800 mb-6">Sell-Through Rate</h3>
            <div className="flex justify-between items-center w-full mb-6">
              <h3 className="text-sm font-bold text-gray-400 tracking-wider">
                {sellThroughLabel}
              </h3>
              <button 
                className="bg-green-500 hover:bg-green-600 text-white text-xs font-bold px-4 py-2 rounded-full transition-all shadow-sm active:scale-95 border-2 border-green-600"
                onClick={() => handleViewChange()}
              >
                Change Timeframe
              </button>
            </div>
            
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sellThroughPieChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={sellThroughPieChartData.filter(d => d.value > 0).length > 1 ? 5 : 0}
                    dataKey="value"
                    stroke="none"
                  >
                    {sellThroughPieChartData.map((_entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <p className="text-gray-500 text-sm mt-4 italic text-center">
              Overview of bundle statuses: collected, missed, or expired.
            </p>
          </div>

          {/* Best Sellers */}
          <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 flex flex-col">
            <h3 className="text-xl font-bold text-gray-800 mb-6">Popular Bundles</h3>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart 
                  margin={{bottom: 30}}
                  data={bestSellers?.bundle_datapoints || []}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="bundle_title" 
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: '#9ca3af', fontSize: 12 }} 
                    label={{value: "Bundle Name", position: 'insideBottom', offset: -25}}
                  />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#9ca3af', fontSize: 12 }} />
                  <Tooltip 
                    labelFormatter={(label) => `Bundle :  ${label}`}
                  />
                  <Bar 
                    dataKey="weekly_average" 
                    fill="#3b82f6" 
                    radius={[4, 4, 0, 0]} 
                    name= "Weekly Average"  
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-gray-500 text-sm mt-4 italic text-center">
              Average weekly sales per bundle template.
            </p>
          </div>

          {/* Pricing Effectiveness */}
          <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 flex flex-col">
            <h3 className="text-xl font-bold text-gray-800 mb-6">Pricing Effectiveness</h3>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart 
                margin={{ top: 10, right: 10, left: 10, bottom: 30 }}
                data={pricingEffectiveness?.coordinates.map(coord => ({
                ...coord,
                discount: (coord.discount * 100).toFixed(1),
                sell_through: +(coord.sell_through * 100).toFixed(1)
                })) || []}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                    <XAxis 
                        dataKey="discount" 
                        name="Discount" 
                        unit="%" 
                        axisLine={false} 
                        tickLine={false} 
                        tick={{ fill: '#9ca3af', fontSize: 12 }} 
                        label={{value: "Discount (%)", position: 'insideBottom', offset: -25}}
                    />
                    <YAxis 
                        dataKey="sell_through" 
                        name="Sell-Through Rate" 
                        unit="%" 
                        axisLine={false} 
                        tickLine={false} 
                        tick={{ fill: '#9ca3af', fontSize: 12 }}
                        label={{ value: 'Sell Through Rate (%)', angle: -90, position: 'insideBottomLeft'}}
                    />
                    <Tooltip 
                        formatter={(value) => value !== undefined ? `${value}%` : 'N/A'} 
                        labelFormatter={(label) => `Discount :  ${label}%`}
                        />
                    <Line 
                        type="monotone" 
                        dataKey="sell_through" 
                        stroke="#f59e0b" 
                        strokeWidth={3} dot={{ r: 6 }} 
                        activeDot={{ r: 8 }} 
                        name="Sell-Through Rate"/>
                </LineChart>
              </ResponsiveContainer>
            </div>
            <p className="text-gray-500 text-sm mt-4 italic text-center">
              Relationship between discount percentage and sell-through success.
            </p>
          </div>

          {/* Posting Windows */}
          <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 flex flex-col">
            <h3 className="text-xl font-bold text-gray-800 mb-6">Peak Posting Times</h3>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart 
                  margin={{ top: 10, right: 10, left: 10, bottom: 30 }}
                  data={postingWindows?.window_datapoints || []}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                  <XAxis 
                    dataKey="posting_timeslot" 
                    name="Weekly Average Bundles Sold"
                    axisLine={false} 
                    tickLine={false} 
                    tick={{ fill: '#9ca3af', fontSize: 11 }} 
                    interval={0}
                    angle={-7}
                    textAnchor="middle"
                    label={{value: "Time Slot (Start Time - End Time)", position: 'insideBottom', offset: -25}}
                  />
                  <YAxis 
                    axisLine={false} 
                    name="Time Slot"
                    tickLine={false} 
                    tick={{ fill: '#9ca3af', fontSize: 12 }} 
                    label={{ value: 'Avg. Weekly Bundles Sold', angle: -90, position: 'insideBottomLeft'}}
                  />
                  <Tooltip 
                    labelFormatter={(label) => `Time Slot :  ${label}`}
                  />
                  <Bar 
                    dataKey="weekly_average" 
                    fill="#8b5cf6" 
                    radius={[4, 4, 0, 0]} 
                    name="Average. Weekly Bundles Sold"/>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-gray-500 text-sm mt-4 italic text-center">
              Best performing times to post bundles for maximum engagement.
            </p>
          </div>

        </div>
      </div>
    </div>
  );
}
