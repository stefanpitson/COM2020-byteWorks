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


export interface DeleteBundlePayload {
  template_id: number
  amount: number
}

export const deleteBundle = async (
  data: DeleteBundlePayload
) => {
  const payload: DeleteBundlePayload = {
    template_id: data.template_id,
    amount: data.amount
  };
  
  const response = await api.post("/bundles/delete", payload)
  return response.data
};