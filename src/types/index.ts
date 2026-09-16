/**
 * Shared TypeScript interfaces for LumieTL frontend.
 */

// ── Translation ──────────────────────────────────────────────────────

export interface TranslationResult {
  result_image_base64: string
  duration: number
}

// ── Batch ────────────────────────────────────────────────────────────

export type FileStatus = 'pending' | 'processing' | 'done' | 'error' | 'cancelled'

export interface BatchFileInfo {
  filename: string
  status: FileStatus
  duration: number
  error: string
  output_path: string | null
}

export interface BatchTask {
  task_id: string
  source_lang: string
  target_lang: string
  engine: string
  cancelled: boolean
  created_at: string
  total: number
  done: number
  success: number
  errors: number
  is_complete: boolean
  files: BatchFileInfo[]
}

// ── History ──────────────────────────────────────────────────────────

export interface HistoryEntry {
  id: number
  timestamp: string
  input_filename: string
  output_path: string | null
  source_lang: string
  target_lang: string
  engine: string
  duration: number
  success: boolean
  error: string
}

export interface HistoryResponse {
  items: HistoryEntry[]
  total: number
}

// ── Models ───────────────────────────────────────────────────────────

export interface ModelInfo {
  name: string
  filename: string
  size_mb: number
  url?: string
  downloaded: boolean
  sha256_ok: boolean
}

export interface ModelStatus {
  ready: boolean
  model_dir?: string
  models: ModelInfo[]
}

export interface ModelDownloadProgress {
  status: 'downloading' | 'done' | 'error'
  progress: number
  total: number
  current_model: string
  percent?: number
  overall_percent?: number
  completed_count?: number
  total_models?: number
  error: string | null
}

// ── Settings ─────────────────────────────────────────────────────────

export interface Settings {
  default_source_lang: string
  default_target_lang: string
  default_engine: string
  output_dir: string
  gpu_enabled: boolean
  available_source_langs: Record<string, string>
  available_target_langs: Record<string, string>
  available_engines: Record<string, string>
}

export interface ApiKeyStatus {
  deepl_set: boolean
  openai_set: boolean
}

// ── App ──────────────────────────────────────────────────────────────

export interface AppInfo {
  name: string
  version: string
}

// ── Toast ────────────────────────────────────────────────────────────

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
  id: number
  message: string
  type: ToastType
  duration: number
}
