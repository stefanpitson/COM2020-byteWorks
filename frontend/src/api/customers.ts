import api from "./axiosConfig";
import type { Customer } from "../types";

export const getCustomerProfile = async(): Promise<Customer> => {
  const response = await api.get<Customer>("/customers/profile");

  return response.data;
};
