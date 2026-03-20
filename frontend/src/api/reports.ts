import api from "./axiosConfig";
import type { Report } from "../types"

export interface ReportListResponse {
    total_count: number;
    reports: Report[];
}

export const getReportList = async (): Promise<ReportListResponse> => {
    const response = await api.get<ReportListResponse>("/reports/list");
    return response.data;
};

export const submitReportResponse = async (reportId: number, responseText: string) => {
    const res = await api.post(`/reports/${reportId}/reply`, { response: responseText });
    return res.data;
};