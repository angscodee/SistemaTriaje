import React from 'react';

function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">SistemaTriaje</h1>
        <p className="text-xl text-gray-400 mb-8">
          Sistema de triaje automático de alertas SOC para PYMEs
        </p>
        <div className="bg-gray-800 rounded-lg p-6 max-w-2xl">
          <h2 className="text-2xl font-semibold mb-4">🚀 En desarrollo</h2>
          <p className="text-gray-300 mb-4">
            El dashboard está en construcción. Por ahora puedes acceder a:
          </p>
          <div className="space-y-2">
            <a
              href="http://localhost:8000/docs"
              className="block bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded transition"
            >
              📚 Backend API (Swagger)
            </a>
            <a
              href="http://localhost:5678"
              className="block bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded transition"
            >
              🔄 n8n Workflow
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
