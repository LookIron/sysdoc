import { useState } from 'react'
import { Loader2, Search, Trash2 } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import type { StartupItem } from '@/types'

const CATEGORY_CONFIG = {
  essential:  { label: '🔒 Essential',  className: 'bg-slate-800 text-slate-300 border-slate-600',  tooltip: 'Required for system operation' },
  useful:     { label: '✅ Useful',      className: 'bg-green-900/50 text-green-400 border-green-700', tooltip: 'Safe to keep, minimal impact' },
  slow:       { label: '⚠️ Slow',        className: 'bg-yellow-900/50 text-yellow-400 border-yellow-700', tooltip: 'Slows boot — consider disabling' },
  ghost:      { label: '👻 Ghost',       className: 'bg-red-900/50 text-red-400 border-red-700',     tooltip: 'Program uninstalled but startup entry remains' },
  unknown:    { label: '❓ Unknown',     className: 'bg-orange-900/50 text-orange-400 border-orange-700', tooltip: 'Not recognized — research before disabling' },
  suspicious: { label: '🔴 Suspicious', className: 'bg-red-950/80 text-red-300 border-red-800',     tooltip: 'Unusual behavior detected' },
} as const

type Category = keyof typeof CATEGORY_CONFIG

interface ConfirmState {
  item: StartupItem
  action: 'toggle' | 'remove'
}

interface Props {
  items: StartupItem[]
  machineId: string
  onFix: (itemId: string, fixCode: string, params: Record<string, string>) => Promise<void>
  loading?: boolean
}

