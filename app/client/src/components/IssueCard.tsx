import { useState } from 'react'
import { ChevronDown, ChevronUp, Loader2, CheckCircle, XCircle } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { SeverityBadge } from './SeverityBadge'
import type { Issue } from '@/types'

interface Props {
  issue: Issue
  machineId: string
  onFix?: (issueId: string, fixCode: string) => Promise<void>
}

type FixState = 'idle' | 'loading' | 'success' | 'error'

export function IssueCard({ issue, onFix }: Props) {
  const [expanded, setExpanded] = useState(false)
  const [fixState, setFixState] = useState<FixState>('idle')

  const handleFix = async () => {
    if (!onFix || !issue.fixCommand) return
    setFixState('loading')
    try {
      await onFix(issue.id, issue.fixCommand)
      setFixState('success')
    } catch {
      setFixState('error')
    }
  }

  return (
    <Card className="border-border/60">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3 flex-1 min-w-0">
            <SeverityBadge severity={issue.severity} />
            <div className="flex-1 min-w-0">
              <p className="font-medium text-foreground text-sm">{issue.title}</p>
              {!expanded && (
                <p className="text-muted-foreground text-xs mt-0.5 line-clamp-1">{issue.description}</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {issue.fixAvailable && (
              <Button
                size="sm"
                variant="secondary"
                disabled={fixState !== 'idle'}
                onClick={handleFix}
                className="h-7 text-xs"
              >
                {fixState === 'loading' && <Loader2 className="h-3 w-3 animate-spin mr-1" />}
                {fixState === 'success' && <CheckCircle className="h-3 w-3 mr-1 text-green-400" />}
                {fixState === 'error' && <XCircle className="h-3 w-3 mr-1 text-red-400" />}
                {fixState === 'idle' ? 'Fix' : fixState === 'loading' ? 'Fixing…' : fixState === 'success' ? 'Done' : 'Failed'}
              </Button>
            )}
            <Button size="sm" variant="ghost" onClick={() => setExpanded(!expanded)} className="h-7 w-7 p-0">
              {expanded ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
            </Button>
          </div>
        </div>
        {expanded && (
          <div className="mt-3 pt-3 border-t border-border/50">
            <p className="text-sm text-muted-foreground leading-relaxed">{issue.description}</p>
            <div className="mt-2 flex items-center gap-2">
              <span className="text-xs text-muted-foreground/60 font-mono">Code: {issue.issueCode}</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
