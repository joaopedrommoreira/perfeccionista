import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext'; // Importamos o useAuth para saber quem está logado

export default function PublicProfilePage() {
    const [profileData, setProfileData] = useState(null);
    const [games, setGames] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const { userId } = useParams();
    const { currentUser } = useAuth(); // Pega o usuário logado do nosso context

    useEffect(() => {
        // Para a API saber se o visitante logado segue o dono do perfil,
        // precisamos enviar o token do visitante, se ele existir.
        const token = localStorage.getItem('userToken');
        const headers = {};
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const fetchAllData = async () => {
            try {
                setIsLoading(true);
                const profileResponse = await fetch(`http://localhost:5000/api/user/${userId}`, { headers });
                if (!profileResponse.ok) throw new Error("Perfil não encontrado.");
                const data = await profileResponse.json();
                setProfileData(data);

                const gamesResponse = await fetch(`http://localhost:5000/api/user/${userId}/platinados`);
                if (gamesResponse.ok) {
                    const gamesData = await gamesResponse.json();
                    setGames(gamesData.games || []);
                }
            } catch (err) {
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };

        fetchAllData();
    }, [userId]); // Roda sempre que o ID na URL mudar

    const handleFollowToggle = async () => {
        const token = localStorage.getItem('userToken');
        if (!token) {
            alert("Você precisa estar logado para seguir usuários.");
            return;
        }

        // Determina se a ação é 'follow' ou 'unfollow'
        const action = profileData.is_followed_by_viewer ? 'unfollow' : 'follow';
        
        try {
            const response = await fetch(`http://localhost:5000/api/user/${userId}/${action}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                // Atualiza a tela imediatamente para a melhor experiência do usuário
                setProfileData(prev => ({
                    ...prev,
                    is_followed_by_viewer: !prev.is_followed_by_viewer,
                    followers_count: action === 'follow' ? prev.followers_count + 1 : prev.followers_count - 1
                }));
            } else {
                const data = await response.json();
                alert(`Erro: ${data.error || 'Ocorreu um erro.'}`);
            }
        } catch (error) {
            alert("Ocorreu um erro de rede. Tente novamente.");
        }
    };

    const getAvatarUrl = () => {
        if (!profileData) return '/default-avatar.png';
        if (profileData.picture_url && profileData.picture_url.startsWith('/api/')) return `http://localhost:5000${profileData.picture_url}`;
        if (profileData.steam_avatar_url) return profileData.steam_avatar_url;
        if (profileData.picture_url) return profileData.picture_url;
        return '/default-avatar.png';
    };

    if (isLoading) return <div className="container"><h1>Carregando Perfil...</h1></div>;
    if (error) return <div className="container"><h1>Erro: {error}</h1></div>;
    if (!profileData) return <div className="container"><h1>Perfil não encontrado.</h1></div>;

return (
    <div className="profile-page-container">
        <header 
            className="profile-banner" 
            style={{ backgroundImage: `url(${profileData.equipped_banner_url || '/default-banner.jpg'})` }}
        />
        <div className="container">
            <div className="profile-main-content">
                {/* --- HEADER DO PERFIL COM NOVO LAYOUT --- */}
                <div className="profile-user-info-header">
                    <img src={getAvatarUrl()} alt={profileData.name} className="profile-avatar-large" />
                    <div className="profile-header-center">
                        <h1>{profileData.username || profileData.steam_name || profileData.name}</h1>
                        <div className="platform-icons">
                            {profileData.steam_id && <img src="https://upload.wikimedia.org/wikipedia/commons/8/83/Steam_icon_logo.svg" alt="Steam"/>}
                        </div>
                    </div>
                    <div className="profile-header-social">
                        <div className="follow-stats">
                            <div className="follow-stat-item">
                                <strong>{profileData.followers_count}</strong>
                                <span>Seguidores</span>
                            </div>
                            <div className="follow-stat-item">
                                <strong>{profileData.following_count}</strong>
                                <span>Seguindo</span>
                            </div>
                        </div>
                        {currentUser && currentUser.id !== profileData.id && (
                            <button onClick={handleFollowToggle} className="button-primary follow-button">
                                {profileData.is_followed_by_viewer ? 'Deixar de Seguir' : 'Seguir'}
                            </button>
                        )}
                    </div>
                </div>

                {/* STATS DE JOGOS (REMOVEMOS OS DE SEGUIDORES DAQUI) */}
                
                {/* O restante da página continua igual */}
                    <div className="profile-games-section">
                        <h2 className="title-platina">Jogos Platinados ({games.length})</h2>
                        <div className="games-grid-public">
                            {games.length > 0 ? games.map(game => (
                                // --- NOVO CARD DE JOGO PLATINADO ---
                                <div key={game.appid} className="profile-game-card">
                                    <img 
                                        src={`https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/${game.appid}/header.jpg`} 
                                        alt={game.name} 
                                    />
                                </div>
                            )) : (
                                <p>Nenhum jogo platinado para exibir ainda.</p>
                            )}
                        </div>
                    </div>
            </div>
        </div>
    </div>
);
}