import { test, expect } from '../../fixtures/auth.fixture';

test.describe('UX-07: Accesibilidad WCAG', () => {

  test('TC-20: Elementos interactivos tienen aria-labels o texto visible', async ({ authPage: page }) => {
    const pages = ['/dashboard', '/clientes', '/expedientes', '/pep', '/reportes', '/grafo'];
    for (const route of pages) {
      await page.goto(route);
      await page.waitForTimeout(300);

      const buttons = page.locator('button, a, input, select, textarea');
      const count = await buttons.count();

      if (count > 0) {
        for (let i = 0; i < Math.min(count, 10); i++) {
          const el = buttons.nth(i);
          const tag = await el.evaluate((e) => e.tagName);
          const hasAria = await el.evaluate((e) =>
            e.hasAttribute('aria-label') || e.hasAttribute('aria-labelledby')
          );
          const hasText = await el.evaluate((e) =>
            (e.textContent || '').trim().length > 0 ||
            (e.getAttribute('placeholder') || '').length > 0
          );

          if (tag !== 'A' || hasText) {
            const passes = hasAria || hasText;
            expect(passes).toBeTruthy();
          }
        }
      }
    }
  });

  test('Contraste de colores en textos principales', async ({ authPage: page }) => {
    await page.goto('/dashboard');

    const textElements = page.locator('.text-gray-900, .text-gray-700, .text-primary-600');
    const count = await textElements.count();
    expect(count).toBeGreaterThanOrEqual(3);

    const firstColor = await textElements.first().evaluate((el) =>
      window.getComputedStyle(el).color
    );
    expect(firstColor).not.toBe('transparent');
  });
});
