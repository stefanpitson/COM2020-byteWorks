import api from "./axiosConfig";
import type { Vendor } from "../types";

export const getVendorProfile = async () => {
  const response = await api.get<Vendor>("/vendors/profile");

  return response.data;
};
