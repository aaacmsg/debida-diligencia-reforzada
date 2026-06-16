# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: alfa\02-form-validation.spec.ts >> ALF-02: Validacion de campos obligatorios >> TC-04: No permite guardar con campos obligatorios vacios
- Location: tests\specs\alfa\02-form-validation.spec.ts:6:3

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.click: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('button:has-text("Nuevo Cliente")')

```

# Page snapshot

```yaml
- generic [ref=e4]:
  - generic [ref=e5]:
    - img [ref=e7]
    - heading "Diligencia Reforzada" [level=1] [ref=e9]
    - paragraph [ref=e10]: Sistema AML/CFT Panama
  - generic [ref=e11]:
    - generic [ref=e12]:
      - generic [ref=e13]: Usuario
      - textbox "Ingrese su usuario" [ref=e14]
    - generic [ref=e15]:
      - generic [ref=e16]: Contrasena
      - textbox "Ingrese su contrasena" [ref=e17]
    - button "Iniciar Sesion" [ref=e18] [cursor=pointer]
  - paragraph [ref=e19]: Cumplimiento segun Ley 23/2015 - Ley 254/2021
```

# Test source

```ts
  1  | import { test, expect } from '../../fixtures/auth.fixture';
  2  | import { generateIdentificacion } from '../../helpers/api.helper';
  3  | 
  4  | test.describe('ALF-02: Validacion de campos obligatorios', () => {
  5  | 
  6  |   test('TC-04: No permite guardar con campos obligatorios vacios', async ({ page }) => {
  7  |     await page.goto('/clientes');
> 8  |     await page.click('button:has-text("Nuevo Cliente")');
     |                ^ Error: page.click: Test timeout of 30000ms exceeded.
  9  |     await page.click('button:has-text("Guardar Cliente")');
  10 | 
  11 |     await expect(page.locator('text=Requerido')).toBeVisible();
  12 |   });
  13 | 
  14 |   test('TC-05: Crea cliente con datos validos', async ({ page }) => {
  15 |     const cedula = generateIdentificacion();
  16 |     const nombre = `Test${Date.now()}`;
  17 | 
  18 |     await page.goto('/clientes');
  19 |     await page.click('button:has-text("Nuevo Cliente")');
  20 |     await page.fill('input:below(:text("Nombre *"))', nombre);
  21 |     await page.fill('input:below(:text("Numero de Identificacion *"))', cedula);
  22 |     await page.click('button:has-text("Guardar Cliente")');
  23 | 
  24 |     await expect(page.locator('text=Cliente y expediente creados exitosamente')).toBeVisible();
  25 |     await expect(page.locator(`text=${nombre}`)).toBeVisible();
  26 |   });
  27 | 
  28 |   test('TC-06: PEP fields required cuando es_pep=true', async ({ page }) => {
  29 |     const cedula = generateIdentificacion();
  30 | 
  31 |     await page.goto('/clientes');
  32 |     await page.click('button:has-text("Nuevo Cliente")');
  33 |     await page.fill('input:below(:text("Nombre *"))', `PEPTest${Date.now()}`);
  34 |     await page.fill('input:below(:text("Numero de Identificacion *"))', cedula);
  35 |     await page.check('input[type="checkbox"]:below(:text("PEP"))');
  36 |     await page.click('button:has-text("Guardar Cliente")');
  37 | 
  38 |     await expect(page.locator('text=Cargo PEP requerido')).toBeVisible();
  39 |     await expect(page.locator('text=Tipo de relacion requerido')).toBeVisible();
  40 |   });
  41 | });
  42 | 
  43 | test.describe('ALF-01: Beneficiario Final', () => {
  44 | 
  45 |   test('Sumatoria participaciones', async ({ page }) => {
  46 |     await page.goto('/clientes');
  47 |     await page.click('button:has-text("Nuevo Cliente")');
  48 | 
  49 |     await page.click('text=III. Beneficiario Final');
  50 | 
  51 |     await expect(page.locator('text=Beneficiario Final')).toBeVisible();
  52 |   });
  53 | });
  54 | 
```