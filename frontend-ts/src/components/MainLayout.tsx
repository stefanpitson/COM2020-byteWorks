import { Outlet } from "react-router-dom";
import NavBar from "./NavBar";
import ProtectedRoute from "./ProtectedRoute";

export default function MainLayout() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* This stays constant on every page inside this layout */}
      <NavBar />

      {/* The 'Outlet' is where the specific page content (Home, Dashboard, etc.) will appear */}
      <main className="flex-grow ">
        <Outlet />
      </main>

      {/* You could also put a Footer here! */}
    </div>
  );
}
