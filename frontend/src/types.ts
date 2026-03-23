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
  photo?: string;
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

export interface ForecastDataPoint {
  bundle_name: string;
  predicted_sales: number;
  predicted_no_show: number;
  chance_of_no_show: number;
  confidence: number;
  recommendation: string[];
  rationale: string[];
}

export interface ForecastDayData {
  date: string; 
  datapoints: ForecastDataPoint[];
}

export interface ForecastWeekData {
week_date: string; 
day_datapoints: ForecastDayData[];
}

export interface AnalyticSellThrough {
  weekly_proportions: {
    collected: number;
    no_show: number;
    expired: number;
    week_start_date: string;
  };
  all_time_proportions: {
    collected: number;
    no_show: number;
    expired: number;
  }
}

// Price Effectiveness
export interface AnalyticsDiscountData{
  coordinates: AnalyticsDiscountCoordinate[];
}

export interface AnalyticsDiscountCoordinate{
  discount: number;
  sell_through: number;
}

// Posting Windows
export interface AnalyticsPostingWindow{
  posting_timeslot: string;
  weekly_average: number;
}

export interface AnalyticsPostingData{
  top_post_window: string;
  window_datapoints: AnalyticsPostingWindow[];
}

// Waste Proxy
export interface AnalyticsWaste {
total_waste_avoided: number;
average_bundle_weight: number;
}

// Best Sellers
export interface AnalyticsPopularBundle {
  bundle_title: string;
  weekly_average: number;
}

export interface AnalyticsBestBundles {
  top_bundle: string;
  bundle_datapoints: AnalyticsPopularBundle[];
}

export interface Report {
  report_id: number;
  title: string;
  complaint: string;
  response: string | null;
  responded: boolean;
  customer_id: number;
  vendor_id: number;
  date_made: string; 
  date_responded: string | null;
}

export interface Badge {
  badge_id: number;
  title: string;
  description: string;
  metric: string;
  threshold: number;
}

export interface BadgeList {
  total_count: number;
  badges: Badge[];
}

export interface LeaderboardEntry {
  customer_id: number;
  rank: number;
  name: string;
  food_saved: number;
  is_you: boolean;
}

export interface LeaderboardList {
  total_count: number;
  entries: LeaderboardEntry[];
}