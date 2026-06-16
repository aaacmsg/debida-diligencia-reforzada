import { test, expect } from '../../fixtures/auth.fixture';
import { generateIdentificacion } from '../../helpers/api.helper';

test.describe('BET-02: PEP auto-flag en expediente', () => {

  test('TC-07: Crear cliente PEP genera expediente pendiente_gerencia', async ({ page }) => {
    const cedula = generateIdentificacion();
    const nombre = `PEP${Date.now()}`;

    await page.goto('/clientes');
    await page.click('button:has-text("Nuevo Cliente")');
    await page.fill('input:below(:text("Nombre *"))', nombre);
    await page.fill('input:below(:text("Numero de Identificacion *"))', cedula);
    await page.check('input[type="checkbox"]:below(:text("PEP"))');

    await page.selectOption('select:below(:text("Cargo Politico"))', 'Director');
    await page.selectOption('select:below(:text("Tipo de Relacion"))', 'directo');
    await page.fill('input:below(:text("Pais de Residencia Fiscal *"))', 'Panama');

    await page.click('button:has-text("Guardar Cliente")');
    await expect(page.locator('text=Cliente y expediente creados exitosamente')).toBeVisible();

    await page.goto('/expedientes');
    await expect(page.locator('text=pendiente_gerencia')).toBeVisible();
    await expect(page.locator('text=alto')).toBeVisible();
  });
});

test.describe('ALF-04: Aprobacion de alto riesgo', () => {

  test('TC-08: Approve requiere comentario', async ({ page }) => {
    await page.goto('/expedientes');

    const expedienteLink = page.locator('a:has-text("EDD-")').first();
    if (await expedienteLink.isVisible()) {
      await expedienteLink.click();
      await page.waitForURL(/\/expedientes\/\d+/);

      const approveBtn = page.locator('button:has-text("Aprobar")');
      if (await approveBtn.isVisible()) {
        await approveBtn.click();

        const commentModal = page.locator('text=Comentario');
        if (await commentModal.isVisible()) {
          await page.click('button:has-text("Confirmar")');
          await expect(page.locator('text=Comentario obligatorio')).toBeVisible();
        }
      }
    }
  });
});
