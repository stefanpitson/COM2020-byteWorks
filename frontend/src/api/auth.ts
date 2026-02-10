import api from "./axiosConfig";
import type { User, Customer, Vendor } from "../types";

// LOGIN

export interface LoginCredentialsPayload {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export const loginUser = async (credentials: LoginCredentialsPayload) => {
  const response = await api.post<LoginResponse>("/auth/login", credentials);

  return response.data;
};

// User

export interface UserSignupData extends Omit<User, "user_id"> {
  password: string;
}

// Customer

export type CustomerSignupData = Omit<
  Customer,
  "customer_id" | "store_credit" | "carbon_saved" | "rating"
>;

export interface RegisterCustomerPayload {
  user: UserSignupData;
  customer: CustomerSignupData;
}

export const registerCustomer = async (
  user: UserSignupData,
  customer: CustomerSignupData,
) => {
  const payload: RegisterCustomerPayload = {
    user: user,
    customer: customer,
  };

  const response = await api.post("/auth/register/customer", payload);
  return response.data;
};

// Vendor

export type VendorSignupData = Omit<
  Vendor,
  "vendor_id" | "carbon_saved" | "validated" | "photo"
>;

export interface RegisterVendorPayload {
  user: UserSignupData;
  vendor: VendorSignupData;
}

export const registerVendor = async (
  user: UserSignupData,
  vendor: VendorSignupData,
) => {
  const payload: RegisterVendorPayload = {
    user: user,
    vendor: vendor,
  };

  const response = await api.post("/auth/register/vendor", payload);
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
