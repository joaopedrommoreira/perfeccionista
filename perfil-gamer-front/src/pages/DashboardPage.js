import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function DashboardPage() {
    const { logout } = useAuth();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    // Estados para os dados e formulários
    const [userData, setUserData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [username, setUsername] = useState('');
    const [avatarFile, setAvatarFile] = useState(null);
    const [gameInput, setGameInput] = useState('');
    const [searchType, setSearchType] = useState('name');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [retroUsername, setRetroUsername] = useState('');
    const [platform, setPlatform] = useState('steam');

    // Estados para as mensagens de status
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
                if (!response.ok) throw new Error('Falha ao buscar dados do usuário.');
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

        // Lógica para a mensagem de status do link da Steam que estava faltando
        if (searchParams.get('steam_linked') === 'true') {
            setSteamLinkStatus('Sua conta Steam foi vinculada com sucesso!');
        } else if (searchParams.get('error') === 'steam_link_failed') {
            setSteamLinkStatus('Ocorreu um erro ao tentar vincular sua conta Steam.');
        }
    }, [navigate, logout, searchParams]);
    
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
            setStatusMessage(`${data.message} A página será recarregada para atualizar a foto.`);
            setTimeout(() => window.location.reload(), 2000);
        } catch (error) {
            setStatusMessage(`Erro: ${error.message}`);
        }
    };

    const handleAddGame = async (e) => {
        e.preventDefault();
        if (!gameInput) { setStatusMessage('Por favor, preencha o campo de busca.'); return; }
        setIsSubmitting(true);
        setStatusMessage(`Verificando "${gameInput}"...`);
        const token = localStorage.getItem('userToken');
        const requestBody = {
        platform: platform,
        // Para RA, sempre enviamos o ID. Para Steam, pode ser nome ou ID.
        // O backend saberá como tratar.
        identifier: gameInput 
    };
        try {
            const response = await fetch('http://localhost:5000/api/profile/games', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify(requestBody)
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Ocorreu um erro.');
            setStatusMessage(data.message);
            setGameInput('');
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

    const handleLinkRetro = async (e) => {
        e.preventDefault();
        setStatusMessage('Verificando conta...');
        const token = localStorage.getItem('userToken');
        try {
            const response = await fetch('http://localhost:5000/api/profile/link-retro', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ retro_username: retroUsername })
            });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);
        setStatusMessage(data.message);
        // Força um recarregamento para mostrar o novo status de conta vinculada
        setTimeout(() => window.location.reload(), 2000);
    } catch (error) {
        setStatusMessage(`Erro: ${error.message}`);
    }
};


    if (isLoading) return <div className="container"><h1>Carregando Dashboard...</h1></div>;
    if (!userData) return null;

    return (
        <div className="container" style={{maxWidth: '800px'}}>
            <header className="profile-header" style={{textAlign: 'center', marginBottom: '30px'}}>
                <h1>Meu Painel de Controle</h1>
                <p>Gerencie suas informações, contas e jogos.</p>
            </header>

            {statusMessage && <div className="status-message-box"><p>{statusMessage}</p></div>}
            
            <div className="dashboard-panel">
                <div className="dashboard-section">
                    <h2>Configurações do Perfil</h2>
                    <div className="profile-settings-grid">
                        <div className="form-group">
                            <label htmlFor="username">Altere seu Nome</label>
                            <form onSubmit={handleUsernameSubmit} className="inline-form">
                                <input id="username" type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="Seu username" />
                                <button type="submit" className="button-primary">Salvar</button>
                            </form>
                        </div>
                        <div className="form-group">
                            <label htmlFor="avatar">Alterar Foto de Perfil</label>
                            <form onSubmit={handleAvatarSubmit} className="inline-form">
                                <input id="avatar" type="file" onChange={e => setAvatarFile(e.target.files[0])} accept="image/png, image/jpeg, image/gif" />
                                <button type="submit" className="button-primary">Upload</button>
                            </form>
                        </div>
                    </div>
                </div>

                <hr className="dashboard-divider" />

<div className="dashboard-section">
    <h2>Contas Vinculadas</h2>
    
    {/* Exibe a mensagem de status após o redirecionamento do link da Steam */}
    {steamLinkStatus && <p style={{ color: 'lightgreen', textAlign: 'center', marginBottom: '15px' }}>{steamLinkStatus}</p>}
    
    <div className="linked-accounts-list">
        
        {/* --- Lógica para a conta Steam --- */}
        {userData && userData.steam_id ? (
            <div className="account-item linked">
                ✅ Steam Vinculada
            </div>
        ) : (
            <button onClick={handleLinkSteam} className="account-item steam">
                Vincular Steam
            </button>
        )}

        {/* --- Lógica para a conta RetroAchievements --- */}
        {userData && userData.retro_username ? (
            <div className="account-item linked retro">
                <span>✅ {userData.retro_username}</span>
            </div>
        ) : (
            <form onSubmit={handleLinkRetro} className="inline-form">
                <input 
                    type="text" 
                    value={retroUsername} 
                    onChange={e => setRetroUsername(e.target.value)} 
                    placeholder="User do RetroAchievements"
                />
                <button type="submit" className="account-item retro">Vincular</button>
            </form>
        )}

        {/* --- Botão para futura integração com a Epic Games --- */}
        <button className="account-item epic" disabled>
            Vincular Epic Games
        </button>

    </div>
</div>
                
                <hr className="dashboard-divider" />

<div className="dashboard-section">
    <h2>Adicionar Jogo Masterizado</h2>

    {/* Seletor de Plataforma */}
    <div className="platform-selector">
        <button 
            className={`platform-btn ${platform === 'steam' ? 'active' : ''}`} 
            onClick={() => setPlatform('steam')}
        >
            Steam
        </button>
        <button 
            className={`platform-btn ${platform === 'retroachievements' ? 'active' : ''}`} 
            onClick={() => setPlatform('retroachievements')}
        >
            RetroAchievements
        </button>
    </div>

    <form onSubmit={handleAddGame} className="add-game-form-improved">
        <input 
            type="text" 
            value={gameInput} 
            onChange={(e) => setGameInput(e.target.value)} 
            // O placeholder muda de acordo com a plataforma selecionada
            placeholder={platform === 'steam' ? 'Nome ou AppID do jogo na Steam' : 'ID do jogo no RetroAchievements'}
            disabled={isSubmitting}
        />
        <button type="submit" disabled={isSubmitting} className="button-primary">
            {isSubmitting ? '...' : 'Verificar'}
        </button>
    </form>
</div>
            </div>
        </div>
    );
}