import { test, expect } from '../../fixtures/auth.fixture';

test.describe('ALF-06: Autenticacion', () => {

  test('TC-01: Login exitoso admin/admin123', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="Ingrese su usuario"]', 'admin');
    await page.fill('input[placeholder="Ingrese su contrasena"]', 'admin123');
    await page.click('button:has-text("Iniciar Sesion")');

    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('text=Diligencia Reforzada')).toBeVisible();
    await expect(page.locator('text=Dashboard')).toBeVisible();
  });

  test('TC-02: Login fallido muestra error', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="Ingrese su usuario"]', 'admin');
    await page.fill('input[placeholder="Ingrese su contrasena"]', 'wrongpass');
    await page.click('button:has-text("Iniciar Sesion")');

    await expect(page.locator('text=Incorrect username or password')).toBeVisible();
    await expect(page).toHaveURL('/login');
  });

  test('TC-03: Redirect a /login si no autenticado', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL('/login');
  });
});

test.describe('ALF-07: Seguridad - proteccion de rutas', () => {

  test('Rutas protegidas redirigen a login', async ({ page }) => {
    const routes = ['/clientes', '/expedientes', '/pep', '/reportes', '/grafo', '/configuracion'];
    for (const route of routes) {
      await page.goto(route);
      await expect(page).toHaveURL('/login');
    }
  });
});
