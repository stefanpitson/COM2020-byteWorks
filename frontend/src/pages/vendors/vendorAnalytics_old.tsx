import { useEffect, useState } from "react";
import { getVendorAnalytics } from "../../api/analytics";
import type { Analytics } from "../../types";

export default function VendorAnalytics() {
//   const [stats, setStats] = useState<Analytics | null>(null);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     const fetchAnalytics = async () => {
//       try {
//         const data = await getVendorAnalytics();
//         setStats(data);
//       } catch (error) {
//         console.error("Failed to load analytics", error);
//       } finally {
//         setLoading(false);
//       }
//     };
//     fetchAnalytics();
//   }, []);

//   if (loading) return <div className="p-20 text-center">Loading Analytics...</div>;

//   return (
//     <div className="min-h-screen bg-pattern p-8 md:p-16 flex justify-center">
//       <div className="max-w-6xl w-full flex flex-col md:flex-row gap-12">
        
//         {/* LEFT COLUMN: Lifetime Totals */}
//         <div className="md:w-1/3 space-y-12 border-r border-gray-400 pr-12">
//           <div>
//             <h1 className="text-6xl font-serif text-green-800">£{stats?.id.toLocaleString()}</h1>
//             <p className="text-xl text-gray-700 mt-2">made</p>
//           </div>

//           <div>
//             <h2 className="text-5xl font-serif text-green-800">{stats?.id}kg</h2>
//             <p className="text-xl text-gray-700 mt-2">saved from going to waste</p>
//           </div>

//           <div>
//             <h2 className="text-5xl font-serif text-green-800">{stats?.id} kgCO2e</h2>
//             <p className="text-xl text-gray-700 mt-2">saved from being wasted</p>
//           </div>
//         </div>

//         {/* RIGHT COLUMN: Weekly Performance & Prediction */}
//         <div className="md:w-2/3 space-y-8">
//           {/* Prediction Box */}
//           <div className="bg-white/50 border border-black p-8 rounded-lg text-center">
//             <p className="text-lg italic text-gray-800">
//               based on your previous performance, you are predicted to sell 
//               <span className="font-bold"> {stats?.id} bundles </span> this week
//             </p>
//           </div>

//           {/* Weekly History List */}
//           {/* <div className="space-y-4">
//             {stats.weekly_history.map((week: any, index: number) => (
//               <div key={index} className="flex items-center gap-6">
//                 <span className="text-sm font-mono text-gray-600 w-32 shrink-0">
//                   {week.start_date}-{week.end_date}
//                 </span>
//                 <div className="flex-1 bg-white/50 border border-black p-6 rounded-lg flex justify-between items-center">
//                   <span className="font-medium">
//                     {week.sold} bundles sold ({Math.round((week.sold / week.posted) * 100)}%)
//                   </span>
//                   <span className="text-gray-600">{week.posted} bundles posted</span>
//                   <span className="text-red-600 font-medium">{week.no_shows} no-shows</span>
//                 </div>
//               </div>
//             ))}
//           </div> */}
//         </div>
//       </div>
//     </div>
//   );
}