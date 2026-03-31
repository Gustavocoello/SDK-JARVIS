// src/sdk/core/client.jsx
import axios from 'axios';

export const createChatClient = ({ baseURL, getToken, appId = 'jarvis-sdk' }) => {
  const instance = axios.create({
    baseURL,
    headers: { 'Content-Type': 'application/json' },
    withCredentials: true,
  });

  instance.interceptors.request.use(async (config) => {
    config.headers['X-Project-Origin'] = appId;

    if (typeof getToken === 'function') {
      try {
        const token = await getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      } catch (e) {
        console.error('[jarvis-sdk] Error obteniendo token:', e);
      }
    }

    return config;
  });

  return instance;
};