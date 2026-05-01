import { cn } from '@/lib/utils'

interface Props {
  label: string
  score: number
}

function colorClass(score: number) {
  if (score >= 80) return 'text-green-400'
  if (score >= 50) return 'text-yellow-400'
  return 'text-red-400'
}

export function SubScoreBadge({ label, score }: Props) {
  return (
    <div className="flex flex-col items-center gap-0.5 px-3 py-2 rounded-lg bg-muted/40 border border-border/40">
      <span className={cn('text-lg font-bold', colorClass(score))}>{score}</span>
      <span className="text-xs text-muted-foreground">{label}</span>
    </div>
  )
}
