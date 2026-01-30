import { Navigate, Outlet } from "react-router-dom";

export default function ProtectedRoute({
  allowedRole,
}: {
  allowedRole: string;
}) {
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");

  // If there's no token, they aren't logged in
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (role !== allowedRole) {
    return <Navigate to="/" />;
  }

  return <Outlet />;
}
