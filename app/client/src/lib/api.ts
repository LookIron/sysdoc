import type { DashboardData, Metric, Issue, ScanResult, FixResult, StartupItem } from '@/types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json() as Promise<T>
}

export async function getDashboard(machineId: string): Promise<DashboardData> {
  return json(`/api/v1/machines/${machineId}/dashboard`)
}

export async function getLatestScan(machineId: string) {
  return json(`/api/v1/machines/${machineId}/scans/latest`)
}

export async function getMetrics(machineId: string, hours = 1): Promise<Metric[]> {
  return json(`/api/v1/machines/${machineId}/metrics?hours=${hours}`)
}

export async function getIssues(machineId: string): Promise<Issue[]> {
  return json(`/api/v1/machines/${machineId}/issues`)
}

export async function triggerScan(machineId: string): Promise<ScanResult> {
  return json(`/api/v1/machines/${machineId}/scan`, { method: 'POST', body: '{}' })
}

export async function triggerFix(machineId: string, issueId: string, fixCode: string): Promise<FixResult> {
  return json(`/api/v1/machines/${machineId}/fix`, {
    method: 'POST',
    body: JSON.stringify({ issue_id: issueId, fix_code: fixCode }),
  })
}

export async function getStartup(machineId: string): Promise<{ items: StartupItem[]; boot_time_estimate_s: number }> {
  return json(`/api/v1/machines/${machineId}/startup`)
}
