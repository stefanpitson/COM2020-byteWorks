import api from "./axiosConfig";
import type { Vendor } from "../types";

export const getVendorProfile = async () => {
  const response = await api.get<Vendor>("/vendors/profile");

  return response.data;
};

type HomeVendor = Vendor & {
  bundle_count: number;
  has_vegan: boolean;
  has_vegetarian: boolean;
};

interface VendorResponse {
  total_count: number;
  vendors: HomeVendor[];
}

export const getAllVendors = async (): Promise<VendorResponse> => {
  const response = await api.get<VendorResponse>("/vendors");
  return response.data;
};

export async function getVendorById(vendorId: number): Promise<Vendor> {
  const res = await api.get<VendorResponse>("/vendors");
  const vendor = res.data.vendors.find(
    (v) => v.vendor_id === vendorId
  );
  if (!vendor) throw new Error("Vendor not found");
  return vendor;
}
