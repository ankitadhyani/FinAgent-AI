import axios from "axios";

export const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function getTransactions({ limit = 600, offset = 0, risk, type } = {}) {
  const params = {
    limit,
    offset,
  };

  if (risk && risk !== "ALL") {
    params.risk = risk;
  }

  if (type && type !== "ALL") {
    params.type = type;
  }

  const response = await axios.get(`${API_BASE}/transactions`, {
    params,
  });

  if (Array.isArray(response.data)) {
    return {
      items: response.data,
      total: response.data.length,
      limit,
      offset,
    };
  }

  return {
    items: Array.isArray(response.data?.items) ? response.data.items : [],
    total: Number(response.data?.total ?? 0),
    limit: Number(response.data?.limit ?? limit),
    offset: Number(response.data?.offset ?? offset),
  };
}

export async function getRiskConfig() {
  const response = await axios.get(`${API_BASE}/risk-config`);
  return response.data;
}

export async function analyzeTransaction(payload) {
  const response = await axios.post(`${API_BASE}/analyze`, payload);
  return response.data;
}

export async function getModelMetrics() {
  const response = await axios.get(`${API_BASE}/model-metrics`);
  return response.data;
}