import { createFileRoute } from '@tanstack/react-router'
import { BarChart2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export const Route = createFileRoute('/metrics')({
  component: MetricsPage,
})

function MetricsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Metrics</h1>
        <p className="text-muted-foreground">Real-time system performance data</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-muted-foreground text-base">
            <BarChart2 className="h-4 w-4" />
            Performance Charts
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm">Connect the agent to start streaming metrics.</p>
        </CardContent>
      </Card>
    </div>
  )
}
