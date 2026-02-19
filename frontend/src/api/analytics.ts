import type { Analytics} from "../types";
import api from "./axiosConfig";

const MOCK_ANALYTICS: Analytics = {
  week_data: [
    {
      week_date: "2026-02-18",
      datapoints: [
        {
          bundle_name: "Pastry Bag",
          predicted_sales: 9,
          no_show: 1,
          chance_of_no_show: 0.1,
          day: "Wednesday",
          start_time: "08:00:00",
          end_time: "10:00:00",
            confidence: 0.624,
          recommendation: "Strong demand. Consider adding 2 more bags tomorrow.",
          rationale: "Sales have been consistently high for pastries on Wednesday mornings."
        },
        {
          bundle_name: "Sandwich Meal",
          predicted_sales: 5,
          no_show: 0,
          chance_of_no_show: 0.0,
          day: "Wednesday",
          start_time: "12:00:00",
          end_time: "14:00:00",
          confidence: 0.624,
          recommendation: "Perfect sell-through. Maintain current levels.",
          rationale: "Mid-day sandwich demand matches your current supply perfectly."
        }
      ]
    },
    {
      week_date: "2026-02-11",
      datapoints: [
        {
          bundle_name: "Hot Meal Box",
          predicted_sales: 18,
          no_show: 1,
          chance_of_no_show: 0.05,
          day: "Wednesday",
          start_time: "17:00:00",
          end_time: "19:00:00",
          confidence: 0.624,
          recommendation: "High demand! Great performance this week.",
          rationale: "Evening hot meals are seeing a significant uptick in interest."
        },
        {
          bundle_name: "Artisan Bread",
          predicted_sales: 12,
          no_show: 0,
          chance_of_no_show: 0.0,
          day: "Wednesday",
          start_time: "09:00:00",
          end_time: "11:00:00",
          confidence: 0.624,
          recommendation: "Sold out quickly. You could increase volume.",
          rationale: "Artisan bread is a local favorite with zero no-shows recently."
        }
      ]
    }
  ]
};

export async function getVendorAnalytics(): Promise<Analytics> {
  try {
    const response = await api.get<Analytics>("/forecast/naive");
    return response.data;
  } catch (error) {
    console.warn("API Analytics call failed. Falling back to mock data.", error);
    return MOCK_ANALYTICS;
  }
}