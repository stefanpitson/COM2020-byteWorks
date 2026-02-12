import { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import HomeIcon from "../assets/icons/home.svg?react";
import UserIcon from "../assets/icons/user.svg?react";
import SettingsIcon from "../assets/icons/settings.svg?react";
import ExitIcon from "../assets/icons/exit.svg?react";

export default function NavBar() {
  const navigate = useNavigate();
  const [isSettingsOpen, setSettingsOpen] = useState<boolean>(false);
  const menuRef = useRef<HTMLDivElement>(null); // Create a reference to the menu

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
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isSettingsOpen]);

  function handleLogout() {
    localStorage.clear();
    navigate("/login");
  }

  return (
    <header>
      <nav className="fixed top-0 right-0 w-full flex justify-between items-center bg-gray-200 p-2 shadow-md shadow-black/5">
        <div>
          <Link 
            to={localStorage.getItem('role') === 'vendor' ? '/vendor/dashboard' : '/customer/home'} 
            className="text-red-700"
          >
            <HomeIcon className="size-8"/>
          </Link>
        </div>
        <div ref={menuRef}>
          <button
            onClick={() => setSettingsOpen(!isSettingsOpen)}
            className="relative bg-gray-400 p-2 rounded-xl hover:bg-gray-300 transition-colors">
            <UserIcon className="size-6"/>
            {isSettingsOpen && (
              <div className="absolute right-0 mt-2 w-max bg-white border rounded-xl shadow-lg z-50">
                <ul className="py-2 text-gray-700 text-left">
                  <li className="px-4 py-2 hover:bg-gray-100 cursor-pointer flex items-left">
                    <SettingsIcon className="size-6"/>
                    Settings
                  </li>
                  <hr></hr>
                  <li 
                  onClick={handleLogout}
                  className="px-4 py-2 hover:bg-gray-100 cursor-pointer text-red-600 flex items-left">
                    <ExitIcon className="size-6" />
                    Logout
                  </li>
                </ul>
              </div>
            )}
          </button>
        </div>
      </nav>
    </header>
  );
}
