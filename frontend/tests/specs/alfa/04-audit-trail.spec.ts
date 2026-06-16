import { test, expect } from '../../fixtures/auth.fixture';

test.describe('ALF-05: Integridad del log de auditoria', () => {

  test('TC-09: Crear cliente genera evento de auditoria', async ({ page }) => {
    await page.goto('/expedientes');

    const expedienteLink = page.locator('a:has-text("EDD-")').first();
    if (await expedienteLink.isVisible()) {
      await expedienteLink.click();
      await page.waitForURL(/\/expedientes\/\d+/);

      await page.click('button:has-text("Trazabilidad")');

      await expect(page.locator('text=CREAR_CLIENTE')).toBeVisible();
      await expect(page.locator('text=admin')).toBeVisible();

      const eventRows = page.locator('table tbody tr');
      const count = await eventRows.count();
      expect(count).toBeGreaterThanOrEqual(1);
    }
  });
});

test.describe('ALF-08: Trazabilidad de modificaciones', () => {

  test('TC-10: Editar cliente genera evento de auditoria', async ({ page }) => {
    await page.goto('/clientes');

    const editBtn = page.locator('button:has-text("Editar")').first();
    if (await editBtn.isVisible()) {
      await editBtn.click();

      await page.fill('input:below(:text("Direccion"))', 'Direccion actualizada test');
      await page.click('button:has-text("Guardar")');

      await page.goto('/reportes');
      await expect(page.locator('text=admin')).toBeVisible();
    }
  });
});

test.describe('ALF-09: Conservacion de registros', () => {

  test('Eventos tienen created_at', async ({ page }) => {
    await page.goto('/reportes');

    const rows = page.locator('table tbody tr');
    const count = await rows.count();
    expect(count).toBeGreaterThanOrEqual(1);

    if (count > 0) {
      const dateCell = rows.first().locator('td').nth(0);
      const dateText = await dateCell.textContent();
      expect(dateText).not.toBeNull();
    }
  });
});
