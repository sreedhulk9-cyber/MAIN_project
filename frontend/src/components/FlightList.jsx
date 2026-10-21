import React, { useState } from 'react';
import FlightCard from './FlightCard';
import { ArrowDownUp, PlaneTakeoff, Info } from 'lucide-react';

export default function FlightList({ searchResponse, isLoading, error }) {
  const [activeSort, setActiveSort] = useState('cheapest'); // 'cheapest', 'fastest', 'stops'

  if (isLoading) {
    return (
      <div className="loading-box" id="flights-loading-state">
        <div className="spinner"></div>
        <p style={{ fontSize: '1.05rem', fontWeight: 600 }}>Connecting to Flight Provider...</p>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Retrieving schedules, fares, and real-time seat availability
        </span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-banner" id="flights-error-state">
        <Info size={20} />
        <div>
          <strong>Flight Search Error:</strong> {error}
        </div>
      </div>
    );
  }

  if (!searchResponse || !searchResponse.flights || searchResponse.flights.length === 0) {
    return (
      <div className="empty-box" id="flights-empty-state">
        <PlaneTakeoff size={48} style={{ opacity: 0.4 }} />
        <div className="empty-title">Ready for Departure</div>
        <p style={{ marginTop: '0.4rem', fontSize: '0.9rem' }}>
          Select your departure city, destination, and travel dates above to search live flights.
        </p>
      </div>
    );
  }

  const { flights, results_count, is_live, source, retrieved_at, cheapest_flight, fastest_flight } = searchResponse;

  // Local sorting
  const sortedFlights = [...flights].sort((a, b) => {
    if (activeSort === 'fastest') {
      return a.duration_minutes - b.duration_minutes;
    }
    if (activeSort === 'stops') {
      return a.stops - b.stops;
    }
    return a.price - b.price; // cheapest default
  });

  const formattedTime = retrieved_at ? new Date(retrieved_at).toLocaleTimeString() : 'Just now';

  return (
    <section id="flight-results-section">
      <div className="results-header">
        <div className="results-meta">
          <span className="results-count" id="results-count-text">
            {results_count} {results_count === 1 ? 'Flight Found' : 'Flights Found'}
          </span>
          <span className={`source-badge ${is_live ? '' : 'demo'}`}>
            Source: {source} · {formattedTime}
          </span>
        </div>

        {/* Sort Controls */}
        <div className="sort-group">
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 600 }}>
            Sort by:
          </span>
          <button
            id="sort-cheapest-btn"
            className={`sort-btn ${activeSort === 'cheapest' ? 'active' : ''}`}
            onClick={() => setActiveSort('cheapest')}
          >
            Cheapest
          </button>
          <button
            id="sort-fastest-btn"
            className={`sort-btn ${activeSort === 'fastest' ? 'active' : ''}`}
            onClick={() => setActiveSort('fastest')}
          >
            Fastest
          </button>
          <button
            id="sort-stops-btn"
            className={`sort-btn ${activeSort === 'stops' ? 'active' : ''}`}
            onClick={() => setActiveSort('stops')}
          >
            Fewest Stops
          </button>
        </div>
      </div>

      <div className="flight-list">
        {sortedFlights.map((flight) => {
          const isCheapest = cheapest_flight && flight.id === cheapest_flight.id;
          const isFastest = fastest_flight && flight.id === fastest_flight.id;
          return (
            <FlightCard
              key={flight.id}
              flight={flight}
              isCheapest={isCheapest}
              isFastest={isFastest}
            />
          );
        })}
      </div>
    </section>
  );
}
