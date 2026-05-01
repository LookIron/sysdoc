export interface Machine {
  id: string
  machineId: string
  hostname: string
  osName: string
  osArch: string
  cpuModel: string
  cpuCores: number
  ramTotalGb: number
}

export interface Scan {
  id: string
  healthScore: number
  scorePerformance: number
  scoreStorage: number
  scoreSecurity: number
  scoreStability: number
  scannedAt: string
  issues: Issue[]
  aiExplanation?: string
}

export interface Issue {
  id: string
  issueCode: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  title: string
  description: string
  fixAvailable: boolean
  fixCommand?: string | null
  resolvedAt?: string | null
}

export interface Metric {
  recordedAt: string
  cpuUsagePct: number | null
  cpuTempC: number | null
  cpuFreqMhz: number | null
  ramUsagePct: number | null
  ramAvailableGb: number | null
  diskReadMbps: number | null
  diskWriteMbps: number | null
  diskUsagePct: number | null
  netUploadMbps: number | null
  netDownloadMbps: number | null
}

export interface DashboardData {
  machine: Machine
  scan: Scan | null
}

export interface ScanResult {
  scanId: string
  healthScore: number
  issuesDetected: number
}

export interface FixResult {
  fixId: string
  status: 'queued' | 'running' | 'success' | 'failed'
}

export interface StartupItem {
  name: string
  path: string | null
  enabled: boolean
  source: string
  category: 'essential' | 'useful' | 'ghost' | 'unknown' | 'suspicious'
}
