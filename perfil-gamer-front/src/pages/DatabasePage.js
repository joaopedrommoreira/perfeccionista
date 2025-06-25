// src/pages/DatabasePage.js
import React, { useState, useEffect } from 'react';

export default function DatabasePage() {
    const [allGames, setAllGames] = useState([]); // Guarda a lista original de jogos
    const [isLoading, setIsLoading] = useState(true);
    
    // --- NOVO ESTADO PARA O TERMO DE BUSCA ---
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const fetchGames = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/games');
                const data = await response.json();
                setAllGames(data); // Salva a lista completa
            } catch (error) {
                console.error("Erro ao buscar dados dos jogos:", error);
            } finally {
                setIsLoading(false);
            }
        };
        fetchGames();
    }, []);

    // --- NOVA LÓGICA DE FILTRAGEM ---
    // Filtra a lista de jogos ANTES de renderizar
    const filteredGames = allGames.filter(game =>
        game.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (isLoading) return <div className="container"><h1>Carregando Banco de Dados...</h1></div>;

    return (
        <div className="container" style={{maxWidth: '1200px'}}>
            <h1>Banco de Dados de Jogos</h1>
            <p>Veja todos os jogos registrados no nosso sistema e suas recompensas.</p>
            
            {/* --- NOVO CAMPO DE BUSCA --- */}
            <input
              type="text"
              placeholder="Buscar por nome do jogo..."
              className="database-search-input"
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
            />
            
            <table className="database-table">
                <thead>
                    <tr>
                        <th>Jogo</th>
                        <th>Plataforma</th>
                        <th>Dificuldade</th>
                        <th>XP</th>
                        <th>Fichas</th>
                    </tr>
                </thead>
                <tbody>
                    {/* Agora usamos a lista FILTRADA para renderizar */}
                    {filteredGames.map(game => (
                        <tr key={game.id}>
                            <td className="game-title-cell">
                                <img 
                                    src={game.platform === 'Steam' 
                                        ? `https://cdn.cloudflare.steamstatic.com/steam/apps/${game.appid}/capsule_231x87.jpg`
                                        : 'https://cdn-1.webcatalog.io/catalog/retroachievement/retroachievement-social-preview.png?v=1726488110610'
                                    } 
                                    alt={game.name}
                                    className="game-icon-table"
                                />
                                {game.name}
                            </td>
                            <td>{game.platform}</td>
                            <td>{game.difficulty}</td>
                            <td>{game.xp_value}</td>
                            <td>{game.coin_value}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            {/* Mensagem para o caso de a busca não retornar nada */}
            {filteredGames.length === 0 && !isLoading && (
                <p style={{marginTop: '20px'}}>Nenhum jogo encontrado com o termo "{searchTerm}".</p>
            )}
        </div>
    );
}