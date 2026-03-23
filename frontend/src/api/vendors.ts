import api from "./axiosConfig";
import type { Vendor } from "../types";

export const getVendorProfile = async (): Promise<Vendor> => {
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
  const res = await api.get<Vendor>(`/vendors/${vendorId}`);
  return res.data;
}

export interface VendorUpdatePayload {
  user: {
    email?: string;
    old_password?: string;
    new_password?: string;
  };
  vendor: {
    name?: string;
    post_code?: string;
    street?: string;
    city?: string;
    phone_number?: string;
    opening_hours?: string;
  };
}

export const updateVendorProfile = async (data: VendorUpdatePayload) => {
  const response = await api.patch("/vendors/profile", data);
  return response.data;
};

export const uploadImage = async (
  image: FormData
) => {
  const response = await api.post("/vendors/upload-image", image, {
    headers: {
      "Content-Type": "multipart/form-data", 
    },
  });

  return response.data;
}