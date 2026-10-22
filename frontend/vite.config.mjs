import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { readFileSync } from 'node:fs'
import { execFileSync } from 'node:child_process'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const root = dirname(fileURLToPath(import.meta.url))
const packageInfo = JSON.parse(readFileSync(resolve(root, 'package.json'), 'utf8'))
let commit = 'local'
try {
  commit = execFileSync('git', ['rev-parse', '--short', 'HEAD'], { cwd: resolve(root, '..'), encoding: 'utf8' }).trim()
} catch {
  // Source archives still build and display an honest fallback.
}

export default defineConfig({
  plugins: [react()],
  define: {
    __APP_VERSION__: JSON.stringify(packageInfo.version),
    __APP_COMMIT__: JSON.stringify(commit),
  },
  build: {
    rollupOptions: {
      input: {
        main: resolve(root, 'index.html'),
        architecture: resolve(root, 'agent_architecture.html'),
        cost: resolve(root, 'cost_performance.html'),
        prodLoop: resolve(root, 'prod_loop.html'),
      },
    },
  },
})
