import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig, type Plugin } from 'vite'

// Link previews (LinkedIn, Slack, X) need an absolute og:image URL. Vercel exposes the
// production host at build time; locally the relative path is kept.
const siteHost = process.env.VERCEL_PROJECT_PRODUCTION_URL
const absoluteOgImage: Plugin = {
  name: 'absolute-og-image',
  transformIndexHtml: (html) =>
    siteHost
      ? html.replaceAll('content="/og-image.png"', `content="https://${siteHost}/og-image.png"`)
      : html,
}

export default defineConfig({
  plugins: [react(), tailwindcss(), absoluteOgImage],
})
