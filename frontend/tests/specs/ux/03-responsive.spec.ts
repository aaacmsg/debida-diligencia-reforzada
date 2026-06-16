import { test, expect } from '../../fixtures/auth.fixture';

test.describe('UX-06: Responsividad', () => {

  test('TC-18: Mobile 320px - sin scroll horizontal', async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 });

    const pages = ['/dashboard', '/clientes', '/expedientes', '/pep', '/reportes', '/grafo'];
    for (const route of pages) {
      await page.goto(route);
      await page.waitForTimeout(500);

      const viewportWidth = page.viewportSize()?.width || 320;
      const htmlWidth = await page.evaluate(() => document.documentElement.scrollWidth);
      expect(htmlWidth).toBeLessThanOrEqual(viewportWidth + 5);
    }
  });

  test('TC-19: Tablet 768px - layout adaptado', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });

    await page.goto('/clientes');
    await page.click('button:has-text("Nuevo Cliente")');
    await page.waitForTimeout(500);

    await page.goto('/dashboard');
    await page.waitForTimeout(500);

    const elementsVisible = page.locator('.card');
    const count = await elementsVisible.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });
});
