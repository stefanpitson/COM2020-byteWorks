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

export interface Template {
  template_id: number;
  title: string;
  description: string;
  cost: number;
  meat_percent: number;
  carb_percent: number;
  veg_percent: number;
  carbon_saved: number;
  is_vegan: boolean;
  is_vegetarian: boolean;
  allergens: {
    allergen_id: number;
    title: string;
  }[];
}
