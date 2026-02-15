import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import CustomerHome from "./pages/customers/CustomerHome";
import VendorDashboard from "./pages/vendors/vendorDashboard";
import "./App.css";
import MainLayout from "./components/MainLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import CustomerSignUp from "./pages/customers/CustomerSignUp";
import VendorSignUp from "./pages/vendors/vendorSignUp";
import VendorSettings from "./pages/vendors/vendorSettings";
import TemplateDetails from "./pages/vendors/templateDetails";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />

        <Route path="/vendor/signup" element={<VendorSignUp />} />
        <Route path="/customer/signup" element={<CustomerSignUp />} />

        <Route path="/vendor/template" element={<TemplateDetails />} />

        {/* Applies the navbar */}
        <Route element={<MainLayout />}>
          {/* Only Customers allowed */}
          <Route element={<ProtectedRoute allowedRole="customer" />}>
            <Route path="/customer/home" element={<CustomerHome />} />

            <Route path="/customer/settings" element={<CustomerSignUp />} />
          </Route>

          {/* Only Vendors allowed */}
          <Route element={<ProtectedRoute allowedRole="vendor" />}>
            <Route path="/vendor/dashboard" element={<VendorDashboard />} />#
            <Route path="/vendor/settings" element={<VendorSettings />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

