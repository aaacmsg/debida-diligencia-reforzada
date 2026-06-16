# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: alfa\01-login.spec.ts >> ALF-06: Autenticacion >> TC-02: Login fallido muestra error
- Location: tests\specs\alfa\01-login.spec.ts:16:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('text=Incorrect username or password')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('text=Incorrect username or password')

```

```yaml
- img
- heading "Diligencia Reforzada" [level=1]
- paragraph: Sistema AML/CFT Panama
- text: Error al iniciar sesion Usuario
- textbox "Ingrese su usuario": admin
- text: Contrasena
- textbox "Ingrese su contrasena": wrongpass
- button "Iniciar Sesion"
- paragraph: Cumplimiento segun Ley 23/2015 - Ley 254/2021
```

# Test source

```ts
  1  | import { test, expect } from '../../fixtures/auth.fixture';
  2  | 
  3  | test.describe('ALF-06: Autenticacion', () => {
  4  | 
  5  |   test('TC-01: Login exitoso admin/admin123', async ({ page }) => {
  6  |     await page.goto('/login');
  7  |     await page.fill('input[placeholder="Ingrese su usuario"]', 'admin');
  8  |     await page.fill('input[placeholder="Ingrese su contrasena"]', 'admin123');
  9  |     await page.click('button:has-text("Iniciar Sesion")');
  10 | 
  11 |     await expect(page).toHaveURL('/dashboard');
  12 |     await expect(page.locator('text=Diligencia Reforzada')).toBeVisible();
  13 |     await expect(page.locator('text=Dashboard')).toBeVisible();
  14 |   });
  15 | 
  16 |   test('TC-02: Login fallido muestra error', async ({ page }) => {
  17 |     await page.goto('/login');
  18 |     await page.fill('input[placeholder="Ingrese su usuario"]', 'admin');
  19 |     await page.fill('input[placeholder="Ingrese su contrasena"]', 'wrongpass');
  20 |     await page.click('button:has-text("Iniciar Sesion")');
  21 | 
> 22 |     await expect(page.locator('text=Incorrect username or password')).toBeVisible();
     |                                                                       ^ Error: expect(locator).toBeVisible() failed
  23 |     await expect(page).toHaveURL('/login');
  24 |   });
  25 | 
  26 |   test('TC-03: Redirect a /login si no autenticado', async ({ page }) => {
  27 |     await page.goto('/dashboard');
  28 |     await expect(page).toHaveURL('/login');
  29 |   });
  30 | });
  31 | 
  32 | test.describe('ALF-07: Seguridad - proteccion de rutas', () => {
  33 | 
  34 |   test('Rutas protegidas redirigen a login', async ({ page }) => {
  35 |     const routes = ['/clientes', '/expedientes', '/pep', '/reportes', '/grafo', '/configuracion'];
  36 |     for (const route of routes) {
  37 |       await page.goto(route);
  38 |       await expect(page).toHaveURL('/login');
  39 |     }
  40 |   });
  41 | });
  42 | 
```