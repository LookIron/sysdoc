import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Zap } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { StartupList } from '@/components/StartupList'
import { getStartup, triggerFix } from '@/lib/api'
import { useMachineStore } from '@/store/machine'

export function StartupRoute() {
  const { machineId } = useMachineStore()
  const activeId = machineId ?? 'demo'
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['startup', activeId],
    queryFn: () => getStartup(activeId),
    retry: false,
  })

  const handleFix = async (itemId: string, fixCode: string, _params: Record<string, string>) => {
    await triggerFix(activeId, itemId, fixCode)
    void queryClient.invalidateQueries({ queryKey: ['startup', activeId] })
  }

  const items = data?.items ?? []
  const bootEstimate = data?.boot_time_estimate_s ?? 0
  const enabled = items.filter(i => i.enabled).length
  const ghosts = items.filter(i => i.category === 'ghost').length
  const suspicious = items.filter(i => i.category === 'suspicious').length

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Startup Intelligence</h1>
        <p className="text-muted-foreground text-sm">Manage programs that run at boot</p>
      </div>

      {isLoading ? (
        <Skeleton className="h-12 w-full rounded-lg" />
      ) : items.length > 0 ? (
        <Card>
          <CardContent className="py-3">
            <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <Zap className="h-4 w-4 text-yellow-400" />
                Boot estimate: ~{bootEstimate}s
              </span>
              <span>{enabled} items enabled</span>
              {ghosts > 0 && <span className="text-red-400">{ghosts} ghost{ghosts > 1 ? 's' : ''} found</span>}
              {suspicious > 0 && <span className="text-red-300">{suspicious} suspicious</span>}
            </div>
          </CardContent>
        </Card>
      ) : null}

      {isLoading ? (
        <div className="space-y-2">{[1, 2, 3].map(i => <Skeleton key={i} className="h-12 w-full" />)}</div>
      ) : items.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground text-sm">No startup data yet — connect the agent and run a scan.</p>
          </CardContent>
        </Card>
      ) : (
        <StartupList items={items} machineId={activeId} onFix={handleFix} />
      )}
    </div>
  )
}
