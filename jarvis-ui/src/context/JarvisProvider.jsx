// src/sdk/context/JarvisProvider.jsx
import React, { createContext, useContext, useMemo, useEffect, useState } from 'react';
import apiClient, { setAuthToken } from '../core/client';
import { streamLogger } from '../utils/logger';

export const JarvisContext = createContext(null);

export const JarvisProvider = ({ children, config = {} }) => {
  // DEBE empezar en true para que el ChatContainer espere
  const [isInitializing, setIsInitializing] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [isReasoning, setIsReasoning] = useState(false);

  useEffect(() => {
    const init = async () => {
      const appId = config?.appId || 'jarvis-sdk-unknown';
      if (config?.getToken) {
        try {
          setAuthToken(config.getToken, appId);
          const token = await config.getToken();
          if (token) {
            setIsAuthenticated(true);
            // Pedimos los datos al backend de user
            try {
              const response = await apiClient.get('/api/v1/user/profile'); // Ajusta a tu ruta de perfil
              if (response.data) {
                // Sincronizamos el objeto user con lo que viene de la DB
                setUser(response.data.user || response.data);
                const userData = response.data.user || response.data;
                setUser(userData); 
                streamLogger.info("✅ SDK User State actualizado:", userData);
              }
            } catch (syncError) {
              streamLogger.error("Error sincronizando perfil en Provider:", syncError);
            }
          }
        } catch (e) {
          streamLogger.error("Error obteniendo token", e);
        }
      } else{
        setAuthToken(null, appId)
      }
      // Finalizamos la carga pase lo que pase
      setIsInitializing(false);
    };
    
    init();
  }, [config?.getToken]);

  // Asegúrate de pasar isAuthenticated en el useMemo
  const value = useMemo(() => ({
    version:"2026.1.0",
    client: apiClient,
    getToken: config?.getToken,
    isAuthenticated, // <--- IMPORTANTE
    isInitializing,
    user,
    logout: config?.logout || (() => {
      localStorage.clear();
      window.location.href = '/';
    })
  }), [config?.getToken, isAuthenticated, isInitializing]);

  const theme = config?.theme || 'dark';

  return (
    <JarvisContext.Provider value={value}>
      <div className="jarvis-sdk-container" data-theme={theme}> 
        {children}
      </div>
    </JarvisContext.Provider>
  );
};

export const useJarvis = () => {
  const context = useContext(JarvisContext);
  if (!context) throw new Error("useJarvis debe usarse dentro de JarvisProvider");
  return context;
};