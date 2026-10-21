import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import SearchForm from './components/SearchForm';
import FlightList from './components/FlightList';
import ChatBox from './components/ChatBox';
import HealthModal from './components/HealthModal';
import { fetchHealth, searchFlights } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('search');
  const [healthData, setHealthData] = useState(null);
  const [isHealthModalOpen, setIsHealthModalOpen] = useState(false);

  const [searchResponse, setSearchResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHealth()
      .then(setHealthData)
      .catch((err) => console.warn('Could not fetch backend health:', err));
  }, []);

  // Initial demo search on load so the user sees results immediately
  useEffect(() => {
    handleSearch({
      origin: 'COK',
      destination: 'DEL',
      departure_date: new Date(Date.now() + 86400000).toISOString().split('T')[0],
      adults: 1,
      travel_class: 'ECONOMY',
      direct_only: false,
      sort_by: 'cheapest',
    });
  }, []);

  const handleSearch = async (params) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await searchFlights(params);
      setSearchResponse(data);
    } catch (err) {
      setError(err.message || 'Failed to search flights');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-wrapper">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        healthData={healthData}
        onOpenInfoModal={() => setIsHealthModalOpen(true)}
      />

      <main className="main-content">
        {activeTab === 'search' ? (
          <div>
            <div className="page-header">
              <h1 className="page-title">
                Find & Compare <span className="page-title-gradient">Flights Globally</span>
              </h1>
              <p className="page-subtitle">
                Autonomous AI flight intelligence powered by AgentOS runtime and Gemini reasoning.
              </p>
            </div>

            <SearchForm onSearch={handleSearch} isLoading={isLoading} />

            <FlightList
              searchResponse={searchResponse}
              isLoading={isLoading}
              error={error}
            />
          </div>
        ) : (
          <div>
            <div className="page-header">
              <h1 className="page-title">
                AgentOS <span className="page-title-gradient">Conversational Assistant</span>
              </h1>
              <p className="page-subtitle">
                Natural-language flight planning, arithmetic calculations, and topic research.
              </p>
            </div>

            <ChatBox />
          </div>
        )}
      </main>

      {isHealthModalOpen && (
        <HealthModal
          healthData={healthData}
          onClose={() => setIsHealthModalOpen(false)}
        />
      )}
    </div>
  );
}
