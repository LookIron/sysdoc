import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

const CONFIG = {
  critical: { label: 'Critical', className: 'bg-red-900/50 text-red-400 border-red-800' },
  high:     { label: 'High',     className: 'bg-orange-900/50 text-orange-400 border-orange-800' },
  medium:   { label: 'Medium',   className: 'bg-yellow-900/50 text-yellow-400 border-yellow-800' },
  low:      { label: 'Low',      className: 'bg-blue-900/50 text-blue-400 border-blue-800' },
} as const

interface Props {
  severity: keyof typeof CONFIG
}

export function SeverityBadge({ severity }: Props) {
  const { label, className } = CONFIG[severity] ?? CONFIG.low
  return <Badge variant="outline" className={cn(className)}>{label}</Badge>
}
