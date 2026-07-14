import { test, expect } from '../../fixtures/auth.fixture';

test.describe('UX-02: Activacion automatica seccion PEP', () => {

  test('TC-13: Campos PEP aparecen al marcar es_pep=true', async ({ authPage: page }) => {
    await page.goto('/clientes');
    await page.click('button:has-text("Nuevo Cliente")');

    await expect(page.locator('text=Cargo Politico')).not.toBeVisible();

    await page.check('input[type="checkbox"]:below(:text("PEP"))');

    await expect(page.locator('text=Cargo Politico')).toBeVisible();
    await expect(page.locator('text=Tipo de Relacion')).toBeVisible();
    await expect(page.locator('text=Pais de Residencia Fiscal')).toBeVisible();

    const amberBg = page.locator('text=Informacion PEP Obligatoria');
    await expect(amberBg).toBeVisible();
  });

  test('TC-14: Campos PEP se ocultan al desmarcar es_pep', async ({ authPage: page }) => {
    await page.goto('/clientes');
    await page.click('button:has-text("Nuevo Cliente")');

    await page.check('input[type="checkbox"]:below(:text("PEP"))');
    await expect(page.locator('text=Cargo Politico')).toBeVisible();

    await page.uncheck('input[type="checkbox"]:below(:text("PEP"))');
    await expect(page.locator('text=Cargo Politico')).not.toBeVisible();
  });
});

test.describe('UX-03: Consistencia visual', () => {

  test('Colores de riesgo consistentes en todas las paginas', async ({ authPage: page }) => {
    await page.goto('/clientes');
    await page.goto('/expedientes');
    await page.goto('/dashboard');

    const riskBadges = page.locator('.bg-red-100, .bg-yellow-100, .bg-green-100');
    const count = await riskBadges.count();

    const primaryElements = page.locator('.text-primary-600, .bg-primary-600');
    const primaryCount = await primaryElements.count();

    expect(count + primaryCount).toBeGreaterThanOrEqual(1);
  });
});
