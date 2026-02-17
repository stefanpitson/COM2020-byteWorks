// import axios from "./axiosConfig";
import type { Analytics} from "../types";
// import api from "./axiosConfig";



export async function getVendorAnalytics(): Promise<Analytics> {
  // const response = await api.get<Analytics>("/");
  const response = {
    data: {
      week_data: [
        {
          week_date: "2026-02-18",
          datapoints: [
            {
              bundle_name: "Pastry Bag",
              predicted: 9,
              no_show: 1,
              posted: 10,
              recommendation: "Post 8 bundles based on last Wed."
            },
            {
              bundle_name: "Sandwich Meal",
              predicted: 5,
              no_show: 0,
              posted: 5,
              recommendation: "Post 5 bundles based on last Wed."
            },
            {
              bundle_name: "Sushi Bag",
              predicted: 13,
              no_show: 2,
              posted: 15,
              recommendation: "Post 12 bundles based on last Thu."
            },
            {
              bundle_name: "Surplus Veg",
              predicted: 5,
              no_show: 1,
              posted: 6,
              recommendation: "Post 4 bundles based on last Thu."
            }
          ]
        }
      ]
    }
  };
  
  return response.data;
}