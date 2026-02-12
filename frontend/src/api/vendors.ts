import api from "./axiosConfig";
import type { Vendor } from "../types";

export const getVendorProfile = async () => {
  const response = await api.get<Vendor>("/vendors/profile");

  return response.data;
};

interface VendorResponse {
  total_count: number;
  vendors: Vendor[];
}

export const getAllVendors = async (): Promise<VendorResponse> => {
  const response = await api.get<VendorResponse>("/vendors");
  return response.data;
};
