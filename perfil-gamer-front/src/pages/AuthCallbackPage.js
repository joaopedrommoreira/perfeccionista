// src/pages/AuthCallbackPage.js
import React, { useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext'; // Importa nosso hook

export default function AuthCallbackPage() {
  const { login } = useAuth(); // Pega a função login do context
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      login(token); // Usa a função login para atualizar o estado global
      navigate('/dashboard'); // Redireciona para o dashboard
    } else {
      navigate('/');
    }
  }, [searchParams, navigate, login]);

  return <div className="container"><h1>Autenticando...</h1></div>;
}