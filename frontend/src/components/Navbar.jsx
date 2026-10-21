import React from 'react';
import { Plane, Bot, Activity, Info, Sparkles } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, healthData, onOpenInfoModal }) {
  const isLive = healthData?.is_live_provider;

  return (
    <header className="navbar" id="agentos-navbar">
      <div className="brand-section">
        <div className="brand-logo-icon">
          <Plane size={24} />
        </div>
        <div>
          <span className="brand-name">AgentOS</span>
          <span className="brand-tag">Runtime</span>
        </div>
      </div>

      <nav className="tab-pill-group">
        <button
          id="tab-search"
          className={`tab-pill-btn ${activeTab === 'search' ? 'active' : ''}`}
          onClick={() => setActiveTab('search')}
        >
          <Plane size={16} />
          <span>Flight Search</span>
        </button>
        <button
          id="tab-chat"
          className={`tab-pill-btn ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          <Bot size={16} />
          <span>AI Agent Chat</span>
        </button>
      </nav>

      <div className="nav-actions">
        <div
          id="provider-status-badge"
          className={`status-badge ${isLive ? '' : 'demo'}`}
          title={isLive ? 'Connected to live Amadeus/Duffel provider' : 'Demo data mode active'}
          onClick={onOpenInfoModal}
          style={{ cursor: 'pointer' }}
        >
          <span className="status-dot"></span>
          <span>{isLive ? 'Live Flights API' : 'Demo Mode'}</span>
          <Info size={13} style={{ marginLeft: 2 }} />
        </div>
      </div>
    </header>
  );
}
