import { test as base, Page } from '@playwright/test';

// Token cacheado por worker: un solo login por corrida (respeta el rate limit del backend)
let cachedTokens: { access: string; refresh: string } | null = null;

export const test = base.extend<{ authPage: Page }>({
  authPage: async ({ page, request, baseURL }, use) => {
    if (!cachedTokens) {
      const resp = await request.post(`${baseURL}/api/v1/auth/login`, {
        form: { username: 'admin', password: 'admin123' },
      });
      if (!resp.ok()) {
        throw new Error(`Login de fixture fallo: ${resp.status()} ${await resp.text()}`);
      }
      const body = await resp.json();
      cachedTokens = { access: body.access_token, refresh: body.refresh_token };
    }
    await page.addInitScript(
      (tokens: { access: string; refresh: string }) => {
        localStorage.setItem('access_token', tokens.access);
        localStorage.setItem('refresh_token', tokens.refresh);
      },
      cachedTokens
    );
    await use(page);
  },
});

export { expect } from '@playwright/test';
