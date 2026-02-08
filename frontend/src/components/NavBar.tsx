import { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";

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
        <div ref={menuRef}>
          <button
            onClick={() => setSettingsOpen(!isSettingsOpen)}
            className="relative bg-gray-400 p-2 rounded-xl hover:bg-gray-300 transition-colors">
            <svg
              // 1. We use 'className' for size and color (w-6 h-6 is standard icon size)
              className="w-6 h-6 fill-current" 
              viewBox="0 0 32 32"
              xmlns="http://www.w3.org/2000/svg"
            >
              <g>
                <g>
                  <path d="M16,14c-3.8598633,0-7-3.140625-7-7s3.1401367-7,7-7s7,3.140625,7,7S19.8598633,14,16,14z M16,2c-2.7568359,0-5,2.2431641-5,5s2.2431641,5,5,5s5-2.2431641,5-5S18.7568359,2,16,2z" />
                </g>
                <g>
                  <path d="M27,32c-0.5522461,0-1-0.4472656-1-1v-6.1152344c0-3.828125-3.1142578-6.9423828-6.9423828-6.9423828h-6.1152344C9.1142578,17.9423828,6,21.0566406,6,24.8847656V31c0,0.5527344-0.4477539,1-1,1s-1-0.4472656-1-1v-6.1152344c0-4.9306641,4.0117188-8.9423828,8.9423828-8.9423828h6.1152344C23.9882813,15.9423828,28,19.9541016,28,24.8847656V31C28,31.5527344,27.5522461,32,27,32z" />
                </g>
              </g>
            </svg>
            {isSettingsOpen && (
              <div className="absolute left-0 mt-2 w-max bg-white border rounded-xl shadow-lg z-50">
                <ul className="py-2 text-gray-700 text-left">
                  <li className="px-4 py-2 hover:bg-gray-100 cursor-pointer flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.325.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 0 1 1.37.49l1.296 2.247a1.125 1.125 0 0 1-.26 1.431l-1.003.827c-.293.241-.438.613-.43.992a7.723 7.723 0 0 1 0 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 0 1-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.47 6.47 0 0 1-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.019-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 0 1-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 0 1-1.369-.49l-1.297-2.247a1.125 1.125 0 0 1 .26-1.431l1.004-.827c.292-.24.437-.613.43-.991a6.932 6.932 0 0 1 0-.255c.007-.38-.138-.751-.43-.992l-1.004-.827a1.125 1.125 0 0 1-.26-1.43l1.297-2.247a1.125 1.125 0 0 1 1.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.086.22-.128.332-.183.582-.495.644-.869l.214-1.28Z" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                    </svg>  
                    Settings
                  </li>
                  <hr></hr>
                  <li 
                  onClick={handleLogout}
                  className="px-4 py-2 hover:bg-gray-100 cursor-pointer text-red-600 flex items-center">
                    <svg 
                    className="size-6 fill-current"
                    id="Layer_1" 
                    data-name="Layer 1" 
                    xmlns="http://www.w3.org/2000/svg" 
                    viewBox="-4 -4 24 24">
                      <title>Trade_Icons</title>
                      <polygon points="10.95 15.84 -0.05 15.84 -0.05 0.17 10.95 0.17 10.95 4.05 9.95 4.05 9.95 1.17 0.95 1.17 0.95 14.84 9.95 14.84 9.95 12.01 10.95 12.01 10.95 15.84"/>
                      <rect x="5" y="8" width="6" height="1"/>
                      <polygon points="11 5.96 15.4 8.5 11 11.04 11 5.96"/>
                    </svg>
                    Logout
                  </li>
                </ul>
              </div>
            )}
          </button>
        </div>
        <div>
          <Link to="/" className="text-red-700">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="black"
              className="w-8 h-8"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"
              />
            </svg>
          </Link>
        </div>
      </nav>
    </header>
  );
}
