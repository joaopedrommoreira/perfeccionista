// src/pages/InventoryPage.js
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

export default function InventoryPage() {
    const [inventory, setInventory] = useState([]);
    // Novo estado para guardar o item que está selecionado
    const [selectedItem, setSelectedItem] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [statusMessage, setStatusMessage] = useState('');
    const { token } = useAuth();

    useEffect(() => {
        const fetchInventory = async () => {
            if (!token) return;
            try {
                const response = await fetch('http://localhost:5000/api/me/inventory', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const data = await response.json();
                if (!response.ok) throw new Error(data.error);
                setInventory(data);
                // Seleciona o primeiro item da lista por padrão ao carregar
                if (data.length > 0) {
                    setSelectedItem(data[0]);
                }
            } catch (error) {
                setStatusMessage(`Erro: ${error.message}`);
            } finally {
                setIsLoading(false);
            }
        };
        fetchInventory();
    }, [token]);

    const handleEquipBanner = async (inventoryId) => {
        setStatusMessage('Equipando banner...');
        try {
            const response = await fetch('http://localhost:5000/api/profile/equip-banner', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ inventory_id: inventoryId })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error);
            setStatusMessage(data.message);
        } catch (error) {
            setStatusMessage(`Erro: ${error.message}`);
        }
    };
    
    if (isLoading) return <div className="container"><h1>Carregando Inventário...</h1></div>;

    return (
        <div className="container">
            <h1>Meu Inventário</h1>
            <p>Equipe os itens cosméticos que você adquiriu na loja.</p>
            {statusMessage && <p>{statusMessage}</p>}

            <div className="inventory-layout">
                {/* --- PAINEL DA ESQUERDA: GRADE DE ITENS --- */}
                <div className="inventory-grid-panel">
                    {inventory.length > 0 ? inventory.map(invItem => (
                        <div 
                            key={invItem.inventory_id} 
                            className={`inventory-slot ${selectedItem?.inventory_id === invItem.inventory_id ? 'active' : ''}`}
                            onClick={() => setSelectedItem(invItem)}
                        >
                            <img 
                                // Usamos a imagem pequena (capsule) para a grade
                                src={`https://cdn.cloudflare.steamstatic.com/steam/apps/${invItem.appid}/capsule_231x87.jpg`} 
                                alt={invItem.name} 
                            />
                        </div>
                    )) : <p>Seu inventário está vazio.</p>}
                </div>

                {/* --- PAINEL DA DIREITA: DETALHES DO ITEM --- */}
                <div className="inventory-detail-panel">
                    {selectedItem ? (
                        <>
                            {selectedItem.item_type === 'BANNER' && (
                                <img src={selectedItem.value} alt={selectedItem.name} className="detail-item-image" />
                            )}
                            <h2>{selectedItem.name}</h2>
                            <p>{selectedItem.description}</p>
                            <button 
                                onClick={() => handleEquipBanner(selectedItem.inventory_id)} 
                                className="button-primary"
                            >
                                Equipar
                            </button>
                        </>
                    ) : (
                        <p>Selecione um item à esquerda para ver os detalhes.</p>
                    )}
                </div>
            </div>
        </div>
    );
}