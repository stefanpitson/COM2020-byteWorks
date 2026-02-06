export interface User {
  user_id: number;
  email: string;
  role: string;
}

export interface Customer {
  customer_id?: number;
  name: string;
  post_code: string;
  store_credit: number;
  carbon_saved: number;
  rating?: number;
}

export interface Vendor {
  vendor_id?: number;
  name: string;
  street: string;
  city: string;
  post_code: string;
  opening_hours: string;
  phone_number: string;
  carbon_saved: number;
  validated: boolean;
  photo: string;
}
