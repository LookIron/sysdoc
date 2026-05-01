import { useQuery } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { SeverityBadge } from '@/components/SeverityBadge'
import { IssueCard } from '@/components/IssueCard'
import { getIssues } from '@/lib/api'
import { useMachineStore } from '@/store/machine'
import type { Issue } from '@/types'

const SEVERITY_ORDER = { critical: 0, high: 1, medium: 2, low: 3 }

export function IssuesRoute() {
  const { machineId } = useMachineStore()
  const activeId = machineId ?? 'demo'

  const { data: issues, isLoading } = useQuery({
    queryKey: ['issues', activeId],
    queryFn: () => getIssues(activeId),
    retry: false,
  })

  const sorted = [...(issues ?? [])].sort(
    (a, b) => SEVERITY_ORDER[a.severity] - SEVERITY_ORDER[b.severity]
  )

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Issues</h1>
        <p className="text-muted-foreground text-sm">Detected problems and recommended fixes</p>
      </div>

      {isLoading ? (
        <div className="space-y-3">{[1, 2, 3].map(i => <Skeleton key={i} className="h-16 w-full" />)}</div>
      ) : sorted.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground text-sm">No active issues found.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {sorted.map((issue: Issue) => (
            <IssueCard key={issue.id} issue={issue} machineId={activeId} />
          ))}
        </div>
      )}

      {sorted.length > 0 && (
        <div className="flex gap-3 text-xs text-muted-foreground pt-2">
          {(['critical', 'high', 'medium', 'low'] as const).map(s => (
            <div key={s} className="flex items-center gap-1.5">
              <SeverityBadge severity={s} />
              <span>{sorted.filter((i: Issue) => i.severity === s).length}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
