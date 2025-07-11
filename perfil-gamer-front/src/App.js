// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Navbar from './components/Navbar';
import { AuthProvider } from './context/AuthContext';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Importa as páginas dos seus novos arquivos
import HomePage from './pages/HomePage';
import AuthCallbackPage from './pages/AuthCallbackPage';
import DashboardPage from './pages/DashboardPage';
import PublicProfilePage from './pages/PublicProfilePage';
import ShopPage from './pages/ShopPage'; // Importa a página da loja
import InventoryPage from './pages/InventoryPage'; // Importa a página de inventário
import OnboardingPage from './pages/OnboardingPage'; // Importa a página de onboarding
import GameDetailPage from './pages/GameDetailPage'; // Importa a página de detalhes do jogo
import DatabasePage from './pages/DatabasePage';


function App() {
  return (
    // Envolvemos toda a aplicação no AuthProvider
    <AuthProvider>
      <Router>
        <Navbar /> {/* Renderiza a Navbar aqui, fora do Routes */}
        <main> {/* Adicionamos um <main> para o conteúdo da página */}
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/auth/callback" element={<AuthCallbackPage />} />
            <Route path="/shop" element={<ShopPage />} /> {/* Rota para a loja */}
            <Route path="/inventory" element={<InventoryPage />} /> {/* Rota para o inventário */}
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/onboarding" element={<OnboardingPage />} /> {/* Rota para a página de onboarding */}
            <Route path="/user/:userId" element={<PublicProfilePage />} />
            <Route path="/jogo/:appid" element={<GameDetailPage />} />
            <Route path="/database" element={<DatabasePage />} />
          </Routes>
        </main>
        <ToastContainer
            position="bottom-right"
            autoClose={5000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="dark"
          />
      </Router>
    </AuthProvider>
  );
}

export default App;