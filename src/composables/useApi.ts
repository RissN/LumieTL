/**
 * Axios wrapper for LumieTL API calls.
 */
import axios, { type AxiosInstance, type AxiosError } from 'axios'

const api: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 300_000, // 5 minutes for large translations
  headers: {
    'Accept': 'application/json',
  },
})

// Response interceptor — normalise errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    const message =
      error.response?.data?.detail ??
      error.message ??
      'An unknown error occurred'
    return Promise.reject(new Error(message))
  },
)

export function useApi() {
  return { api }
}

export default api
