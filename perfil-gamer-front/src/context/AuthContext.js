// src/context/AuthContext.js
import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(localStorage.getItem('userToken'));
    const [currentUser, setCurrentUser] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    // useCallback garante que a função não seja recriada a cada renderização
    const refetchUser = useCallback(async () => {
        if (token) {
            try {
                const response = await fetch('http://localhost:5000/api/me', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (!response.ok) throw new Error("Token de autenticação falhou.");
                const userData = await response.json();
                setCurrentUser(userData);
            } catch (error) {
                console.error("Falha na autenticação:", error);
                localStorage.removeItem('userToken');
                setToken(null);
                setCurrentUser(null);
            }
        } else {
            setCurrentUser(null);
        }
    }, [token]);

    useEffect(() => {
        setIsLoading(true);
        refetchUser().finally(() => setIsLoading(false));
    }, [refetchUser]);

    const login = (newToken) => {
        localStorage.setItem('userToken', newToken);
        setToken(newToken);
    };

    const logout = () => {
        localStorage.removeItem('userToken');
        setToken(null);
    };

    // Adicionamos 'refetchUser' ao valor fornecido pelo context
    const value = { currentUser, token, isLoading, login, logout, refetchUser };

    return (
        <AuthContext.Provider value={value}>
            {!isLoading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    return useContext(AuthContext);
};