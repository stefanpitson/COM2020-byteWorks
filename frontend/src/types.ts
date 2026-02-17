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
  total_revenue: number;
  carbon_saved: number;
  food_saved: number;
  validated: boolean;
  photo: string;
}

export interface Template {
  template_id: number;
  title: string;
  description: string;
  estimated_value:number;
  cost: number;
  meat_percent: number;
  carb_percent: number;
  veg_percent: number;
  carbon_saved: number;
  weight: number;
  is_vegan: boolean;
  is_vegetarian: boolean;
  vendor?: number;
  photo: string;
  allergens: {
    allergen_id: number;
    title: string;
  }[];
}

export interface Reservation {
  reservation_id: number;
  bundle_id: number;
  customer_id: number;
  time_created: string;
  code: number;
  status: string;
};

export interface VendorReservation {
  reservation_id: number;
  bundle_id: number;
  customer_id: number;
  time_created: string;
  status: string;
  code?: number; // vendor does not see real code initially
}

export interface Streak {
  count: number;
  last: string; 
}
export interface Analytics {
  id: number;
}
