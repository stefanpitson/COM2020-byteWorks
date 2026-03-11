import type { ForecastWeekData} from "../types";
import api from "./axiosConfig";


export async function getVendorAnalytics(): Promise<ForecastWeekData> {
  const response = await api.get<ForecastWeekData>("/forecast/naive", {});
  return response.data;
}