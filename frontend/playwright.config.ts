import { defineConfig, devices } from '@playwright/test';

// Parametrizable para entornos donde el puerto 3000 esta ocupado:
//   E2E_HOST=127.0.0.1 E2E_PORT=3001 npx playwright test
const E2E_PORT = Number(process.env.E2E_PORT || 3000);
const E2E_HOST = process.env.E2E_HOST || 'localhost';

export default defineConfig({
  testDir: './tests/specs',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [
    ['html', { outputFolder: 'tests/report' }],
    ['list'],
  ],
  use: {
    baseURL: `http://${E2E_HOST}:${E2E_PORT}`,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: `npx vite --host 0.0.0.0 --port ${E2E_PORT} --strictPort`,
    // url (no port): valida contra la IP exacta y evita reutilizar por error
    // otro servidor que escuche el mismo puerto solo en IPv6
    url: `http://${E2E_HOST}:${E2E_PORT}`,
    cwd: '.',
    reuseExistingServer: true,
    timeout: 60000,
  },
});
