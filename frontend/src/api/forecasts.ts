import type { ForecastWeekData} from "../types";
import api from "./axiosConfig";


export async function getVendorForecasts(model: string): Promise<ForecastWeekData> {
    if (model === "moving average") {
        const response = await api.post<ForecastWeekData>("/forecast/moving-average", {}, { timeout: 15000 });
        return response.data;

    } else if (model === "linear regression") {
        const response = await api.post<ForecastWeekData>("/forecast/linear-regression", {}, { timeout: 15000 });
        return response.data;
    } else {
        const response = await api.post<ForecastWeekData>("/forecast/naive", {}, { timeout: 15000 });
        return response.data;
    }     
}