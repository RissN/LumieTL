export interface HistoryItem {
  id: number
  timestamp: string
  input_path: string
  output_path: string | null
  source_lang: string
  target_lang: string
  engine: string
  duration: number
  success: boolean
  error: string
}

export interface AppSettings {
  default_source_lang: string
  default_target_lang: string
  default_engine: string
  font_size: number
  output_dir: string
  gpu_enabled: boolean
}

export interface ApiKeysStatus {
  deepl_set: boolean
  openai_set: boolean
}

export interface ModelItem {
  key: string
  name: string
  description: string
  size_mb: number
  downloaded: boolean
  valid: boolean
}

export interface ModelsStatus {
  ready: boolean
  models: ModelItem[]
}
