import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { useAuthStore } from './stores/authStore';
import Layout from './components/layout/Layout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ClientesPage from './pages/ClientesPage';
import ExpedientesPage from './pages/ExpedientesPage';
import ExpedienteDetailPage from './pages/ExpedienteDetailPage';
import PEPSearchPage from './pages/PEPSearchPage';
import ReportesPage from './pages/ReportesPage';
import GrafoPage from './pages/GrafoPage';
import ConfiguracionPage from './pages/ConfiguracionPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

function App() {
  return (
    <BrowserRouter>
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="clientes" element={<ClientesPage />} />
          <Route path="expedientes" element={<ExpedientesPage />} />
          <Route path="expedientes/:id" element={<ExpedienteDetailPage />} />
          <Route path="pep" element={<PEPSearchPage />} />
          <Route path="reportes" element={<ReportesPage />} />
          <Route path="grafo" element={<GrafoPage />} />
          <Route path="configuracion" element={<ConfiguracionPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
