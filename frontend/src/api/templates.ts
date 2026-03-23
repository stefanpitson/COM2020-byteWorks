import api from "./axiosConfig";
import type { Template } from "../types";

interface TemplateListResponse {
  total_count: number;
  templates: Template[];
}

export interface CreateTemplatePayload {
  title: string;
  description: string;
  cost: number;
  estimated_value: number;
  weight: number;
  meat_percent: number;
  carb_percent: number;
  veg_percent: number;
  is_vegan: boolean;
  is_vegetarian: boolean;
  allergen_titles: string[]; 
}

export async function getVendorTemplates(vendorId: number): Promise<TemplateListResponse> {
  const response = await api.get<TemplateListResponse>(
    `/templates/vendor/${vendorId}`
  );
  return response.data;
}

export async function getTemplateBundleCount(templateId: number): Promise<number> {
  const response = await api.get<number>(
    `/templates/count/${templateId}`
  );
  return response.data ?? 0;
}

export async function getTemplateById(templateId: number): Promise<Template> {
  const response = await api.get<Template>(
    `/templates/${templateId}`
  );
  return response.data;
}

export async function createTemplate(payload: CreateTemplatePayload): Promise<Template> {
  const response = await api.post<Template>("/templates", payload);
  return response.data;
}

export async function deleteTemplate(templateId: number) {
  const response = await api.delete(`/templates/${templateId}`)
  return response.data
}

export const uploadTemplateImage = async (templateId: number, imageData: FormData) => {
  const response = await api.post(`/templates/upload-image/${templateId}`, imageData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};