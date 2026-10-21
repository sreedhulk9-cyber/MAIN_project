import React, { useState } from 'react';
import { Plane, Clock, ChevronDown, ChevronUp, ExternalLink, ShieldAlert } from 'lucide-react';

export default function FlightCard({ flight, isCheapest, isFastest }) {
  const [expanded, setExpanded] = useState(false);

  // Format currency
  const formatPrice = (price, curr) => {
    if (curr === 'INR') {
      return `₹${price.toLocaleString('en-IN')}`;
    }
    return `${curr} ${price.toLocaleString()}`;
  };

  // Format time (e.g. 2026-11-15T06:15:00 -> 06:15)
  const formatClock = (isoStr) => {
    if (!isoStr) return '--:--';
    if (isoStr.includes('T')) {
      const parts = isoStr.split('T')[1].split(':');
      return `${parts[0]}:${parts[1]}`;
    }
    return isoStr;
  };

  // Format date
  const formatDate = (isoStr) => {
    if (!isoStr) return '';
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } catch {
      return '';
    }
  };

  return (
    <div
      className={`flight-card ${isCheapest ? 'best-deal' : ''}`}
      id={`flight-card-${flight.id}`}
    >
      {/* Badges */}
      {isCheapest && <div className="deal-ribbon">Cheapest Deal</div>}
      {!isCheapest && isFastest && <div className="deal-ribbon fastest">Fastest</div>}

      <div className="flight-card-main">
        {/* Airline Info */}
        <div className="airline-col">
          <div className="airline-avatar">
            {flight.airline_code || flight.airline.slice(0, 2).toUpperCase()}
          </div>
          <div>
            <div className="airline-name">{flight.airline}</div>
            <div className="flight-num">{flight.flight_number}</div>
            {flight.is_demo && (
              <span style={{ fontSize: '0.68rem', color: '#fbbf24', fontWeight: 700 }}>
                DEMO DATA
              </span>
            )}
          </div>
        </div>

        {/* Departure -> Duration -> Arrival Timeline */}
        <div className="timeline-col">
          {/* Departure */}
          <div className="time-box">
            <span className="flight-time">{formatClock(flight.departure_time)}</span>
            <span className="flight-iata">{flight.origin}</span>
            <span className="flight-city-label">{flight.origin_city} · {formatDate(flight.departure_time)}</span>
          </div>

          {/* Duration Line */}
          <div className="duration-line-wrapper">
            <span className="duration-text">{flight.duration}</span>
            <div className="duration-visual">
              <div className="duration-bar"></div>
              <Plane size={14} className="plane-mid-icon" />
            </div>
            <span className={`stops-tag ${flight.stops > 0 ? 'has-stops' : ''}`}>
              {flight.stops === 0 ? 'Non-stop' : `${flight.stops} Stop (${flight.stop_airports.join(', ') || '1 layover'})`}
            </span>
          </div>

          {/* Arrival */}
          <div className="time-box right">
            <span className="flight-time">{formatClock(flight.arrival_time)}</span>
            <span className="flight-iata">{flight.destination}</span>
            <span className="flight-city-label">{flight.destination_city} · {formatDate(flight.arrival_time)}</span>
          </div>
        </div>

        {/* Price & Booking */}
        <div className="price-col">
          <div className="flight-price">{formatPrice(flight.price, flight.currency)}</div>
          <div className="price-note">Total fare · {flight.cabin_class}</div>

          {flight.booking_url ? (
            <a
              href={flight.booking_url}
              target="_blank"
              rel="noopener noreferrer"
              className="book-btn"
            >
              <span>Book Flight</span>
              <ExternalLink size={14} />
            </a>
          ) : (
            <button
              className="book-btn"
              onClick={() => alert(`To book ${flight.airline} (${flight.flight_number}), visit the official ${flight.airline} portal or your preferred travel booking engine.`)}
            >
              Select Offer
            </button>
          )}

          {flight.segments && flight.segments.length > 1 && (
            <button
              onClick={() => setExpanded(!expanded)}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-secondary)',
                fontSize: '0.78rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.2rem',
                marginTop: '0.25rem',
              }}
            >
              {expanded ? 'Hide Segments' : 'View Segments'}
              {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
          )}
        </div>
      </div>

      {/* Return Flight Segment (if round trip) */}
      {flight.is_round_trip && flight.return_flight && (
        <div
          style={{
            marginTop: '1.25rem',
            paddingTop: '1.25rem',
            borderTop: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '0.85rem',
            color: 'var(--text-secondary)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>RETURN:</span>
            <span>{flight.return_flight.airline} ({flight.return_flight.flight_number})</span>
          </div>
          <div>
            Departs: {formatClock(flight.return_flight.departure_time)} → Arrives: {formatClock(flight.return_flight.arrival_time)} ({flight.return_flight.duration})
          </div>
        </div>
      )}

      {/* Expanded Segment Details */}
      {expanded && flight.segments && (
        <div
          style={{
            marginTop: '1rem',
            padding: '1rem',
            background: 'rgba(10, 13, 20, 0.6)',
            borderRadius: 'var(--radius-sm)',
            fontSize: '0.85rem',
          }}
        >
          <div style={{ fontWeight: 700, marginBottom: '0.5rem', color: '#a5b4fc' }}>
            Flight Segments:
          </div>
          {flight.segments.map((seg, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                padding: '0.35rem 0',
                borderBottom: idx < flight.segments.length - 1 ? '1px solid rgba(255,255,255,0.05)' : 'none',
              }}
            >
              <span>{seg.carrier_name} {seg.flight_number}</span>
              <span>{seg.departure_airport} ({formatClock(seg.departure_time)}) → {seg.arrival_airport} ({formatClock(seg.arrival_time)})</span>
              <span>Duration: {seg.duration}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
