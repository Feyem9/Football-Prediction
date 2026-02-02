/**
 * Test Utilities - Helpers pour les tests React
 * Ce fichier est dans un dossier test/ et n'est pas concerné par fast-refresh
 */
/* eslint-disable react-refresh/only-export-components */
import { render, type RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import type { ReactElement, ReactNode } from 'react';

// Wrapper avec les providers nécessaires
function AllTheProviders({ children }: { children: ReactNode }) {
  return (
    <BrowserRouter>
      {children}
    </BrowserRouter>
  );
}

// Custom render avec providers
function customRender(
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  return render(ui, { wrapper: AllTheProviders, ...options });
}

// Re-export everything
export * from '@testing-library/react';
export { customRender as render };
