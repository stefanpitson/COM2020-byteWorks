import api from "./axiosConfig";

export interface CreateBundlePayload {
  template_id: number;
  amount: number;
}

export const createBundle = async (
    data: CreateBundlePayload
) => {
  const payload: CreateBundlePayload = {
    template_id: data.template_id,
    amount: data.amount
  };

  const response = await api.post("/bundles/create", payload);
  return response.data;
};