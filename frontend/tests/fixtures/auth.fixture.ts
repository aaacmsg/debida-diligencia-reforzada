import { test as base } from '@playwright/test';

export const test = base.extend({
  authPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.fill('input[placeholder="Ingrese su usuario"]', 'admin');
    await page.fill('input[placeholder="Ingrese su contrasena"]', 'admin123');
    await page.click('button:has-text("Iniciar Sesion")');
    await page.waitForURL('/dashboard');
    await use(page);
  },
});

export { expect } from '@playwright/test';
