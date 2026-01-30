import api from "./axiosConfig";
import type { User, Customer, Vendor } from '../types';

export interface LoginCredentialsPayload {
  email: string;
  password: string;
}

export interface LoginResponse {
    access_token: string;
    token_type: string;
    user: User
}

export const loginUser = async (credentials: LoginCredentialsPayload) => {
  const response = await api.post<LoginResponse>('/auth/login', credentials);
  
  return response.data;
};

export interface UserSignupData extends Omit<User, 'user_id'>{
  password: string;
};
export type CustomerSignupData = Omit<Customer, 'customer_id' | 'store_credit' | 'carbon_saved' | 'rating'>;

export interface RegisterCustomerPayload{
  user: UserSignupData
  customer: CustomerSignupData
}

export const registerCustomer = async(user: UserSignupData, customer: CustomerSignupData) => {

  const payload: RegisterCustomerPayload = {
    user: user,
    customer: customer
  };

  const response = await api.post('/auth/register/customer', payload);
  return response.data;
}



export interface RegisterVendorPayload{
  user: User
  password: string
  vendor: Vendor
}

export const registerVendor = async(user: User, password: string, vendor: Vendor) => {

  const payload: RegisterVendorPayload = {
    user: user,
    password: password,
    vendor: vendor
  };

  const response = await api.post('/auth/register/vendor', payload);
  return response.data;
}


