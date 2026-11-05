import React, { useState, useEffect } from 'react';

interface Alert {
  id: number;
  external_id: string;
  source: string;
  rule_description: string;
  severity_original: string;
  status: string;
  received_at: string;
}

interface Metrics {
  total_alerts: number;
  critical_open_alerts: number;
  mttt_minutes: number;
  false_positive_rate: number;
}

function App() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_URL = 'http://localhost:8000/api/v1';

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Fetch metrics
      const metricsRes = await fetch(`${API_URL}/metrics/summary`);
      const metricsData = await metricsRes.json();
      setMetrics(metricsData);

      // Fetch alerts
      const alertsRes = await fetch(`${API_URL}/alerts?page=1&page_size=10`);
      const alertsData = await alertsRes.json();
      setAlerts(alertsData.items || []);

      setLoading(false);
    } catch (err) {
      setError('Error al conectar con el backend. Asegúrate de que esté en ejecución.');
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'alta':
        return 'bg-red-600';
      case 'media':
        return 'bg-yellow-600';
      case 'baja':
        return 'bg-blue-600';
      default:
        return 'bg-gray-600';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'triada':
        return 'text-green-400';
      case 'pendiente':
        return 'text-yellow-400';
      case 'descartada':
        return 'text-gray-400';
      default:
        return 'text-blue-400';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-xl">Cargando dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 text-gray-100 flex items-center justify-center">
        <div className="text-center max-w-2xl">
          <h1 className="text-4xl font-bold mb-4 text-red-500">❌ Error</h1>
          <p className="text-xl mb-6">{error}</p>
          <div className="bg-gray-800 rounded-lg p-6">
            <p className="text-gray-300 mb-4">Pasos para solucionar:</p>
            <ol className="text-left text-gray-400 space-y-2">
              <li>1. Verifica que el backend esté corriendo: <code className="bg-gray-700 px-2 py-1 rounded">docker compose ps</code></li>
              <li>2. Verifica los logs: <code className="bg-gray-700 px-2 py-1 rounded">docker compose logs backend</code></li>
              <li>3. Ejecuta las migraciones: <code className="bg-gray-700 px-2 py-1 rounded">make migrate</code></li>
            </ol>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">SistemaTriaje</h1>
            <p className="text-gray-400 text-sm">Sistema de triaje automático de alertas SOC</p>
          </div>
          <div className="flex gap-4">
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              📚 API Docs
            </a>
            <a
              href="http://localhost:5678"
              target="_blank"
              rel="noopener noreferrer"
              className="text-purple-400 hover:text-purple-300 text-sm"
            >
              🔄 n8n
            </a>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="container mx-auto px-6 py-8">
        {/* KPIs */}
        {metrics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <p className="text-gray-400 text-sm mb-2">Total de Alertas</p>
              <p className="text-3xl font-bold">{metrics.total_alerts}</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <p className="text-gray-400 text-sm mb-2">Críticas Abiertas</p>
              <p className="text-3xl font-bold text-red-500">{metrics.critical_open_alerts}</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <p className="text-gray-400 text-sm mb-2">MTTT (minutos)</p>
              <p className="text-3xl font-bold text-blue-500">{metrics.mttt_minutes.toFixed(2)}</p>
            </div>
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <p className="text-gray-400 text-sm mb-2">% Falsos Positivos</p>
              <p className="text-3xl font-bold text-yellow-500">{metrics.false_positive_rate.toFixed(1)}%</p>
            </div>
          </div>
        )}

        {/* Alerts table */}
        <div className="bg-gray-800 rounded-lg border border-gray-700">
          <div className="px-6 py-4 border-b border-gray-700">
            <h2 className="text-xl font-semibold">Alertas Recientes</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Fuente</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Descripción</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Severidad</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Estado</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase">Fecha</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {alerts.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-8 text-center text-gray-400">
                      No hay alertas. Ejecuta <code className="bg-gray-700 px-2 py-1 rounded">make seed</code> para generar datos de prueba.
                    </td>
                  </tr>
                ) : (
                  alerts.map((alert) => (
                    <tr key={alert.id} className="hover:bg-gray-750">
                      <td className="px-6 py-4 text-sm">{alert.id}</td>
                      <td className="px-6 py-4 text-sm">
                        <span className="px-2 py-1 bg-gray-700 rounded text-xs">{alert.source}</span>
                      </td>
                      <td className="px-6 py-4 text-sm">{alert.rule_description || 'N/A'}</td>
                      <td className="px-6 py-4 text-sm">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getSeverityColor(alert.severity_original)}`}>
                          {alert.severity_original}
                        </span>
                      </td>
                      <td className={`px-6 py-4 text-sm font-medium ${getStatusColor(alert.status)}`}>
                        {alert.status}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-400">
                        {new Date(alert.received_at).toLocaleString('es-ES')}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Info footer */}
        <div className="mt-8 text-center text-gray-500 text-sm">
          <p>✅ Dashboard funcional | 🔄 Autorefresco cada 30s (próximamente)</p>
          <p className="mt-2">
            Credenciales: admin@example.com / Demo1234! | 
            <a href="https://github.com/angscodee/SistemaTriaje" className="text-blue-400 hover:text-blue-300 ml-2">
              GitHub
            </a>
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;
