import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Slider from "react-slick";
import "slick-carousel/slick/slick.css"; 
import "slick-carousel/slick/slick-theme.css";

export default function HomePage() {
    const [topGames, setTopGames] = useState([]);
    const [topUsers, setTopUsers] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const { currentUser } = useAuth();


    const handleLogin = () => {
        window.location.href = 'http://localhost:5000/api/auth/google/login';
    };    
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

    const sliderSettings = {
    dots: true,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    autoplay: true,
    autoplaySpeed: 5000,
    fade: true,
    cssEase: 'linear'
    };

    const newsSlides = [
  {
    id: 1,
    title: "Chegou os Jogos da Capcom!",
    description: "Agora você pode comprar e equipar banners para personalizar seu perfil público. Visite a Loja e o seu Inventário!",
    imageUrl: "https://sm.ign.com/ign_br/screenshot/default/01hyjcymm23t5ppjzba77bf3vq_bx6r.jpg" // Exemplo de imagem
  },
  {
    id: 2,
    title: "Integração com RetroAchievements Chegou!",
    description: "Vincule sua conta do RetroAchievements no Dashboard e adicione seus jogos masterizados ao seu perfil.",
    imageUrl: "https://sm.ign.com/t/ign_br/screenshot/default/bdc077c8b4bbbd099eeb421963c7f90d_3jtp.1200.jpg" // Exemplo de imagem
  },
  {
    id: 3,
    title: "Lançamento do BETA 0.5!",
    description: "Estamos felizes em anunciar o lançamento do Perfeccionista BETA 0.5!",
    imageUrl: "https://techstory.in/wp-content/uploads/2022/01/wXbZrULvucAkiwyk7xyLoe.jpg" // Exemplo de imagem
  }
];

    return (
        <>
            {/* --- SEÇÃO 1: CABEÇALHO VISUAL --- */}
            <header className="page-header">
                <div className="page-header-content">
                    <img 
                        src="https://www.pngplay.com/wp-content/uploads/13/Fortnite-Master-Chief-Transparent-Images.png" 
                        alt="Logo Platinas PC" 
                        className="header-logo" 
                    />
                    <div className="header-text-content">
                        <h1 className="header-title">Comunidade Brasileira de Platinas no PC</h1>
                        <div className="header-actions">
                            {currentUser ? (
                                <Link to="/dashboard" className="button-primary large">Ir para o Dashboard</Link>
                            ) : (
                                <button onClick={handleLogin} className="button-primary large">Junte-se à Comunidade</button>
                            )}
                        </div>
                    </div>              
                </div>
            </header>
        {/* --- NOVA SEÇÃO DE CARROSSEL DE NOVIDADES --- */}
        <section className="news-carousel-section">
            <Slider {...sliderSettings}>
                {newsSlides.map(slide => (
                    <div key={slide.id} className="news-slide">
                        <img src={slide.imageUrl} alt={slide.title} className="slide-background-image"/>
                        <div className="slide-content">
                            <h2>{slide.title}</h2>
                            <p>{slide.description}</p>
                        </div>
                    </div>
                ))}
            </Slider>
        </section>
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
                                        <Link to={`/jogo/${game.appid}`} key={`<span class="math-inline">\{game\.platform\}\-</span>{game.appid}`} className="ranking-link">
                                            <li className="ranking-item">
                                                <span className="ranking-position">{index + 1}</span>
                                                    <img 
                                                    className="ranking-image small"
                                                    alt={game.name}
                                                    // --- LÓGICA CONDICIONAL DA IMAGEM ---
                                                    src={
                                                        game.platform === 'steam'
                                                        ? `https://cdn.cloudflare.steamstatic.com/steam/apps/${game.appid}/capsule_231x87.jpg`
                                                        : 'https://i.postimg.cc/Y2RVXmwj/Sem-T-tulo-1.png'
                                                    } 
                                                    />
                                                <span className="ranking-name">{game.name}</span>
                                                <span className="ranking-value">🏅 {game.count} platinas</span>
                                            </li>
                                        </Link>
                                    ))}
                                </ol>
                            </div>
                            {/* Ranking de Usuários */}
                            <div className="ranking-list">
                                <h2 className="section-title">🏆 Usuários com Mais XP</h2>
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
                                                <span className="ranking-value">⭐️ {user.xp} XP</span>
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