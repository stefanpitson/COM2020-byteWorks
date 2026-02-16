import { Outlet } from "react-router-dom";
import NavBar from "./NavBar";

export default function Layout() {
  return (
    <div className="min-h-screen bg-[hsl(32,80%,96%)] font-sans">
      <NavBar />
      {/* pt-16 ensures content starts below the fixed navbar */}
      <main className="pt-16">
        <Outlet />
      </main>
    </div>
  );
}
