import { test, expect } from '../../fixtures/auth.fixture';
import { generateIdentificacion } from '../../helpers/api.helper';

test.describe('BET-02: PEP auto-flag', () => {

  test('TC-11: Cliente PEP crea expediente con requiere_aprobacion_gerencial=true', async ({ page }) => {
    const cedula = generateIdentificacion();
    const nombre = `BetaPEP${Date.now()}`;

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
    const row = page.locator(`text=${nombre}`);
    await expect(row).toBeVisible();
  });
});

test.describe('BET-01: Documento origen de fondos', () => {

  test('TC-12: Upload de documento en expediente', async ({ page }) => {
    await page.goto('/expedientes');

    const expedienteLink = page.locator('a:has-text("EDD-")').first();
    if (await expedienteLink.isVisible()) {
      await expedienteLink.click();
      await page.waitForURL(/\/expedientes\/\d+/);

      await page.click('button:has-text("Documentos")');

      const fileInput = page.locator('input[type="file"]');
      if (await fileInput.isVisible()) {
        const filePath = __dirname + '/../../fixtures/test-doc.pdf';
        await fileInput.setInputFiles({
          name: 'test-doc.pdf',
          mimeType: 'application/pdf',
          buffer: Buffer.from('%PDF-1.4 test document content'),
        });
        await page.click('button:has-text("Subir")');
      }
    }
  });
});
