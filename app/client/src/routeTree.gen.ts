import { createRouter, createRootRoute, createRoute } from '@tanstack/react-router'
import { RootLayout } from './routes/__root'
import { DashboardRoute } from './routes/index'
import { IssuesRoute } from './routes/issues'
import { MetricsRoute } from './routes/metrics'
import { StartupRoute } from './routes/startup'

const rootRoute = createRootRoute({ component: RootLayout })

const indexRoute = createRoute({ getParentRoute: () => rootRoute, path: '/', component: DashboardRoute })
const issuesRoute = createRoute({ getParentRoute: () => rootRoute, path: '/issues', component: IssuesRoute })
const metricsRoute = createRoute({ getParentRoute: () => rootRoute, path: '/metrics', component: MetricsRoute })
const startupRoute = createRoute({ getParentRoute: () => rootRoute, path: '/startup', component: StartupRoute })

const routeTree = rootRoute.addChildren([indexRoute, issuesRoute, metricsRoute, startupRoute])

export const router = createRouter({ routeTree })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
