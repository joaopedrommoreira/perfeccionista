import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function HomePage() {
    const [topGames, setTopGames] = useState([]);
    const [topUsers, setTopUsers] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchRankingData = async () => {
            try {
                const [topGamesResponse, topUsersResponse] = await Promise.all([
                    fetch('http://localhost:5000/api/rankings/top-games'),
                    fetch('http://localhost:5000/api/rankings/top-users')
                ]);

                if (!topGamesResponse.ok || !topUsersResponse.ok) {
                    throw new Error("Falha ao buscar os dados dos rankings.");
                }

                const topGamesData = await topGamesResponse.json();
                const topUsersData = await topUsersResponse.json();

                setTopGames(topGamesData);
                setTopUsers(topUsersData);

            } catch (error) {
                console.error("Erro ao buscar dados da página inicial:", error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchRankingData();
    }, []);

    return (
        <>
            {/* --- SEÇÃO 1: CABEÇALHO VISUAL --- */}
            <header className="page-header">
                <div className="page-header-content">
                    <img 
                        src="https://i.postimg.cc/BQTNZWVD/Chat-GPT-Image-8-de-jun-de-2025-11-01-50.png" 
                        alt="Logo Platinas PC" 
                        className="header-logo" 
                    />
                    <h1 className="header-title">Comunidade Brasileira de Platinas no PC</h1>
                </div>
            </header>

            {/* --- SEÇÃO 2: RANKINGS --- */}
            <section className="rankings-section">
                <div className="container">
                    {isLoading ? (
                        <p>Carregando rankings...</p>
                    ) : (
                        <div className="ranking-container">
                            {/* Ranking de Jogos */}
                            <div className="ranking-list">
                                <h2 className="section-title">Jogos Mais Platinados</h2>
                                <ol>
                                    {topGames.map((game, index) => (
                                        <Link to={`/jogo/${game.appid}`} key={game.appid} className="ranking-link">
                                            <li className="ranking-item">
                                                <span className="ranking-position">{index + 1}</span>
                                                <img 
                                                    src={`https://cdn.cloudflare.steamstatic.com/steam/apps/${game.appid}/capsule_231x87.jpg`} 
                                                    alt={game.name}
                                                    className="ranking-image small"
                                                />
                                                <span className="ranking-name">{game.name}</span>
                                                <span className="ranking-value">{game.count} platinas</span>
                                            </li>
                                        </Link>
                                    ))}
                                </ol>
                            </div>
                            {/* Ranking de Usuários */}
                            <div className="ranking-list">
                                <h2 className="section-title">Usuários com Mais XP</h2>
                                <ol>
                                    {topUsers.map((user, index) => (
                                        // Usamos a variável 'user' que vem do .map
                                        <Link to={`/user/${user.id}`} key={user.id} className="ranking-link">
                                            <li className="ranking-item">
                                                <span className="ranking-position">{index + 1}</span>
                                                <img 
                                                    src={user.avatar && user.avatar.startsWith('http') ? user.avatar : `http://localhost:5000${user.avatar || '/default-avatar.png'}`} 
                                                    alt={user.name} 
                                                    className="ranking-image avatar" 
                                                />
                                                <span className="ranking-name">{user.name}</span>
                                                <span className="ranking-value">{user.xp} XP</span>
                                            </li>
                                        </Link>
                                    ))}
                                </ol>
                            </div>
                        </div>
                    )}
                </div>
            </section>
        </>
    );
}