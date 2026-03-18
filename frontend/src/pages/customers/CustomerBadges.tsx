import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { getOwnedBadges, getUnownedBadges, getLeaderboard } from "../../api/customers";
import type { Badge, LeaderboardEntry } from "../../types";

const getBadgeStyling = (metric: string, threshold: number, isOwned: boolean) => {
  if (!isOwned) {
    return { bg: "bg-gray-100", text: "text-gray-400", border: "border-gray-200", icon: "🔒" };
  }

  if (metric === "streak_count" && threshold >= 30) {
    return { bg: "bg-[hsl(var(--accent)/0.2)]", text: "text-[hsl(var(--accent))]", border: "border-[hsl(var(--accent)/0.4)]", icon: "👑" };
  }
  if (metric === "streak_count") {
    return { bg: "bg-[hsl(var(--accent)/0.15)]", text: "text-[hsl(var(--accent))]", border: "border-[hsl(var(--accent)/0.3)]", icon: "🔥" };
  }

  if (metric === "bundles_saved" && threshold >= 20) {
    return { bg: "bg-[hsl(var(--primary-dark)/0.15)]", text: "text-[hsl(var(--primary-dark))]", border: "border-[hsl(var(--primary-dark)/0.4)]", icon: "🏆" };
  }
  if (metric === "bundles_saved") {
    return { bg: "bg-[hsl(var(--primary-dark)/0.1)]", text: "text-[hsl(var(--primary-dark))]", border: "border-[hsl(var(--primary-dark)/0.2)]", icon: "🛍️" };
  }

  if (metric === "food_saved" && threshold >= 10) {
    return { bg: "bg-[hsl(var(--primary)/0.2)]", text: "text-[hsl(var(--primary-dark))]", border: "border-[hsl(var(--primary)/0.4)]", icon: "🏅" };
  }
  if (metric === "food_saved") {
    return { bg: "bg-[hsl(var(--primary)/0.1)]", text: "text-[hsl(var(--primary))]", border: "border-[hsl(var(--primary)/0.2)]", icon: "🍲" };
  }

  if (metric === "carbon_saved") {
    return { bg: "bg-green-100", text: "text-green-700", border: "border-green-300", icon: "🌍" };
  }

  if (metric === "money_saved") {
    return { bg: "bg-yellow-100", text: "text-yellow-700", border: "border-yellow-300", icon: "💷" };
  }
  
  return { bg: "bg-white", text: "text-[hsl(var(--text-main))]", border: "border-gray-200", icon: "⭐" };
};

function metricFormat(metric: string) {
  if (metric === "streak_count") return "Days";
  if (metric === "bundles_saved") return "Bundles";
  if (metric === "food_saved") return "kg";
  if (metric === "carbon_saved") return "kg CO₂";
  if (metric === "money_saved") return "£ Saved";
  return metric.replace("_", " ");
}

