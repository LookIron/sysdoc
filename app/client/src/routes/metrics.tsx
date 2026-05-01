import { useQuery } from '@tanstack/react-query'
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { getMetrics } from '@/lib/api'
import { useMachineStore } from '@/store/machine'
import type { Metric } from '@/types'

function fmt(m: Metric) {
  return {
    ...m,
    time: new Date(m.recordedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
  }
}

export function MetricsRoute() {
  const { machineId } = useMachineStore()
  const activeId = machineId ?? 'demo'

  const { data: raw, isLoading } = useQuery({
    queryKey: ['metrics', activeId],
    queryFn: () => getMetrics(activeId, 1),
    refetchInterval: 5_000,
    retry: false,
  })

  const metrics = (raw ?? []).map(fmt).slice(-60)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Metrics</h1>
        <p className="text-muted-foreground text-sm">Real-time performance — updates every 5 seconds</p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-48 w-full rounded-lg" />)}
        </div>
      ) : metrics.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground text-sm">No metrics yet — connect the agent to start streaming data.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <MetricCard title="CPU">
            <LineChart data={metrics}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="time" tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} />
              <YAxis tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} domain={[0, 100]} />
              <Tooltip contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 6 }} />
              <Legend />
              <Line type="monotone" dataKey="cpuUsagePct" name="Usage %" stroke="#a78bfa" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="cpuTempC" name="Temp °C" stroke="#f97316" dot={false} strokeWidth={2} />
            </LineChart>
          </MetricCard>

          <MetricCard title="RAM">
            <AreaChart data={metrics}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="time" tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} />
              <YAxis tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} domain={[0, 100]} />
              <Tooltip contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 6 }} />
              <Legend />
              <Area type="monotone" dataKey="ramUsagePct" name="Usage %" stroke="#22c55e" fill="#22c55e33" strokeWidth={2} />
            </AreaChart>
          </MetricCard>

          <MetricCard title="Disk I/O (MB/s)">
            <BarChart data={metrics}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="time" tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} />
              <YAxis tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} />
              <Tooltip contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 6 }} />
              <Legend />
              <Bar dataKey="diskReadMbps" name="Read" fill="#60a5fa" />
              <Bar dataKey="diskWriteMbps" name="Write" fill="#f472b6" />
            </BarChart>
          </MetricCard>

          <MetricCard title="Network (MB/s)">
            <LineChart data={metrics}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="time" tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} />
              <YAxis tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} />
              <Tooltip contentStyle={{ background: 'hsl(var(--card))', border: '1px solid hsl(var(--border))', borderRadius: 6 }} />
              <Legend />
              <Line type="monotone" dataKey="netUploadMbps" name="Upload" stroke="#34d399" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="netDownloadMbps" name="Download" stroke="#818cf8" dot={false} strokeWidth={2} />
            </LineChart>
          </MetricCard>
        </div>
      )}
    </div>
  )
}

function MetricCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={160}>
          {children as React.ReactElement}
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
