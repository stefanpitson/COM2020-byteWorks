import api from "./axiosConfig";
import type { Customer } from "../types";

export const getCustomerProfile = async () => {
  const response = await api.get<Customer>("/customers/profile");

  return response.data;
};
