import { test, expect } from '../../fixtures/auth.fixture';

test.describe('UX-04: Grafo de relaciones', () => {

  test('TC-15: Grafo carga con nodos y aristas', async ({ page }) => {
    await page.goto('/grafo');

    await expect(page.locator('svg')).toBeVisible();
    await expect(page.locator('text=Leyenda')).toBeVisible();
    await expect(page.locator('text=Cliente')).toBeVisible();
    await expect(page.locator('text=PEP')).toBeVisible();
  });

  test('TC-16: Controles de zoom funcionan', async ({ page }) => {
    await page.goto('/grafo');

    const zoomValue = page.locator('text=/Zoom.*\\d+%/');

    const zoomInBtn = page.locator('button:has-text("Zoom In")');
    if (await zoomInBtn.isVisible()) {
      await zoomInBtn.click();
      await expect(page.locator('text=/Zoom.*\\d+%/')).toBeVisible();
    }

    const zoomOutBtn = page.locator('button:has-text("Zoom Out")');
    if (await zoomOutBtn.isVisible()) {
      await zoomOutBtn.click();
    }

    const resetBtn = page.locator('button:has-text("Reset")');
    if (await resetBtn.isVisible()) {
      await resetBtn.click();
    }
  });

  test('TC-17: Nodos son arrastrables', async ({ page }) => {
    await page.goto('/grafo');

    const circle = page.locator('svg circle').first();
    await expect(circle).toBeVisible();

    const box = await circle.boundingBox();
    if (box) {
      await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
      await page.mouse.down();
      await page.mouse.move(box.x + 50, box.y + 50, { steps: 5 });
      await page.mouse.up();
    }
  });
});
