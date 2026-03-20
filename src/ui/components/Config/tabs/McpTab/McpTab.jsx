// src/sdk/components/config/tabs/McpTab/McpTab.jsx
import React, { useState, useEffect } from 'react';
import { useLocation } from "react-router-dom";

// Componentes internos del SDK
import McpTestMode from './utils/McpTestMode';
import { MCPSearchPanel } from '../../../SearchBar/utils/MCPSearchPanel'; 

// Hooks y Core del SDK
import { useJarvis } from '../../../../../hooks/useJarvis';
import apiClient from '../../../../../core/client'; // Tu cliente axios del SDK
import Logger from '../../../../../utils/logger';

// Iconos
import { FcGoogle } from 'react-icons/fc';
import { AiOutlineCloudServer } from 'react-icons/ai';
import { SiNotion, SiMysql, SiMicrosoftaccess } from 'react-icons/si';
import { IoPrismOutline } from 'react-icons/io5';
import { FaGithub, FaCheckCircle, FaTimesCircle } from 'react-icons/fa';

import './McpTab.css';

const log = new Logger('McpTab');

const McpTab = () => {
  const [mainView, setMainView] = useState('');
  const location = useLocation();
  
  // Obtenemos la lógica desde el SDK
  const { connectGoogleCalendar, serviceConnections, setServiceConnections } = useJarvis();
  const [connectingService, setConnectingService] = useState(null);

  const integrationApi = {
    getStatus: async () => {
      const response = await apiClient.get('/api/v1/integrations/status'); 
      return response.data;
    },
    disconnect: async (provider) => {
      const response = await apiClient.post(`/api/v1/integrations/disconnect/${provider}`);
      return response.data;
    }
  };

  const fetchIntegrationStatus = async () => {
    try {
      const status = await integrationApi.getStatus();
      // Actualizamos el estado global del SDK
      if (setServiceConnections) setServiceConnections(status);
    } catch (error) {
      log.error("Error fetching integration status:", error);
    }
  };

  useEffect(() => {
    fetchIntegrationStatus();
    const params = new URLSearchParams(location.search);
    if (params.get("connection_success") || params.get("error")) {
      window.history.replaceState({}, "", location.pathname);
    }
  }, [location.search]);

  const handleServiceConnect = async (serviceName) => {
    setConnectingService(serviceName);
    try {
      if (serviceName === 'google_calendar') {
        await connectGoogleCalendar(); // Usamos la función del SDK
      } else {
        // Simulación para otros servicios
        await new Promise(resolve => setTimeout(resolve, 1500));
        if (setServiceConnections) {
          setServiceConnections(prev => ({ ...prev, [serviceName]: true }));
        }
        alert(`${serviceName} connected (Simulated)`);
      }
    } catch (error) {
      log.error(`Error connecting to ${serviceName}:`, error);
    } finally {
      if (serviceName !== 'google_calendar') setConnectingService(null);
    }
  };

  const handleServiceDisconnect = async (serviceName) => {
    try {
      await integrationApi.disconnect(serviceName); 
      await fetchIntegrationStatus();
    } catch (error) {
      log.error(`Error disconnecting ${serviceName}:`, error);
    }
  };

  // Sub-componente de tarjeta (local)
  const ServiceConnectionCard = ({ service, icon, name, description, connected, onConnect, onDisconnect, isConnecting, badge }) => (
    <div className={`service-connection-card ${connected ? 'connected' : ''}`}>
      <div className="service-connection-header">
        <div className="service-connection-icon">{icon}</div>
        <div className="service-connection-info">
          <h4 className="service-connection-name">
            {name}
            {badge && <span className="service-connection-badge developing"> {badge}</span>}
          </h4>
          <p className="service-connection-description">{description}</p>
        </div>
        <div className="service-connection-status">
          {connected ? <FaCheckCircle className="status-icon connected" /> : <FaTimesCircle className="status-icon disconnected" />}
        </div>
      </div>
      <div className="service-connection-actions">
        {!connected ? (
          <button className="service-connect-btn" onClick={() => onConnect(service)} disabled={isConnecting}>
            {isConnecting ? 'Conectando...' : 'Conectar'}
          </button>
        ) : (
          <button className="service-disconnect-btn" onClick={() => onDisconnect(service)}>Disconnect</button>
        )}
      </div>
    </div>
  );

  // VISTAS
  if (mainView === 'server') {
    return (
      <div className="mcp-tab-container">
        <MCPSearchPanel />
        <div className="mcp-footer">
          <button onClick={() => setMainView('')} className="mcp-back-button red">Back</button>
        </div>
      </div>
    );
  }

  if (mainView === 'prueba') {
    return <McpTestMode setMainView={setMainView} />;
  }

  return (
    <div className="mcp-main-view">
      <h2 className="mcp-main-title">Model Context Protocol</h2>
      <div className="service-connections-section">
        <div className="service-connections-grid">
          <ServiceConnectionCard
            service="google_calendar"
            icon={<FcGoogle size={32} />}
            name="Google Calendar"
            description="Manage events"
            connected={serviceConnections?.google_calendar}
            onConnect={handleServiceConnect}
            onDisconnect={handleServiceDisconnect}
            isConnecting={connectingService === 'google_calendar'}
          />
          {/* ... Repetir para GitHub, MySQL, etc ... */}
          <ServiceConnectionCard
            service="github"
            icon={<FaGithub size={32} color="#fff" />}
            name="GitHub"
            description="Manage repos"
            connected={serviceConnections?.github}
            onConnect={handleServiceConnect}
            onDisconnect={handleServiceDisconnect}
            isConnecting={connectingService === 'github'}
          />
        </div>
      </div>

      <div className="mcp-main-buttons">
        <button onClick={() => setMainView('server')} className="mcp-main-button server">
          <AiOutlineCloudServer size={48} color="#fff" />
          <span>Server</span>
        </button>
        <button onClick={() => setMainView('prueba')} className="mcp-main-button prueba">
          <IoPrismOutline size={48} color="#fff" />
          <span>Test</span>
        </button>
      </div>
    </div>
  );
};

export default McpTab;