import api from "./axiosConfig";
import type { Customer, Streak } from "../types";

export const getCustomerProfile = async(): Promise<Customer> => {
  const response = await api.get<Customer>("/customers/profile");

  return response.data;
};

export const getCustomerStreak = async () => {
  const response = await api.get<Streak>("/customers/streak");

  return response.data;
}

export interface CustomerUpdatePayload {
  user: {
    email?: string;
    old_password?: string;
    new_password?: string;
  };
  customer: {
    name?: string;
    post_code?: string;
  };
}

export const updateCustomerProfile = async (data: CustomerUpdatePayload) => {
  const response = await api.patch("/customers/profile", data);
  return response.data;
};