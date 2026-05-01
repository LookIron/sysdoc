import { createRouter } from '@tanstack/react-router'
import { Route as rootRoute } from './routes/__root'
import { Route as IndexRoute } from './routes/index'
import { Route as IssuesRoute } from './routes/issues'
import { Route as MetricsRoute } from './routes/metrics'
import { Route as StartupRoute } from './routes/startup'

const routeTree = rootRoute.addChildren([
  IndexRoute,
  IssuesRoute,
  MetricsRoute,
  StartupRoute,
])

export const router = createRouter({ routeTree })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
