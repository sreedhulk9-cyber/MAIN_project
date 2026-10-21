import React from 'react';
import { X, CheckCircle2, AlertTriangle, Key, ExternalLink } from 'lucide-react';

export default function HealthModal({ healthData, onClose }) {
  if (!healthData) return null;

  const isLive = healthData.is_live_provider;

  return (
    <div className="modal-overlay" onClick={onClose} id="health-modal">
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>AgentOS Runtime & Provider Status</h3>
          <button
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Status card */}
        <div
          style={{
            padding: '1rem',
            borderRadius: 'var(--radius-md)',
            background: isLive ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
            border: `1px solid ${isLive ? 'rgba(16, 185, 129, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`,
            marginBottom: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.85rem'
          }}
        >
          {isLive ? <CheckCircle2 size={24} color="#10b981" /> : <AlertTriangle size={24} color="#f59e0b" />}
          <div>
            <div style={{ fontWeight: 700, color: isLive ? '#34d399' : '#fbbf24' }}>
              {isLive ? 'Live Flight Provider Connected' : 'Demo Flight Provider Active'}
            </div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              Provider: {healthData.provider} · Gemini API: {healthData.gemini_configured ? 'Configured' : 'Missing'}
            </div>
          </div>
        </div>

        {/* Registered Agents */}
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
            Registered AgentOS Agents:
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {healthData.registered_agents?.map((agent) => (
              <span
                key={agent}
                style={{
                  background: 'rgba(99, 102, 241, 0.15)',
                  color: '#818cf8',
                  border: '1px solid rgba(99, 102, 241, 0.3)',
                  padding: '0.3rem 0.75rem',
                  borderRadius: '999px',
                  fontSize: '0.82rem',
                  fontWeight: 600
                }}
              >
                {agent}
              </span>
            ))}
          </div>
        </div>

        {/* How to configure Live API credentials */}
        <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, marginBottom: '0.65rem' }}>
            <Key size={16} color="var(--accent-primary)" />
            <span>How to connect Live Amadeus Flights API:</span>
          </div>
          <ol style={{ paddingLeft: '1.25rem', fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            <li>Sign up for a free developer account at <strong>developers.amadeus.com</strong>.</li>
            <li>Create an app in the Self-Service Workspace to receive your <code>API Key</code> (Client ID) and <code>API Secret</code>.</li>
            <li>Add the keys to your <code>.env</code> file in the project root:
              <pre style={{
                background: '#0a0d14',
                padding: '0.5rem 0.75rem',
                borderRadius: '6px',
                marginTop: '0.35rem',
                fontFamily: 'var(--font-mono)',
                color: '#38bdf8'
              }}>
                AMADEUS_CLIENT_ID=your_api_key_here<br />
                AMADEUS_CLIENT_SECRET=your_api_secret_here
              </pre>
            </li>
            <li>Restart the backend service. AgentOS will automatically switch to Live Amadeus API queries!</li>
          </ol>
        </div>

        <button
          onClick={onClose}
          style={{
            width: '100%',
            marginTop: '1.5rem',
            padding: '0.75rem',
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            color: '#fff',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          Close
        </button>
      </div>
    </div>
  );
}
