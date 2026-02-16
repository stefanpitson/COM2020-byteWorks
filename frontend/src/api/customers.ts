import api from "./axiosConfig";
import type { Customer, Streak } from "../types";

export const getCustomerProfile = async () => {
  const response = await api.get<Customer>("/customers/profile");

  return response.data;
};

export const getCustomerStreak = async () => {
  const response = await api.get<Streak>("/customers/streak");

  return response.data;
}