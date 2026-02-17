import { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import logo from "../assets/logo.jpg"; 
import { getCustomerProfile, getCustomerStreak } from "../api/customers"
import type { Streak } from "../types"

const SettingsIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5 mr-2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.212 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

const ExitIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5 mr-2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" />
  </svg>
);

const UserIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
    <path strokeLinecap="round" strokeLinejoin="round" d="M17.982 18.725A7.488 7.488 0 0012 15.75a7.488 7.488 0 00-5.982 2.975m11.963 0a9 9 0 10-11.963 0m11.963 0A8.966 8.966 0 0112 21a8.966 8.966 0 01-5.982-2.275M15 9.75a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

const BagIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5 mr-2">
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 10.5V6a3.75 3.75 0 10-7.5 0v4.5m11.356-1.993l1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 01-1.12-1.243l1.264-12A1.125 1.125 0 015.513 7.5h12.974c.576 0 1.059.435 1.119 1.007zM8.625 10.5a.375.375 0 11-.75 0 .375.375 0 01.75 0zm7.5 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
  </svg>
);

const FireIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-fire" viewBox="0 0 16 16">
    <path d="M8 16c3.314 0 6-2 6-5.5 0-1.5-.5-4-2.5-6 .25 1.5-1.25 2-1.25 2C11 4 9 .5 6 0c.357 2 .5 4-2 6-1.25 1-2 2.729-2 4.5C2 14 4.686 16 8 16m0-1c-1.657 0-3-1-3-2.75 0-.75.25-2 1.25-3C6.125 10 7 10.5 7 10.5c-.375-1.25.5-3.25 2-3.5-.179 1-.25 2 1 3 .625.5 1 1.364 1 2.25C11 14 9.657 15 8 15"/>
  </svg>
);

export default function NavBar() {
  const navigate = useNavigate();
  const [isSettingsOpen, setSettingsOpen] = useState<boolean>(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const [storeCredit, setStoreCredit] = useState<number | null>(null);
  const [streak, setStreak] = useState<Streak | null>(null);

  const role = localStorage.getItem('role');
  const homeLink = role === 'vendor' ? '/vendor/dashboard' : '/customer/home';


  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        isSettingsOpen &&
        menuRef.current &&
        !menuRef.current.contains(event.target as Node)
      ) {
        setSettingsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isSettingsOpen]);

  useEffect(() => {
    async function fetchData() {
      if (role !== "customer") return;

      try {
        const profile = await getCustomerProfile();
        setStoreCredit(profile.store_credit);

        const streakResponse = await getCustomerStreak();
        setStreak(streakResponse);
      } catch (err) {
        console.error("Failed to load navbar data", err);
      }
    }
    fetchData();
  }, [role]);

  function handleLogout() {
    localStorage.clear();
    navigate("/login");
  }

  const today = new Date().toISOString().slice(0, 10);
  const hasStreak = streak && streak.count > 0;
  const isExtendedToday = streak ? streak.last === today : false;
  const isGrey = !hasStreak || !isExtendedToday;
  const displayCount = streak ? streak.count : 0;

  return (
    <nav className="fixed top-0 left-0 right-0 h-16 bg-white/90 backdrop-blur-md border-b border-gray-200 shadow-sm z-50 px-4 md:px-8 flex justify-between items-center transition-all">
      
      <Link to={homeLink} className="flex items-center gap-3 group">
        <div className="w-10 h-10 rounded-xl overflow-hidden shadow-md group-hover:shadow-lg transition-all border border-gray-100">
           <img 
             src={logo} 
             alt="ByteWork Logo" 
             className="w-full h-full object-cover"
             onError={(e) => {
               e.currentTarget.style.display = 'none';
               e.currentTarget.parentElement?.classList.add('bg-[hsl(158,48%,46%)]'); // Fallback Green
             }}
           />
        </div>
        <span className="font-extrabold text-xl tracking-tight text-gray-800">
          Byte<span className="text-[hsl(158,48%,46%)]">Work</span>
        </span>
      </Link>

      <div ref={menuRef} className="flex items-center gap-4">

        {role === "customer" && (
          <div
            className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm font-semibold ${
              isGrey
                ? "bg-gray-100 text-gray-400"
                : "bg-[hsl(34,92%,64%)]/10 text-[hsl(14,90%,60%)]"
            }`}
          >
            <FireIcon />
            <span>{displayCount} day streak</span>
          </div>
        )}

        {role === "customer" && storeCredit !== null && (
          <div
            className={`px-3 py-1 rounded-full text-sm font-semibold ${
              storeCredit === 0
                ? "bg-red-100 text-red-600"
                : "bg-[hsl(158,48%,46%)]/10 text-[hsl(158,48%,46%)]"
            }`}
          >
           Balance: £{storeCredit.toFixed(2)}
          </div>
        )}

        <button
          onClick={() => setSettingsOpen(!isSettingsOpen)}
          className={`
            p-2 rounded-full transition-all duration-200 border border-transparent
            ${isSettingsOpen 
              ? "bg-gray-100 ring-2 ring-[hsl(158,48%,46%)] ring-offset-2" 
              : "hover:bg-gray-100 hover:shadow-sm"}
          `}
        >
          <div className="text-gray-600">
            <UserIcon />
          </div>
        </button>

        {isSettingsOpen && (
          <div className="absolute right-0 top-full mt-3 w-48 bg-white border border-gray-100 rounded-2xl shadow-xl py-2 animate-in fade-in slide-in-from-top-2">
            <div className="px-4 py-2 border-b border-gray-100 mb-1">
              <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">Account</p>
            </div>
            
            <ul className="text-sm text-gray-700">
              <li>
                <button className="w-full text-left px-4 py-2.5 hover:bg-gray-50 hover:text-[hsl(158,48%,46%)] flex items-center transition-colors">
                  <SettingsIcon />
                  Settings
                </button>
              </li>
              <li>
                <Link
                  to={
                    localStorage.getItem("role") === "vendor"
                      ? "/vendor/reservations"
                      : "/customer/reservations"
                  }
                  className="w-full text-left px-4 py-2.5 hover:bg-gray-50 hover:text-[hsl(158,48%,46%)] flex items-center transition-colors"
                >
                  <BagIcon />
                  Reservations
                </Link>
              </li>
              <li>
                <button 
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-2.5 hover:bg-red-50 hover:text-red-600 flex items-center transition-colors"
                >
                  <ExitIcon />
                  Logout
                </button>
              </li>
            </ul>
          </div>
        )}
      </div>
    </nav>
  );
}