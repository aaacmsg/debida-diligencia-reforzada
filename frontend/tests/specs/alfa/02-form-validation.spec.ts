import { test, expect } from '../../fixtures/auth.fixture';
import { generateIdentificacion } from '../../helpers/api.helper';

test.describe('ALF-02: Validacion de campos obligatorios', () => {

  test('TC-04: No permite guardar con campos obligatorios vacios', async ({ page }) => {
    await page.goto('/clientes');
    await page.click('button:has-text("Nuevo Cliente")');
    await page.click('button:has-text("Guardar Cliente")');

    await expect(page.locator('text=Requerido')).toBeVisible();
  });

  test('TC-05: Crea cliente con datos validos', async ({ page }) => {
    const cedula = generateIdentificacion();
    const nombre = `Test${Date.now()}`;

    await page.goto('/clientes');
    await page.click('button:has-text("Nuevo Cliente")');
    await page.fill('input:below(:text("Nombre *"))', nombre);
    await page.fill('input:below(:text("Numero de Identificacion *"))', cedula);
    await page.click('button:has-text("Guardar Cliente")');

    await expect(page.locator('text=Cliente y expediente creados exitosamente')).toBeVisible();
    await expect(page.locator(`text=${nombre}`)).toBeVisible();
  });

  test('TC-06: PEP fields required cuando es_pep=true', async ({ page }) => {
    const cedula = generateIdentificacion();

    await page.goto('/clientes');
    await page.click('button:has-text("Nuevo Cliente")');
    await page.fill('input:below(:text("Nombre *"))', `PEPTest${Date.now()}`);
    await page.fill('input:below(:text("Numero de Identificacion *"))', cedula);
    await page.check('input[type="checkbox"]:below(:text("PEP"))');
    await page.click('button:has-text("Guardar Cliente")');

    await expect(page.locator('text=Cargo PEP requerido')).toBeVisible();
    await expect(page.locator('text=Tipo de relacion requerido')).toBeVisible();
  });
});

test.describe('ALF-01: Beneficiario Final', () => {

  test('Sumatoria participaciones', async ({ page }) => {
    await page.goto('/clientes');
    await page.click('button:has-text("Nuevo Cliente")');

    await page.click('text=III. Beneficiario Final');

    await expect(page.locator('text=Beneficiario Final')).toBeVisible();
  });
});
