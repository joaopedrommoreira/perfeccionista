// src/pages/OnboardingPage.js
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function OnboardingPage() {
    const [username, setUsername] = useState('');
    const [termsAccepted, setTermsAccepted] = useState(false);
    const [statusMessage, setStatusMessage] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const { login } = useAuth();

    // Este useEffect é crucial: ele pega o token da URL e "loga" o usuário no nosso Contexto.
    useEffect(() => {
        const token = searchParams.get('token');
        if (token) {
            login(token); // Isso atualiza o estado global da aplicação
        } else {
            // Se um usuário não-logado tentar acessar esta página, ele é enviado para o início.
            navigate('/');
        }
    }, [login, navigate, searchParams]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!termsAccepted) {
            setStatusMessage("Você precisa aceitar os termos de uso.");
            return;
        }
        setIsSubmitting(true);
        setStatusMessage('');
        
        const token = localStorage.getItem('userToken');

        try {
            const response = await fetch('http://localhost:5000/api/profile/username', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}`},
                body: JSON.stringify({ username })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error);
            
            // Se tudo deu certo, redireciona para o dashboard!
            navigate('/dashboard');

        } catch (error) {
            setStatusMessage(`Erro: ${error.message}`);
        } finally {
            setIsSubmitting(false);
        }
    };

    const isButtonDisabled = !username || !termsAccepted || isSubmitting;

    return (
        <div className="container">
            <div className="content-section" style={{maxWidth: '600px', margin: '50px auto'}}>
                <h2>Finalize seu Cadastro</h2>
                <p>Bem-vindo! Para continuar, escolha um nome de usuário único. Este nome será público e não poderá ser alterado depois.</p>
                
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="Seu username único"
                        style={{ width: '100%', padding: '12px', borderRadius: '4px', border: '1px solid #555', background: '#333', color: 'white', marginBottom: '15px', fontSize: '1rem' }}
                    />
                    <div style={{display: 'flex', alignItems: 'center', marginBottom: '20px', justifyContent: 'center'}}>
                        <input 
                            type="checkbox" 
                            id="terms" 
                            checked={termsAccepted} 
                            onChange={(e) => setTermsAccepted(e.target.checked)}
                            style={{marginRight: '10px', transform: 'scale(1.2)'}}
                        />
                        <label htmlFor="terms">Eu li e aceito os termos de uso.</label>
                    </div>
                    
                    <button type="submit" className="button-primary" disabled={isButtonDisabled} style={{width: '100%', fontSize: '1.1rem'}}>
                        {isSubmitting ? 'Salvando...' : 'Concluir e Acessar'}
                    </button>
                </form>
                {statusMessage && <p style={{marginTop: '15px', color: 'lightcoral', fontWeight: 'bold'}}>{statusMessage}</p>}
            </div>
        </div>
    );
}