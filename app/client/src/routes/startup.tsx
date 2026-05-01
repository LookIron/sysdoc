import { Zap } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function StartupRoute() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Startup Intelligence</h1>
        <p className="text-muted-foreground text-sm">Manage programs that run at boot</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-muted-foreground text-base">
            <Zap className="h-4 w-4" />
            Startup Programs
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm">Run a scan to analyze your startup programs. Full UI coming in issue #7.</p>
        </CardContent>
      </Card>
    </div>
  )
}
