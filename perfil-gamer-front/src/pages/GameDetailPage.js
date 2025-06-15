import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';

export default function GameDetailPage() {
    const [gameData, setGameData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const { appid } = useParams();

    const [activeTab, setActiveTab] = useState('hall-da-fama');

    useEffect(() => {
        const fetchGameData = async () => {
            setIsLoading(true);
            try {
                const response = await fetch(`http://localhost:5000/api/game/${appid}`);
                if (!response.ok) {
                    const errData = await response.json();
                    throw new Error(errData.error || "Jogo não encontrado.");
                }
                const data = await response.json();
                setGameData(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };
        fetchGameData();
    }, [appid]);

    const renderActiveTabContent = () => {
        if (!gameData) return null;

        switch (activeTab) {
            case 'hall-da-fama':
                return (
                    <div className="user-grid">
                        {gameData.completers.length > 0 ? (
                            gameData.completers.map(user => (
                                <Link to={`/user/${user.id}`} key={user.id} className="user-card-link">
                                    <div className="user-card-small">
                                        <img 
                                            src={user.avatar && user.avatar.startsWith('http') ? user.avatar : `http://localhost:5000${user.avatar || '/default-avatar.png'}`} 
                                            alt={user.username}
                                        />
                                        <span>{user.username}</span>
                                    </div>
                                </Link>
                            ))
                        ) : (
                            <p>Seja o primeiro a conquistar este jogo e aparecer aqui!</p>
                        )}
                    </div>
                );
            case 'guias':
                return <p>Em breve: guias da comunidade para este jogo.</p>;
            case 'comunidade':
                return <p>Em breve: discussões e comentários sobre este jogo.</p>;
            default:
                return null;
        }
    };

    if (isLoading) return <div className="container"><h1>Carregando...</h1></div>;
    if (error) return <div className="container"><h1>Erro: {error}</h1></div>;
    if (!gameData) return <div className="container"><h1>Jogo não encontrado.</h1></div>;

    const { game, completers } = gameData;
    const gameImage = game.platform === 'steam' 
        ? `https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/${game.appid}/header.jpg`
        : 'https://cdn-1.webcatalog.io/catalog/retroachievement/retroachievement-social-preview.png?v=1726488110610';

    return (
        <div className="container">
            <div className="game-detail-card">
                <div className="game-detail-header-flex">
                    <img 
                        src={gameImage} 
                        alt={game.name}
                        className="game-detail-image"
                    />
                    <div className="game-detail-info">
                        <h1>{game.name}</h1>
                        <p className="game-detail-rewards">
                            <span className="reward-badge xp">{game.xp_value} XP</span>
                            <span className="reward-badge coin">{game.coin_value} Fichas</span>
                        </p>
                    </div>
                </div>

                <div className="tabs-container">
                    <button className={`tab-button ${activeTab === 'hall-da-fama' ? 'active' : ''}`} onClick={() => setActiveTab('hall-da-fama')}>
                        Hall da Fama ({completers.length})
                    </button>
                    <button className={`tab-button ${activeTab === 'guias' ? 'active' : ''}`} onClick={() => setActiveTab('guias')}>
                        Guias
                    </button>
                    <button className={`tab-button ${activeTab === 'comunidade' ? 'active' : ''}`} onClick={() => setActiveTab('comunidade')}>
                        Comunidade
                    </button>
                </div>

                <div className="tab-content">
                    {renderActiveTabContent()}
                </div>
            </div>
        </div>
    );
}