// src/components/Navbar.js
import React from 'react';
import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
    const { currentUser, logout } = useAuth();

    const handleLogin = () => {
        window.location.href = 'http://localhost:5000/api/auth/google/login';
    };

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <Link to="/" className="navbar-logo">
                    O Perfeccionista v0.4
                </Link>
                <ul className="navbar-menu">
                    <li className="navbar-item">
                        <NavLink to="/" className={({ isActive }) => (isActive ? "navbar-link active" : "navbar-link")}>
                            Início
                        </NavLink>
                    </li>

                    {/* Adicionamos o link da Loja aqui, visível para todos */}
                    <li className="navbar-item">
                        <NavLink to="/shop" className={({ isActive }) => (isActive ? "navbar-link active" : "navbar-link")}>
                            Loja
                        </NavLink>
                    </li>

                    {currentUser ? (
                        // --- Links para usuários LOGADOS ---
                        <>
                            <li className="navbar-item">
                                <NavLink to="/dashboard" className={({ isActive }) => (isActive ? "navbar-link active" : "navbar-link")}>
                                    Dashboard
                                </NavLink>
                            </li>
                            <li className="navbar-item">
                                <NavLink to={`/user/${currentUser.id}`} className={({ isActive }) => (isActive ? "navbar-link active" : "navbar-link")}>
                                    Meu Perfil
                                </NavLink>
                            </li>
                            <li className="navbar-item">
                                <NavLink to="/inventory" className={({ isActive }) => (isActive ? "navbar-link active" : "navbar-link")}>
                                    Inventário
                                </NavLink>
                            </li>
                            <li className="navbar-item">
                                <button onClick={logout} className="navbar-button">Sair</button>
                            </li>                            
                        </>
                    ) : (
                        // --- Botão de Login para usuários DESLOGADOS (NOVO ESTILO) ---
                        <li className="navbar-item">
                            <button onClick={handleLogin} className="navbar-button google-style">
                                <img src="https://developers.google.com/identity/images/g-logo.png" alt="Google G" className="google-icon-navbar" />
                                <span>Conectar-se</span>
                            </button>
                        </li>
                    )}
                </ul>
            </div>
        </nav>
    );
}