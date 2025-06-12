// src/pages/DashboardPage.js
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function DashboardPage() {
    const { logout } = useAuth();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    // Estado para os dados do usuário vindos da API /me
    const [userData, setUserData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    
    // Estados para os formulários
    const [username, setUsername] = useState('');
    const [avatarFile, setAvatarFile] = useState(null);
    const [gameName, setGameName] = useState('');
    const [searchType, setSearchType] = useState('name');
    const [isSubmitting, setIsSubmitting] = useState(false);
    
    // Estado para mensagens de status
    const [statusMessage, setStatusMessage] = useState('');
    const [steamLinkStatus, setSteamLinkStatus] = useState('');


    useEffect(() => {
        const token = localStorage.getItem('userToken');
        if (!token) { navigate('/'); return; }

        const fetchUserData = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/me', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!response.ok) throw new Error('Falha ao buscar dados.');
                const data = await response.json();
                setUserData(data);
                setUsername(data.username || '');
            } catch (error) {
                console.error(error);
                logout();
            } finally {
                setIsLoading(false);
            }
        };
        fetchUserData();
        
        // Lógica para a mensagem de status do link da Steam
        if (searchParams.get('steam_linked') === 'true') {
            setSteamLinkStatus('Sua conta Steam foi vinculada com sucesso!');
        } else if (searchParams.get('error')) {
            setSteamLinkStatus('Ocorreu um erro ao vincular sua conta Steam.');
        }
    }, [navigate, logout, searchParams]);
    
    // --- Funções de Submissão dos Formulários ---

    const handleUsernameSubmit = async (e) => {
        e.preventDefault();
        setStatusMessage('Salvando...');
        const token = localStorage.getItem('userToken');
        try {
            const response = await fetch('http://localhost:5000/api/profile/username', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ username: username })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error);
            setStatusMessage(data.message);
        } catch (error) {
            setStatusMessage(`Erro: ${error.message}`);
        }
    };
    
    const handleAvatarSubmit = async (e) => {
        e.preventDefault();
        if (!avatarFile) { setStatusMessage('Por favor, selecione um arquivo de imagem.'); return; }
        setStatusMessage('Enviando...');
        const token = localStorage.getItem('userToken');
        const formData = new FormData();
        formData.append('avatar', avatarFile);

        try {
            const response = await fetch('http://localhost:5000/api/profile/avatar', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error);
            setStatusMessage(`${data.message} A página será recarregada.`);
            
            // Força o recarregamento da página para atualizar todas as informações, incluindo o avatar na navbar
            setTimeout(() => window.location.reload(), 2000);

        } catch (error) {
            setStatusMessage(`Erro: ${error.message}`);
        }
    };

    const handleAddGame = async (e) => {
        e.preventDefault();
        const inputValue = gameName;
        if (!inputValue) { setStatusMessage('Por favor, preencha o campo de busca.'); return; }
        setIsSubmitting(true);
        setStatusMessage(`Verificando "${inputValue}"...`);
        const token = localStorage.getItem('userToken');
        let requestBody = searchType === 'name' ? { game_name: inputValue } : { appid: inputValue };

        try {
            const response = await fetch('http://localhost:5000/api/profile/games', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify(requestBody)
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Ocorreu um erro.');
            setStatusMessage(data.message);
            setGameName('');
        } catch (error) {
            setStatusMessage(`Erro: ${error.message}`);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleLinkSteam = () => {
        const token = localStorage.getItem('userToken');
        if (token) {
            window.location.href = `http://localhost:5000/api/steam/link?jwt=${token}`;
        }
    };


    if (isLoading) return <div className="container"><h1>Carregando Dashboard...</h1></div>;
    if (!userData) return null;

    return (
        <div className="container" style={{maxWidth: '800px'}}>
            <header className="profile-header" style={{textAlign: 'center', marginBottom: '30px'}}>
                <h1>Painel de Controle</h1>
                <p>Gerencie suas informações, contas e jogos.</p>
            </header>

            {/* Seção para Mensagens de Status */}
            {statusMessage && <div className="content-section" style={{textAlign: 'center', borderColor: 'lightgreen'}}><p>{statusMessage}</p></div>}
            
            {/* --- SEÇÕES RESTAURADAS E FUNCIONAIS --- */}

            <div className="content-section">
                <h2>Alterar Foto de Perfil</h2>
                <form onSubmit={handleAvatarSubmit}>
                    <input type="file" onChange={e => setAvatarFile(e.target.files[0])} accept="image/png, image/jpeg, image/gif" />
                    <button type="submit" className="button-primary">Fazer Upload</button>
                </form>
            </div>

            <div className="content-section">
                <h2>Contas Vinculadas</h2>
                {steamLinkStatus && <p style={{ color: 'lightgreen' }}>{steamLinkStatus}</p>}
                {userData.steam_id ? (
                    <div className="linked-account">
                        <p>✅ Conta Steam Vinculada!</p>
                        <small>ID: {userData.steam_id}</small>
                    </div>
                ) : (
                    <div>
                        <p>Sua conta Steam ainda não foi vinculada.</p>
                        <button onClick={handleLinkSteam} className="steam-button">Vincular Steam</button>
                    </div>
                )}
            </div>
            
            <div className="content-section">
                <h2>Adicionar Jogo Platinado (Steam)</h2>
                <form onSubmit={handleAddGame}>
                    <div className="search-type-selector">
                        <label><input type="radio" name="searchType" value="name" checked={searchType === 'name'} onChange={() => setSearchType('name')} />Buscar por Nome</label>
                        <label><input type="radio" name="searchType" value="appid" checked={searchType === 'appid'} onChange={() => setSearchType('appid')} />Buscar por AppID</label>
                    </div>
                    <p>{searchType === 'name' ? 'Digite o nome de um jogo.' : 'Digite o AppID de um jogo.'}</p>
                    <input type="text" value={gameName} onChange={(e) => setGameName(e.target.value)} placeholder={searchType === 'name' ? 'Ex: Elden Ring' : 'Ex: 1245620'} disabled={isSubmitting}/>
                    <button type="submit" disabled={isSubmitting} className="button-primary" style={{marginTop: '10px'}}>
                        {isSubmitting ? 'Verificando...' : 'Adicionar e Verificar Jogo'}
                    </button>
                </form>
            </div>
            
            <div className="content-section">
                <h2>Seu Perfil Público</h2>
                <Link to={`/user/${userData.id}`} className="button-primary">Ver meu Perfil Público</Link>
            </div>
        </div>
    );
}