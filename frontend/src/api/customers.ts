import api from "./axiosConfig";
import type { Customer } from "../types";

export const getCustomerProfile = async () => {
  const response = await api.get<Customer>("/customers/profile");

  return response.data;
};

export const getCustomerStreak = async () => {
  const response = await api.get<number>("/customers/streak");

  return response.data;
}
