import { Page } from '@playwright/test';

export async function login(page: Page, username = 'admin', password = 'admin123') {
  await page.goto('/login');
  await page.fill('input[placeholder="Ingrese su usuario"]', username);
  await page.fill('input[placeholder="Ingrese su contrasena"]', password);
  await page.click('button:has-text("Iniciar Sesion")');
  await page.waitForURL('/dashboard');
}

export async function createClient(
  page: Page,
  data: {
    nombre: string;
    tipo_identificacion?: string;
    numero_identificacion?: string;
    es_pep?: boolean;
    cargo_pep?: string;
    relacion_pep?: string;
    pais_residencia_fiscal?: string;
  }
) {
  await page.goto('/clientes');
  await page.click('button:has-text("Nuevo Cliente")');
  await page.fill('input[placeholder="Ingrese su usuario"]', data.nombre);
  // Simplified - actual form filling depends on exact field layout
  await page.fill('input:below(:text("Nombre *"))', data.nombre);
}

export function generateIdentificacion(): string {
  const nums = Math.floor(Math.random() * 10000000).toString().padStart(7, '0');
  const prefix = Math.floor(Math.random() * 20).toString();
  return `${prefix}-${nums}-${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`;
}
