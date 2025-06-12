// src/pages/ShopPage.js
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import './ShopPage.css'; // Certifique-se de ter um arquivo CSS para estilos

export default function ShopPage() {
    const [items, setItems] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [statusMessage, setStatusMessage] = useState('');
    const [redeemedKey, setRedeemedKey] = useState(null);
    const { currentUser, refetchUser } = useAuth(); 

    useEffect(() => {
        const fetchItems = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/shop/items');
                const data = await response.json();
                setItems(data);
            } catch (error) {
                console.error("Erro ao buscar itens da loja:", error);
            } finally {
                setIsLoading(false);
            }
        };
        fetchItems();
    }, []);

    const handleRedeemItem = async (itemId) => {
    setRedeemedKey(null);
    setStatusMessage('Processando resgate...');
    const token = localStorage.getItem('userToken');
    if (!token) { 
        setStatusMessage("Você precisa estar logado para resgatar itens."); 
        return; 
    }
    
    try {
        const response = await fetch(`http://localhost:5000/api/shop/buy/${itemId}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        const data = await response.json();
        if (!response.ok) {
            // Se a resposta da API não for 'ok', lança um erro com a mensagem do backend
            throw new Error(data.error || 'Ocorreu um erro desconhecido.');
        }

        // Se a compra foi bem-sucedida
        setStatusMessage(data.message);
        setRedeemedKey(data.redeemed_key); // Mostra a chave resgatada

        // CHAMA A NOVA FUNÇÃO PARA ATUALIZAR OS DADOS DO USUÁRIO EM TODO O SITE
        await refetchUser();

    } catch (error) {
        setStatusMessage(`Erro: ${error.message}`);
    }
};

    if (isLoading) return <div className="container"><h1>Carregando Loja...</h1></div>;

    return (
        <div className="container">
            <div className="shop-header">
                <div className="shop-header-content">
                    <h1>Loja de Resgate</h1>
                    <p>Use suas Fichas para resgatar chaves de jogos e outros itens digitais!</p>
                </div>
                <img 
                    src="https://i.postimg.cc/0ytMJHpW/Chat-GPT-Image-8-de-jun-de-2025-19-40-24.png" 
                    alt="Imagem Decorativa da Loja" 
                    className="shop-header-image" 
                />
            </div>
            <h1>Ùltima atualização </h1>
            <p>08/06/2025</p>

            {redeemedKey && (
                <div className="redeemed-key-container">
                    <h3>Chave Resgatada com Sucesso!</h3>
                    <p>Copie sua chave abaixo. Ela não será mostrada novamente.</p>
                    <div className="key-box">{redeemedKey}</div>
                </div>
            )}
            {statusMessage && !redeemedKey && <p>{statusMessage}</p>}

            {/* --- NOVA ESTRUTURA DE GRADE PARA A LOJA --- */}
            <div className="shop-grid">
                {items.map(item => (
                    <div key={item.id} className="shop-item-card">
                        <img 
                            src={`https://shared.cloudflare.steamstatic.com/store_item_assets/steam/apps/${item.appid}/header.jpg`} 
                            alt={item.name}
                            className="shop-item-image"
                        />
                        <div className="shop-item-content">
                            <h3>{item.name}</h3>
                            <p className="shop-item-description">{item.description}</p>
                            <div className="shop-item-footer">
                                <span className="reward-badge coin">{item.price_coins} Fichas</span>
                                <button 
                                    className="button-primary"
                                    onClick={() => handleRedeemItem(item.id)}
                                    disabled={!currentUser || currentUser.total_coins < item.price_coins || item.stock === 0}
                                >
                                    {item.stock === 0 ? 'Fora de Estoque' : 'Resgatar'}
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}