import type { ForecastWeekData} from "../types";
import api from "./axiosConfig";



export async function getSellThrough() {
  const response = await api.post<ForecastWeekData>("analytics/sell_through_proportions");
  return response.data;
}
