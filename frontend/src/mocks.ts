import type { Customer, User, Vendor } from "./types";

export const mockCustomer: Customer = {
  customer_id: 1,
  name: "Monty",
  post_code: "EX4 4DE",
  store_credit: 100,
  carbon_saved: 0,
  rating: 5.0,
};

export const mockVendor: Vendor = {
  vendor_id: 1,
  name: "Best Bakes",
  street: "One street",
  city: "Exeter",
  post_code: "EX4 4DE",
  phone_number: "0000000000001",
  opening_hours: "Mon-Fri 8:00 - 18:00",
  carbon_saved: 0,
  validated: true
};

export const mockUserCus: User = {
  user_id: 1,
  email: "Monty@Gmail.com",
  role: "customer",
};

export const mockUserVen: User = {
  user_id: 2,
  email: "Bakes@Gmail.com",
  role: "vendor",
};

export const mockToken = "mock-jwt-token-12345";
