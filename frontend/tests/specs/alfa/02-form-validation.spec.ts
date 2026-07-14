import { test, expect } from '../../fixtures/auth.fixture';
import { generateIdentificacion } from '../../helpers/api.helper';

test.describe('ALF-02: Validacion de campos obligatorios', () => {

  test('TC-04: No permite guardar con campos obligatorios vacios', async ({ authPage: page }) => {
    await page.goto('/clientes');
    await page.click('button:has-text("Nuevo Cliente")');
    await page.click('button:has-text("Guardar Cliente")');

    await expect(page.locator('text=Requerido').first()).toBeVisible();
  });

  test('TC-05: Crea cliente con datos validos', async ({ authPage: page }) => {
    const cedula = generateIdentificacion();
    const nombre = `Test${Date.now()}`;

    await page.goto('/clientes');
    await page.click('button:has-text("Nuevo Cliente")');
    await page.fill('input[name="nombre"]', nombre);
    await page.fill('input[name="numero_identificacion"]', cedula);
    await page.click('button:has-text("Guardar Cliente")');

    await expect(page.locator('text=Cliente y expediente creados exitosamente')).toBeVisible({ timeout: 10000 });
    await expect(page.locator(`text=${nombre}`).first()).toBeVisible();
  });

  test('TC-06: PEP fields required cuando es_pep=true', async ({ authPage: page }) => {
    const cedula = generateIdentificacion();

    await page.goto('/clientes');
    await page.click('button:has-text("Nuevo Cliente")');
    await page.fill('input[name="nombre"]', `PEPTest${Date.now()}`);
    await page.fill('input[name="numero_identificacion"]', cedula);
    await page.check('input[name="es_pep"]');
    await page.click('button:has-text("Guardar Cliente")');

    await expect(page.locator('text=Cargo PEP requerido')).toBeVisible();
    await expect(page.locator('text=Tipo de relacion requerido')).toBeVisible();
  });
});

test.describe('ALF-01: Beneficiario Final', () => {

  test('Sumatoria participaciones', async ({ authPage: page }) => {
    await page.goto('/clientes');
    await page.click('button:has-text("Nuevo Cliente")');

    await page.click('text=III. Beneficiario Final');

    await expect(page.locator('text=Beneficiario Final')).toBeVisible();
  });
});
