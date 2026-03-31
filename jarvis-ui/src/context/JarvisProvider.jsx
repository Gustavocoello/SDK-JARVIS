// src/sdk/context/JarvisProvider.jsx
import React, { createContext, useContext, useMemo, useEffect, useState } from 'react';
import { createChatClient } from '../core/client';
import { streamLogger } from '../utils/logger';

export const JarvisContext = createContext(null);

export const JarvisProvider = ({ children, config = {} }) => {
  const [isInitializing, setIsInitializing] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  const client = useMemo(() => createChatClient({
    baseURL: config.baseURL,
    getToken: config.getToken,
    appId: config.appId || 'jarvis-sdk',
  }), [config.baseURL, config.getToken, config.appId]);

  useEffect(() => {
    const init = async () => {
      if (!config.getToken) {
        setIsInitializing(false);
        return;
      }
      try {
        const token = await config.getToken();
        console.log('[jarvis-sdk] init con baseURL:', config.baseURL);
        console.log('[jarvis-sdk] getToken existe:', !!config.getToken);
        if (token) {
          setIsAuthenticated(true);
          try {
            const response = await client.get('/api/v1/user/profile');
            const userData = response.data?.user || response.data;
            setUser(userData);
            streamLogger.info('✅ SDK User cargado:', userData);
          } catch (syncError) {
            streamLogger.error('Error cargando perfil:', syncError);
          }
        }
      } catch (e) {
        streamLogger.error('Error obteniendo token:', e);
      } finally {
        setIsInitializing(false);
      }
    };

    init();
  }, [config.getToken]);

  const value = useMemo(() => ({
    version: '2026.1.0',
    client,
    getToken: config.getToken,
    isAuthenticated,
    isInitializing,
    user,
    logout: config.logout || (() => {
      console.warn('[jarvis-sdk] logout llamado sin handler configurado');
    }),
  }), [client, config.getToken, isAuthenticated, isInitializing, user, config.logout]);

  return (
    <JarvisContext.Provider value={value}>
      <div className="jarvis-sdk-container" data-theme={config.theme || 'dark'}>
        {children}
      </div>
    </JarvisContext.Provider>
  );
};

export const useJarvis = () => {
  const context = useContext(JarvisContext);
  if (!context) throw new Error('useJarvis debe usarse dentro de JarvisProvider');
  return context;
};

