import { createRootRoute, Link, Outlet } from '@tanstack/react-router'
import { Activity } from 'lucide-react'

export const Route = createRootRoute({
  component: RootLayout,
})

function RootLayout() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b border-border/40 bg-background/95 backdrop-blur sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-primary" />
            <span className="font-semibold text-foreground">SysDoc</span>
          </div>
          <nav className="flex items-center gap-1">
            {[
              { to: '/', label: 'Dashboard' },
              { to: '/issues', label: 'Issues' },
              { to: '/metrics', label: 'Metrics' },
              { to: '/startup', label: 'Startup' },
            ].map(({ to, label }) => (
              <Link
                key={to}
                to={to}
                className="px-3 py-1.5 rounded-md text-sm text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
                activeProps={{ className: 'px-3 py-1.5 rounded-md text-sm text-foreground bg-muted' }}
                activeOptions={{ exact: to === '/' }}
              >
                {label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
