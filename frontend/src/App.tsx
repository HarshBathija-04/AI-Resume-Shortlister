import { useEffect } from 'react'
import { BrowserRouter, Route, Routes, useLocation } from 'react-router-dom'
import { Toaster } from 'sonner'
import { Layout } from './components/Layout'
import { HistoryPage } from './pages/History'
import { HomePage } from './pages/Home'
import { NotFoundPage } from './pages/NotFound'
import { RunPage } from './pages/RunPage'

function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => window.scrollTo(0, 0), [pathname])
  return null
}

export default function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="runs/:id" element={<RunPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
      <Toaster position="bottom-right" richColors closeButton />
    </BrowserRouter>
  )
}
