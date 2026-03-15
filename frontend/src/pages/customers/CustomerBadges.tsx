import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

interface Badge {
  badge_id: number;
  title: string;
  description: string;
  metric: string;
  threshold: number;
}

interface LeaderboardEntry {
  id: number;
  name: string;
  co2_saved: number;
}

const MOCK_BADGES: Badge[] = [
  { badge_id: 1, title: "Spark", description: "Started your first streak!", metric: "streak_count", threshold: 1 },
  { badge_id: 2, title: "Heating Up", description: "Maintained a 3-day streak.", metric: "streak_count", threshold: 3 },
  { badge_id: 3, title: "On Fire", description: "A perfect week of rescuing food!", metric: "streak_count", threshold: 7 },
  { badge_id: 4, title: "Unstoppable", description: "Two straight weeks of rescues.", metric: "streak_count", threshold: 14 },
  { badge_id: 5, title: "Monthly Master", description: "An entire month of daily impact.", metric: "streak_count", threshold: 30 },
  { badge_id: 6, title: "Legendary", description: "60 straight days! You are a rescuing machine.", metric: "streak_count", threshold: 60 },
  { badge_id: 7, title: "First Rescue", description: "Rescued your very first bundle.", metric: "bundles_saved", threshold: 1 },
  { badge_id: 8, title: "High Five", description: "Rescued 5 bundles from going to waste.", metric: "bundles_saved", threshold: 5 },
  { badge_id: 9, title: "Perfect Ten", description: "Hit the double digits with 10 rescued bundles.", metric: "bundles_saved", threshold: 10 },
  { badge_id: 10, title: "Bundle Boss", description: "Rescued 15 bundles.", metric: "bundles_saved", threshold: 15 },
  { badge_id: 11, title: "Bundle Champion", description: "An incredible 20 bundles rescued!", metric: "bundles_saved", threshold: 20 },
  { badge_id: 12, title: "Making a Dent", description: "Saved 1kg of food from the bin.", metric: "food_saved", threshold: 1 },
  { badge_id: 13, title: "Heavy Lifter", description: "Saved 2kg of delicious food.", metric: "food_saved", threshold: 2 },
  { badge_id: 14, title: "Triple Threat", description: "Saved 3kg of food.", metric: "food_saved", threshold: 3 },
  { badge_id: 15, title: "Eco Champion", description: "Saved 4kg of food.", metric: "food_saved", threshold: 4 },
  { badge_id: 16, title: "Waste Warrior", description: "A massive 5kg of food saved!", metric: "food_saved", threshold: 5 }
];

const MOCK_LEADERBOARD: LeaderboardEntry[] = [
  { id: 1, name: "Sarah J.", co2_saved: 142.5 },
  { id: 2, name: "Alex M.", co2_saved: 128.0 },
  { id: 3, name: "David K.", co2_saved: 115.2 },
  { id: 4, name: "Emma W.", co2_saved: 98.7 },
  { id: 5, name: "You", co2_saved: 85.4 },
  { id: 6, name: "Chris P.", co2_saved: 72.1 },
  { id: 7, name: "Jessica T.", co2_saved: 64.9 },
];

const getBadgeStyling = (metric: string, threshold: number) => {
  if (metric === "streak_count" && threshold >= 30) {
    return { bg: "bg-[hsl(var(--accent)/0.2)]", text: "text-[hsl(var(--accent))]", border: "border-[hsl(var(--accent)/0.4)]", icon: "👑" };
  }
  if (metric === "streak_count") {
    return { bg: "bg-[hsl(var(--accent)/0.15)]", text: "text-[hsl(var(--accent))]", border: "border-[hsl(var(--accent)/0.3)]", icon: "🔥" };
  }
  if (metric === "bundles_saved") {
    return { bg: "bg-[hsl(var(--primary-dark)/0.1)]", text: "text-[hsl(var(--primary-dark))]", border: "border-[hsl(var(--primary-dark)/0.3)]", icon: "🛍️" };
  }
  if (metric === "food_saved") {
    return { bg: "bg-[hsl(var(--primary)/0.1)]", text: "text-[hsl(var(--primary))]", border: "border-[hsl(var(--primary)/0.2)]", icon: "🍲" };
  }
  
  return { bg: "bg-white", text: "text-[hsl(var(--text-main))]", border: "border-gray-200", icon: "⭐" };
};

