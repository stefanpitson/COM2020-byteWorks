import type { AnalyticsBestBundles, AnalyticsDiscountData, AnalyticSellThrough, AnalyticsPostingData, AnalyticsWaste } from "../types";
import api from "./axiosConfig";



export async function getSellThrough() {
  const response = await api.get<AnalyticSellThrough>("analytics/sell_through_proportions");
  return response.data;
}

export async function getWasteProxy() {
  const response = await api.get<AnalyticsWaste>("analytics/waste_proxy");
  return response.data;
}

export async function getPricingEffectiveness() {
  const response = await api.get<AnalyticsDiscountData>("analytics/pricing_effectiveness");
  return response.data;
}

export async function getPostingWindows() {
  const response = await api.post<AnalyticsPostingData>("analytics/posting_windows");
  return response.data;
}

export async function getBestSellers() {
  const response = await api.post<AnalyticsBestBundles>("analytics/bestsellers");
  return response.data;
}



