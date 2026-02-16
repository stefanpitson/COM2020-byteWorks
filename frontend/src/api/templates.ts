import axios from "./axiosConfig";
import type { Template } from "../types";

interface TemplateListResponse {
  total_count: number;
  templates: Template[];
}

export async function getVendorTemplates(vendorId: number): Promise<TemplateListResponse> {
  const response = await axios.get<TemplateListResponse>(
    `/templates/vendor/${vendorId}`
  );
  return response.data;
}

export async function getTemplateBundleCount(templateId: number): Promise<number> {
  const response = await axios.get<number>(
    `/templates/count/${templateId}`
  );
  return response.data ?? 0;
}

export async function getTemplateById(templateId: number): Promise<Template> {
  const response = await axios.get<Template>(
    `/templates/${templateId}`
  );
  return response.data;
}