export default function CustomerBadges() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<"badges" | "leaderboard">("badges");
  
  const [ownedBadges, setOwnedBadges] = useState<Badge[]>([]);
  const [unownedBadges, setUnownedBadges] = useState<Badge[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const [owned, unowned, board] = await Promise.all([
          getOwnedBadges(),
          getUnownedBadges(),
          getLeaderboard()
        ]);
        
        setOwnedBadges(owned.badges);
        setUnownedBadges(unowned.badges);
        setLeaderboard(board.entries);
      } catch (error) {
        console.error("Failed to load data", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

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
                  : "See how much food our top rescuers are saving."}
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
        {isLoading ? (
            <div className="flex justify-center items-center py-20">
                <div className="animate-spin w-10 h-10 border-4 border-[hsl(var(--primary))] border-t-transparent rounded-full"></div>
            </div>
        ) : (
            <>
            {activeTab === "badges" && (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {ownedBadges.map((badge) => {
                const style = getBadgeStyling(badge.metric, badge.threshold, true);
                return (
                    <div key={`owned-${badge.badge_id}`} className="bg-white rounded-3xl p-6 border border-white/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-lg transition-all hover:-translate-y-1 flex flex-col items-center text-center group cursor-default">
                        <div className={`w-24 h-24 rounded-full border-4 flex items-center justify-center text-4xl mb-5 transition-transform duration-300 group-hover:scale-110 shadow-inner ${style.bg} ${style.border}`}>
                            <span className="drop-shadow-sm">{style.icon}</span>
                        </div>
                        <h3 className="text-lg font-extrabold text-[hsl(var(--primary-dark))] mb-2 leading-tight">{badge.title}</h3>
                        <p className="text-sm text-[hsl(var(--text-main))] leading-relaxed mb-6 flex-grow opacity-90">{badge.description}</p>
                        <div className={`text-[10px] font-bold uppercase tracking-wider px-3 py-1.5 rounded-xl bg-opacity-50 ${style.bg} ${style.text}`}>
                            Target: {badge.threshold} {metricFormat(badge.metric)}
                        </div>
                    </div>
                );
                })}

                {unownedBadges.map((badge) => {
                const style = getBadgeStyling(badge.metric, badge.threshold, false);
                return (
                    <div key={`unowned-${badge.badge_id}`} className="bg-white/40 backdrop-blur-sm rounded-3xl p-6 border-2 border-dashed border-[hsl(var(--text-main)/0.2)] flex flex-col items-center text-center opacity-70">
                        <div className={`w-24 h-24 rounded-full border-4 flex items-center justify-center text-4xl mb-5 shadow-inner ${style.bg} ${style.border}`}>
                            <span className="opacity-50 grayscale">{getBadgeStyling(badge.metric, badge.threshold, true).icon}</span>
                        </div>
                        <h3 className="text-lg font-bold text-gray-500 mb-2 leading-tight">{badge.title}</h3>
                        <p className="text-sm text-gray-400 leading-relaxed mb-6 flex-grow">{badge.description}</p>
                        <div className={`text-[10px] font-bold uppercase tracking-wider px-3 py-1.5 rounded-xl bg-gray-100 text-gray-400`}>
                            Goal: {badge.threshold} {metricFormat(badge.metric)}
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
                    <span className="font-bold text-[hsl(var(--text-main))] uppercase tracking-wider text-xs text-right">Food Saved</span>
                </div>
                
                <div className="divide-y divide-gray-50">
                    {leaderboard.map((user) => {
                    const isTopThree = user.rank <= 3;
                    const isMe = user.is_you;
                    
                    let rankStyling = "text-[hsl(var(--text-main))] font-bold";
                    if (user.rank === 1) rankStyling = "text-yellow-500 font-extrabold text-lg";
                    if (user.rank === 2) rankStyling = "text-gray-400 font-extrabold text-lg";
                    if (user.rank === 3) rankStyling = "text-amber-700 font-extrabold text-lg";

                    const displayName = user.name.split("#")[0];

                    return (
                        <div key={user.customer_id} className={`px-6 py-5 flex items-center justify-between transition-colors ${isMe ? "bg-[hsl(var(--accent)/0.05)]" : "hover:bg-gray-50/50"}`}>
                        <div className="flex items-center gap-4">
                            <div className={`w-8 text-center ${rankStyling}`}>
                            {user.rank === 1 ? "👑" : user.rank === 2 ? "🥈" : user.rank === 3 ? "🥉" : `#${user.rank}`}
                            </div>
                            <div className="flex items-center gap-3">
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${isMe ? "bg-[hsl(var(--accent))] text-white" : isTopThree ? "bg-[hsl(var(--primary))] text-white" : "bg-[hsl(var(--primary)/0.1)] text-[hsl(var(--primary-dark))]"}`}>
                                {displayName.charAt(0)}
                            </div>
                            <span className={`font-bold ${isMe ? "text-[hsl(var(--accent))]" : "text-[hsl(var(--primary-dark))]"}`}>
                                {displayName} {isMe && "(You)"}
                            </span>
                            </div>
                        </div>
                        
                        <div className="text-right">
                            <span className="font-extrabold text-[hsl(var(--primary))] text-lg">
                            {user.food_saved.toFixed(1)}
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
            </>
        )}

      </div>
    </div>
  );
}