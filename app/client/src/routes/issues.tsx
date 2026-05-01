import { createFileRoute } from '@tanstack/react-router'
import { AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export const Route = createFileRoute('/issues')({
  component: IssuesPage,
})

function IssuesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Issues</h1>
        <p className="text-muted-foreground">Detected problems and recommended fixes</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-muted-foreground text-base">
            <AlertTriangle className="h-4 w-4" />
            Active Issues
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm">No issues detected. Run a scan to check your system.</p>
        </CardContent>
      </Card>
    </div>
  )
}