export function StartupList({ items, machineId: _machineId, onFix, loading }: Props) {
  const [search, setSearch] = useState('')
  const [activeCategories, setActiveCategories] = useState<Set<Category>>(new Set())
  const [showDisabled, setShowDisabled] = useState(false)
  const [confirm, setConfirm] = useState<ConfirmState | null>(null)
  const [fixingId, setFixingId] = useState<string | null>(null)

  const filtered = items.filter(item => {
    if (!showDisabled && !item.enabled) return false
    if (search && !item.name.toLowerCase().includes(search.toLowerCase())) return false
    if (activeCategories.size > 0 && !activeCategories.has(item.category as Category)) return false
    return true
  })

  const toggleCategory = (cat: Category) => {
    setActiveCategories(prev => {
      const next = new Set(prev)
      next.has(cat) ? next.delete(cat) : next.add(cat)
      return next
    })
  }

  const handleConfirm = async () => {
    if (!confirm) return
    const { item, action } = confirm
    setConfirm(null)
    setFixingId(item.id)
    try {
      const fixCode = action === 'remove' ? 'FIX_P04_GHOST' : 'FIX_STARTUP_TOGGLE'
      await onFix(item.id, fixCode, { name: item.name, source: item.source, action: action === 'remove' ? 'remove' : 'disable' })
    } finally {
      setFixingId(null)
    }
  }

  if (loading) {
    return <div className="space-y-2">{[1, 2, 3, 4, 5].map(i => <Skeleton key={i} className="h-12 w-full" />)}</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            className="w-full pl-9 pr-3 h-9 rounded-md bg-muted border border-border text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            placeholder="Search by name…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {(Object.keys(CATEGORY_CONFIG) as Category[]).map(cat => (
            <button
              key={cat}
              onClick={() => toggleCategory(cat)}
              className={cn(
                'text-xs px-2 py-1 rounded border transition-colors',
                activeCategories.has(cat)
                  ? CATEGORY_CONFIG[cat].className
                  : 'border-border text-muted-foreground hover:border-primary/50'
              )}
            >
              {CATEGORY_CONFIG[cat].label}
            </button>
          ))}
          <button
            onClick={() => setShowDisabled(!showDisabled)}
            className={cn(
              'text-xs px-2 py-1 rounded border transition-colors',
              showDisabled ? 'border-primary text-primary' : 'border-border text-muted-foreground'
            )}
          >
            Show disabled
          </button>
        </div>
      </div>

      <div className="rounded-lg border border-border overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-muted/30">
              <th className="text-left px-4 py-2.5 font-medium text-muted-foreground">Name</th>
              <th className="text-left px-3 py-2.5 font-medium text-muted-foreground hidden md:table-cell">Category</th>
              <th className="text-left px-3 py-2.5 font-medium text-muted-foreground hidden lg:table-cell">Path</th>
              <th className="text-left px-3 py-2.5 font-medium text-muted-foreground hidden sm:table-cell">Boot impact</th>
              <th className="text-right px-4 py-2.5 font-medium text-muted-foreground">Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-muted-foreground">
                  No startup items match the current filters.
                </td>
              </tr>
            ) : filtered.map(item => {
              const catConfig = CATEGORY_CONFIG[item.category as Category] ?? CATEGORY_CONFIG.unknown
              const isFixing = fixingId === item.id
              const isEssential = item.category === 'essential'
              const isGhost = item.category === 'ghost'

              return (
                <tr key={item.id} className={cn('border-b border-border/50 hover:bg-muted/20 transition-colors', !item.enabled && 'opacity-50')}>
                  <td className="px-4 py-3">
                    <span className={cn('font-medium text-foreground', !item.enabled && 'line-through')}>{item.name}</span>
                  </td>
                  <td className="px-3 py-3 hidden md:table-cell">
                    <span title={catConfig.tooltip}>
                      <Badge variant="outline" className={cn('text-xs', catConfig.className)}>{catConfig.label}</Badge>
                    </span>
                  </td>
                  <td className="px-3 py-3 hidden lg:table-cell">
                    <span
                      className="text-xs text-muted-foreground truncate max-w-[200px] block"
                      title={item.path ?? undefined}
                    >
                      {item.path ? item.path.substring(item.path.lastIndexOf('/') + 1) || item.path : '—'}
                    </span>
                  </td>
                  <td className="px-3 py-3 hidden sm:table-cell">
                    <span className="text-xs text-muted-foreground">
                      {item.boot_impact_s == null ? 'Unknown' : item.boot_impact_s === 0 ? 'None' : `+${item.boot_impact_s}s`}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    {isFixing ? (
                      <Loader2 className="h-4 w-4 animate-spin text-muted-foreground inline" />
                    ) : isGhost ? (
                      <Button
                        size="sm"
                        variant="destructive"
                        className="h-7 text-xs"
                        onClick={() => setConfirm({ item, action: 'remove' })}
                      >
                        <Trash2 className="h-3 w-3 mr-1" /> Remove
                      </Button>
                    ) : !isEssential ? (
                      <Button
                        size="sm"
                        variant={item.enabled ? 'secondary' : 'outline'}
                        className="h-7 text-xs"
                        onClick={() => setConfirm({ item, action: 'toggle' })}
                      >
                        {item.enabled ? 'Disable' : 'Enable'}
                      </Button>
                    ) : null}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {confirm && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-card border border-border rounded-lg p-6 max-w-md w-full space-y-4 shadow-2xl">
            <h3 className="font-semibold text-foreground">
              {confirm.action === 'remove' ? 'Remove startup entry?' : `${confirm.item.enabled ? 'Disable' : 'Enable'} startup item?`}
            </h3>
            <p className="text-sm text-muted-foreground">
              {confirm.action === 'remove'
                ? `This will remove the ghost startup entry for "${confirm.item.name}". The original program is already uninstalled.`
                : `This will ${confirm.item.enabled ? 'disable' : 'enable'} "${confirm.item.name}" from running at startup.`
              }
            </p>
            <div className="flex gap-3 justify-end">
              <Button variant="outline" size="sm" onClick={() => setConfirm(null)}>Cancel</Button>
              <Button
                size="sm"
                variant={confirm.action === 'remove' ? 'destructive' : 'default'}
                onClick={handleConfirm}
              >
                Confirm
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
