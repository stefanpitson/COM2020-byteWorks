import { useState, useEffect, useRef} from "react";
import { Link } from "react-router-dom";


export default function NavBar() {
  const [isSettingsOpen, setSettingsOpen] = useState<boolean>(false);
  const menuRef = useRef<HTMLDivElement>(null); // Create a reference to the menu

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      
      if (isSettingsOpen && menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setSettingsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isSettingsOpen]);


  return (
    <header>
      <nav className="fixed top-0 left-0 w-full flex justify-between items-center bg-gray-200 p-2 shadow-md shadow-black/5">
        <div>
          <Link  to="/" className="text-green-700">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-8 h-8">
              <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
            </svg>

          </Link>
        </div>
        <div>
          <button onClick={() => setSettingsOpen(!isSettingsOpen)} className="relative bg-gray-400 p-2 rounded-xl hover:bg-gray-300 transition-colors">
            Options
            {isSettingsOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-white border rounded-xl shadow-lg z-50">
              <ul className="py-2 text-gray-700">
                <li className="px-4 py-2 hover:bg-gray-100 cursor-pointer">Settings</li>
                <li className="px-4 py-2 hover:bg-gray-100 cursor-pointer text-red-600">Logout</li>
              </ul>
            </div>
          )}
          </button>
        </div>
      </nav>
    </header>
  );
}