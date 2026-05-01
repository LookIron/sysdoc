interface Props {
  score: number
  size?: number
}

function scoreColor(score: number): string {
  if (score >= 80) return '#22c55e'
  if (score >= 50) return '#eab308'
  return '#ef4444'
}

export function HealthGauge({ score, size = 160 }: Props) {
  const r = (size - 16) / 2
  const cx = size / 2
  const cy = size / 2
  const circumference = Math.PI * r
  const fillLength = (score / 100) * circumference
  const color = scoreColor(score)

  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size / 2 + 16} viewBox={`0 0 ${size} ${size / 2 + 16}`}>
        <path
          d={`M 8 ${cy} A ${r} ${r} 0 0 1 ${size - 8} ${cy}`}
          fill="none"
          stroke="hsl(var(--muted))"
          strokeWidth={12}
          strokeLinecap="round"
        />
        <path
          d={`M 8 ${cy} A ${r} ${r} 0 0 1 ${size - 8} ${cy}`}
          fill="none"
          stroke={color}
          strokeWidth={12}
          strokeLinecap="round"
          strokeDasharray={`${fillLength} ${circumference}`}
          style={{ transition: 'stroke-dasharray 0.6s ease' }}
        />
        <text x={cx} y={cy} textAnchor="middle" dominantBaseline="middle" fill={color} fontSize={size * 0.22} fontWeight="700">
          {score}
        </text>
      </svg>
      <span className="text-xs text-muted-foreground uppercase tracking-wide">Health Score</span>
    </div>
  )
}
