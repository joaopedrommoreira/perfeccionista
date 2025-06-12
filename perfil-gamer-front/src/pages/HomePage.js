import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function HomePage() {
    // Estados para todos os nossos dados dinâmicos
    const [topGames, setTopGames] = useState([]);
    const [topUsers, setTopUsers] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    const roadmapData = [
        {
            id: 1,
            version: "v0.1",
            title: "A Fundação",
            status: "Concluido",
            description: "Criação do Sistema Base do site, incluindo autenticação de usuários, criação de perfis e integração com a API Steam."
        },
        {
            id: 2,
            version: "v0.2",
            title: "Gamificação e Personalização",
            status: "Concluido",
            description: "Melhorias na experiência do usuário, incluindo sistema de XP, conquistas e personalização de perfis."
        },
        {
            id: 3,
            version: "v0.3",
            title: "Comunidade e Engajamento",
            status: "Em Andamento",
            description: "Refinamento do sistema de rankings, adição de comentários e feedbacks, e melhorias na interação entre usuários."
        },
        {
            id: 4,
            version: "v0.4",
            title: "Melhorias no Frontend",
            status: "Planejado",
            description: "Atualização do design do site, tornando-o mais responsivo e intuitivo, com foco na experiência do usuário."
        },
        {
            id: 5,
            version: "v0.5",
            title: "Suporte Mobile",
            status: "Planejado",
            description: "Desenvolvimento de uma versão mobile do site, garantindo que os usuários possam acessar suas informações e interagir com a comunidade de qualquer lugar."
        }
    ];

    // useEffect para buscar todos os dados da página inicial de uma só vez
useEffect(() => {
    const fetchRankingData = async () => {
        try {
            // Agora buscamos apenas os 2 rankings em paralelo
            const [topGamesResponse, topUsersResponse] = await Promise.all([
                fetch('http://localhost:5000/api/rankings/top-games'),
                fetch('http://localhost:5000/api/rankings/top-users')
            ]);

            // Verificamos se as duas respostas foram bem-sucedidas
            if (!topGamesResponse.ok || !topUsersResponse.ok) {
                throw new Error("Falha ao buscar os dados dos rankings.");
            }

            // Processamos os resultados de cada busca
            const topGamesData = await topGamesResponse.json();
            const topUsersData = await topUsersResponse.json();

            // Atualizamos nossos estados com os dados recebidos
            setTopGames(topGamesData);
            setTopUsers(topUsersData);

        } catch (error) {
            console.error("Erro ao buscar dados da página inicial:", error);
        } finally {
            setIsLoading(false);
        }
    };

    fetchRankingData();
}, []); // O array vazio [] faz com que isso rode apenas uma vez quando a página carrega

    return (
        <>
            {/* --- SEÇÃO 1: CABEÇALHO VISUAL --- */}
            <header className="page-header">
                <div className="page-header-content">
                    <img 
                        src="https://i.postimg.cc/52ncFyD0/Chat-GPT-Image-10-de-jun-de-2025-22-19-57.png" 
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
                                        <li key={game.appid} className="ranking-item">
                                            <span className="ranking-position">{index + 1}</span>
                                            <img 
                                                src={`https://cdn.cloudflare.steamstatic.com/steam/apps/${game.appid}/capsule_231x87.jpg`} 
                                                alt={game.name}
                                                className="ranking-image small"
                                            />
                                            <span className="ranking-name">{game.name}</span>
                                            <span className="ranking-value">{game.count} platinas</span>
                                        </li>
                                    ))}
                                </ol>
                            </div>
                            {/* Ranking de Usuários */}
                            <div className="ranking-list">
                                <h2 className="section-title">Usuários com Mais XP</h2>
                                <ol>
                                    {topUsers.map((user, index) => (
                                        <li key={user.id} className="ranking-item">
                                            <span className="ranking-position">{index + 1}</span>
                                            <img 
    src={user.avatar && user.avatar.startsWith('http') ? user.avatar : `http://localhost:5000${user.avatar}`} 
    alt={user.name} 
    className="ranking-image avatar" 
/>
                                            <span className="ranking-name">{user.name}</span>
                                            <span className="ranking-value">{user.xp} XP</span>
                                        </li>
                                    ))}
                                </ol>
                            </div>
                        </div>
                    )}
                </div>
</section>

<section className="roadmap-section">
    <div className="container">
        <h2 className="section-title">Nosso Roadmap</h2>
        <div className="timeline">
            {roadmapData.map(item => (
                <div key={item.id} className={`timeline-item status-${item.status.toLowerCase().replace(' ', '-')}`}>
                    <div className="timeline-dot"></div>
                    <div className="timeline-content">
                        <h3>{item.title} <span className="status-badge">{item.status}</span></h3>
                        <p>{item.description}</p>
                    </div>
                </div>
            ))}
        </div>
    </div>
</section>
        </>
    );
}