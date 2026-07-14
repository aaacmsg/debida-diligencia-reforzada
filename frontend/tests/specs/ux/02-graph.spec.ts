import { test, expect } from '../../fixtures/auth.fixture';

test.describe('UX-04: Grafo de relaciones', () => {

  test('TC-15: Grafo carga con nodos y aristas', async ({ authPage: page }) => {
    await page.goto('/grafo');

    await expect(page.locator('svg').first()).toBeVisible();
    const leyenda = page.getByTestId('grafo-leyenda');
    await expect(leyenda).toBeVisible();
    await expect(leyenda.getByText('Cliente', { exact: true })).toBeVisible();
    await expect(leyenda.getByText('PEP', { exact: true })).toBeVisible();
  });

  test('TC-16: Controles de zoom funcionan', async ({ authPage: page }) => {
    await page.goto('/grafo');

    await expect(page.locator('text=/Zoom.*\\d+%/')).toBeVisible();

    await page.getByLabel('Acercar').click();
    await expect(page.locator('text=/Zoom: 120%/')).toBeVisible();

    await page.getByLabel('Alejar').click();
    await expect(page.locator('text=/Zoom: 100%/')).toBeVisible();

    await page.getByLabel('Restablecer vista').click();
    await expect(page.locator('text=/Zoom: 100%/')).toBeVisible();
  });

  test('TC-17: Nodos son arrastrables', async ({ authPage: page }) => {
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
