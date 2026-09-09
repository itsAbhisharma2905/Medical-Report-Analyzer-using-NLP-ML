import type { AnalyzeResponse } from "../types/api";

const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();

/** The deployed FastAPI service is the default; local environments can override it. */
export const API_BASE_URL = (configuredBaseUrl || "https://medical-report-analyzer-api.vercel.app").replace(/\/$/, "");

export class ApiError extends Error {
  readonly status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export const apiUrl = (path: string): string => {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function detailFromPayload(payload: unknown): string | undefined {
  if (!isRecord(payload)) return undefined;
  if (typeof payload.detail === "string") return payload.detail;
  if (Array.isArray(payload.detail)) return "The server rejected the request. Please check the submitted information.";
  return undefined;
}

function friendlyHttpMessage(status: number, detail?: string): string {
  const normalized = detail?.toLowerCase() ?? "";
  if (normalized.includes("ocr") || normalized.includes("scanned") || normalized.includes("image-only")) {
    return "This PDF appears to be scanned or image-based. The deployed version currently supports text-based PDFs. Please upload a text-based PDF.";
  }
  if (status === 400) return detail || "Please check the submitted information and try again.";
  if (status === 413) return "This file is too large. Please upload a PDF smaller than 25 MB.";
  if (status === 422) return detail || "The report could not be processed. Please check the file and try again.";
  if (status >= 500) return "The analysis service is temporarily unavailable. Please try again shortly.";
  return detail || "Unable to analyze the report. Please check your input and try again.";
}

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, init);
  } catch {
    throw new ApiError("Unable to reach the analysis service. Please check your connection and try again.");
  }

  const payload: unknown = await response.json().catch(() => undefined);
  if (!response.ok) {
    throw new ApiError(friendlyHttpMessage(response.status, detailFromPayload(payload)), response.status);
  }
  return payload as T;
}

function validateAnalysisResponse(payload: unknown): AnalyzeResponse {
  if (!isRecord(payload) || typeof payload.summary !== "string" || !isRecord(payload.entities) || !isRecord(payload.patient_details) || !isRecord(payload.metadata)) {
    throw new ApiError("The analysis service returned an unexpected response. Please try again.");
  }
  for (const value of Object.values(payload.entities)) {
    if (!Array.isArray(value)) throw new ApiError("The analysis service returned an unexpected response. Please try again.");
  }
  return payload as unknown as AnalyzeResponse;
}

export async function analyzeText(text: string): Promise<AnalyzeResponse> {
  const payload = await requestJson<unknown>(apiUrl("/analyze"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, persist: false }),
  });
  return validateAnalysisResponse(payload);
}

export async function uploadReport(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const payload = await requestJson<unknown>(apiUrl("/upload-report"), {
    method: "POST",
    body: formData,
  });
  return validateAnalysisResponse(payload);
}

export async function checkHealth(): Promise<boolean> {
  const payload = await requestJson<{ status?: string }>(apiUrl("/health"));
  return payload.status === "ok";
}
