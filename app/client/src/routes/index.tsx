import { useQuery } from '@tanstack/react-query'
import { Stethoscope, RefreshCw, Loader2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { HealthGauge } from '@/components/HealthGauge'
import { SubScoreBadge } from '@/components/SubScoreBadge'
import { IssueCard } from '@/components/IssueCard'
import { getLatestScan, triggerScan } from '@/lib/api'
import { useMachineStore } from '@/store/machine'
import { useState } from 'react'
import type { Issue } from '@/types'

const DEMO_MACHINE_ID = 'demo'

interface ScanData {
  health_score: number
  score_performance: number
  score_storage: number
  score_security: number
  score_stability: number
  scanned_at: string
  issues: Issue[]
  aiExplanation?: string
}

export function DashboardRoute() {
  const { machineId } = useMachineStore()
  const activeId = machineId ?? DEMO_MACHINE_ID
  const [scanning, setScanning] = useState(false)

  const { data: scan, isLoading, error, refetch } = useQuery<ScanData | null>({
    queryKey: ['scan', activeId],
    queryFn: () => getLatestScan(activeId) as Promise<ScanData | null>,
    retry: false,
    staleTime: 30_000,
  })

  const handleScan = async () => {
    setScanning(true)
    try { await triggerScan(activeId) } catch { /* ignore */ }
    finally {
      setScanning(false)
      void refetch()
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground text-sm">System health overview</p>
        </div>
        <div className="flex items-center gap-3">
          {scan && (
            <span className="text-xs text-muted-foreground">
              Last scan: {new Date(scan.scanned_at).toLocaleTimeString()}
            </span>
          )}
          <Button size="sm" onClick={handleScan} disabled={scanning}>
            {scanning ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <RefreshCw className="h-4 w-4 mr-2" />}
            Scan Now
          </Button>
        </div>
      </div>

      {isLoading ? (
        <DashboardSkeleton />
      ) : error || !scan ? (
        <EmptyState onScan={handleScan} scanning={scanning} />
      ) : (
        <ScanDisplay scan={scan} machineId={activeId} />
      )}
    </div>
  )
}

function ScanDisplay({ scan, machineId }: { scan: ScanData; machineId: string }) {
  return (
    <>
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col items-center gap-6 sm:flex-row sm:items-center">
            <HealthGauge score={scan.health_score ?? 0} size={180} />
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 flex-1">
              <SubScoreBadge label="Performance" score={scan.score_performance ?? 0} />
              <SubScoreBadge label="Storage" score={scan.score_storage ?? 0} />
              <SubScoreBadge label="Security" score={scan.score_security ?? 0} />
              <SubScoreBadge label="Stability" score={scan.score_stability ?? 0} />
            </div>
          </div>
        </CardContent>
      </Card>

      {(scan.health_score ?? 100) < 70 && (
        <Card className="border-primary/30 bg-primary/5">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <Stethoscope className="h-4 w-4 text-primary" />
              AI Diagnosis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {scan.aiExplanation ?? 'Connect the agent and run a scan to get a personalized AI diagnosis of your system.'}
            </p>
          </CardContent>
        </Card>
      )}

      {scan.issues && scan.issues.length > 0 ? (
        <div className="space-y-3">
          <h2 className="text-base font-semibold text-foreground">Active Issues ({scan.issues.length})</h2>
          {scan.issues.map((issue: Issue) => (
            <IssueCard key={issue.id} issue={issue} machineId={machineId} />
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-muted-foreground text-sm">No active issues detected.</p>
          </CardContent>
        </Card>
      )}
    </>
  )
}

function DashboardSkeleton() {
  return (
    <div className="space-y-4">
      <Card><CardContent className="pt-6"><Skeleton className="h-48 w-full" /></CardContent></Card>
      <Skeleton className="h-24 w-full" />
      <Skeleton className="h-20 w-full" />
      <Skeleton className="h-20 w-full" />
    </div>
  )
}

function EmptyState({ onScan, scanning }: { onScan: () => void; scanning: boolean }) {
  return (
    <Card className="border-dashed">
      <CardContent className="py-16 flex flex-col items-center gap-4">
        <Stethoscope className="h-12 w-12 text-muted-foreground/40" />
        <div className="text-center">
          <p className="font-medium text-foreground">No scan data yet</p>
          <p className="text-muted-foreground text-sm mt-1">Run a scan to see your system health score and detected issues.</p>
        </div>
        <Button onClick={onScan} disabled={scanning}>
          {scanning ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <RefreshCw className="h-4 w-4 mr-2" />}
          Run First Scan
        </Button>
      </CardContent>
    </Card>
  )
}
