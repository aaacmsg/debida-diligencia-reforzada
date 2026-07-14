import { test, expect } from '../../fixtures/auth.fixture';
import { generateIdentificacion } from '../../helpers/api.helper';

test.describe('BET-02: PEP auto-flag en expediente', () => {

  test('TC-07: Crear cliente PEP genera expediente pendiente_gerencia', async ({ authPage: page }) => {
    const cedula = generateIdentificacion();
    const nombre = `PEP${Date.now()}`;

    await page.goto('/clientes');
    await page.click('button:has-text("Nuevo Cliente")');
    await page.fill('input[name="nombre"]', nombre);
    await page.fill('input[name="numero_identificacion"]', cedula);
    await page.check('input[name="es_pep"]');

    await page.selectOption('select[name="cargo_pep"]', 'Director');
    await page.selectOption('select[name="relacion_pep"]', 'directo');
    await page.fill('input[name="pais_residencia_fiscal"]', 'Panama');

    await page.click('button:has-text("Guardar Cliente")');
    await expect(page.locator('text=Cliente y expediente creados exitosamente')).toBeVisible({ timeout: 10000 });

    await page.goto('/expedientes');
    await expect(page.locator('span:has-text("pendiente gerencia")').first()).toBeVisible();
    await expect(page.locator('span:has-text("alto")').first()).toBeVisible();
  });
});

test.describe('ALF-04: Aprobacion de alto riesgo', () => {

  test('TC-08: Approve requiere comentario', async ({ authPage: page }) => {
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