export default function CustomerBadges() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<"badges" | "leaderboard">("badges");

  return (
    <div className="min-h-screen bg-[hsl(var(--background))] pb-20 font-['Quicksand']">
      
      <div className="bg-white/60 backdrop-blur-md border-b border-white/50 pt-12 pb-24 px-6 relative overflow-hidden">
        <div className="max-w-5xl mx-auto relative z-10">
          <button 
            onClick={() => navigate(-1)}
            className="text-sm font-bold text-[hsl(var(--text-main))] hover:text-[hsl(var(--accent))] transition-colors mb-6 flex items-center gap-2"
          >
            ← Back to Dashboard
          </button>
          
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <h1 className="text-4xl md:text-5xl font-extrabold text-[hsl(var(--primary-dark))] tracking-tight">
                {activeTab === "badges" ? "My Badges" : "Impact Leaderboard"}
              </h1>
              <p className="text-[hsl(var(--text-main))] mt-2 text-lg opacity-80">
                {activeTab === "badges" 
                  ? "Track your impact and milestones." 
                  : "See how much CO₂ our top rescuers are saving."}
              </p>
            </div>

            <div className="flex bg-white/50 p-1.5 rounded-2xl border border-white backdrop-blur-sm w-fit shadow-sm">
              <button
                onClick={() => setActiveTab("badges")}
                className={`px-6 py-2.5 rounded-xl font-bold transition-all duration-200 ${
                  activeTab === "badges"
                    ? "bg-[hsl(var(--primary))] text-white shadow-md"
                    : "text-[hsl(var(--text-main))] hover:bg-white/60"
                }`}
              >
                Badges
              </button>
              <button
                onClick={() => setActiveTab("leaderboard")}
                className={`px-6 py-2.5 rounded-xl font-bold transition-all duration-200 flex items-center gap-2 ${
                  activeTab === "leaderboard"
                    ? "bg-[hsl(var(--primary))] text-white shadow-md"
                    : "text-[hsl(var(--text-main))] hover:bg-white/60"
                }`}
              >
                Leaderboard 🌍
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 -mt-8 relative z-20">
        
        {activeTab === "badges" && (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {MOCK_BADGES.map((badge) => {
              const style = getBadgeStyling(badge.metric, badge.threshold);
              
              return (
                <div 
                  key={badge.badge_id} 
                  className="bg-white rounded-3xl p-6 border border-white/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-lg transition-all hover:-translate-y-1 flex flex-col items-center text-center group cursor-default"
                >
                  <div className={`w-24 h-24 rounded-full border-4 flex items-center justify-center text-4xl mb-5 transition-transform duration-300 group-hover:scale-110 shadow-inner ${style.bg} ${style.border}`}>
                    <span className="drop-shadow-sm">{style.icon}</span>
                  </div>
                  
                  <h3 className="text-lg font-extrabold text-[hsl(var(--primary-dark))] mb-2 leading-tight">
                    {badge.title}
                  </h3>
                  
                  <p className="text-sm text-[hsl(var(--text-main))] leading-relaxed mb-6 flex-grow opacity-90">
                    {badge.description}
                  </p>
                  
                  <div className={`text-[10px] font-bold uppercase tracking-wider px-3 py-1.5 rounded-xl bg-opacity-50 ${style.bg} ${style.text}`}>
                    Target: {badge.threshold} {metricFormat(badge.metric)}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {activeTab === "leaderboard" && (
          <div className="max-w-3xl mx-auto">
            <div className="bg-white rounded-3xl border border-white/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] overflow-hidden">
              <div className="bg-[hsl(var(--primary)/0.05)] px-6 py-4 border-b border-gray-100 flex justify-between items-center">
                <span className="font-bold text-[hsl(var(--text-main))] uppercase tracking-wider text-xs">Rank & Rescuer</span>
                <span className="font-bold text-[hsl(var(--text-main))] uppercase tracking-wider text-xs text-right">CO₂ Saved</span>
              </div>
              
              <div className="divide-y divide-gray-50">
                {MOCK_LEADERBOARD.map((user, index) => {
                  const isTopThree = index < 3;
                  const isMe = user.name === "You";
                  
                  let rankStyling = "text-[hsl(var(--text-main))] font-bold";
                  if (index === 0) rankStyling = "text-yellow-500 font-extrabold text-lg";
                  if (index === 1) rankStyling = "text-gray-400 font-extrabold text-lg";
                  if (index === 2) rankStyling = "text-amber-700 font-extrabold text-lg";

                  return (
                    <div 
                      key={user.id} 
                      className={`px-6 py-5 flex items-center justify-between transition-colors ${
                        isMe ? "bg-[hsl(var(--accent)/0.05)]" : "hover:bg-gray-50/50"
                      }`}
                    >
                      <div className="flex items-center gap-4">
                        <div className={`w-8 text-center ${rankStyling}`}>
                          {index === 0 ? "👑" : index === 1 ? "🥈" : index === 2 ? "🥉" : `#${index + 1}`}
                        </div>
                        <div className="flex items-center gap-3">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${
                            isMe 
                              ? "bg-[hsl(var(--accent))] text-white" 
                              : isTopThree 
                                ? "bg-[hsl(var(--primary))] text-white"
                                : "bg-[hsl(var(--primary)/0.1)] text-[hsl(var(--primary-dark))]"
                          }`}>
                            {user.name.charAt(0)}
                          </div>
                          <span className={`font-bold ${isMe ? "text-[hsl(var(--accent))]" : "text-[hsl(var(--primary-dark))]"}`}>
                            {user.name}
                          </span>
                        </div>
                      </div>
                      
                      <div className="text-right">
                        <span className="font-extrabold text-[hsl(var(--primary))] text-lg">
                          {user.co2_saved.toFixed(1)}
                        </span>
                        <span className="text-[hsl(var(--text-main))] text-sm font-medium ml-1">kg</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}

function metricFormat(metric: string) {
  if (metric === "streak_count") return "Days";
  if (metric === "bundles_saved") return "Bundles";
  if (metric === "food_saved") return "kg";
  return metric.replace("_", " ");
}