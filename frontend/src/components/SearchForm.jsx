import React, { useState, useEffect, useRef } from 'react';
import { ArrowLeftRight, Search, Calendar, Users, Briefcase, MapPin } from 'lucide-react';
import { searchAirports } from '../services/api';

export default function SearchForm({ onSearch, isLoading }) {
  const [tripType, setTripType] = useState('one_way'); // 'one_way' or 'round_trip'
  const [originInput, setOriginInput] = useState('Kochi (COK)');
  const [originCode, setOriginCode] = useState('COK');
  const [originSuggestions, setOriginSuggestions] = useState([]);
  const [showOriginDropdown, setShowOriginDropdown] = useState(false);

  const [destInput, setDestInput] = useState('Delhi (DEL)');
  const [destCode, setDestCode] = useState('DEL');
  const [destSuggestions, setDestSuggestions] = useState([]);
  const [showDestDropdown, setShowDestDropdown] = useState(false);

  // Set default departure date to tomorrow
  const getDefaultDates = () => {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const nextWeek = new Date(today);
    nextWeek.setDate(nextWeek.getDate() + 8);

    const format = (d) => d.toISOString().split('T')[0];
    return {
      dep: format(tomorrow),
      ret: format(nextWeek),
    };
  };

  const defaultDates = getDefaultDates();
  const [departureDate, setDepartureDate] = useState(defaultDates.dep);
  const [returnDate, setReturnDate] = useState(defaultDates.ret);
  const [adults, setAdults] = useState(1);
  const [cabinClass, setCabinClass] = useState('ECONOMY');
  const [directOnly, setDirectOnly] = useState(false);

  const originRef = useRef(null);
  const destRef = useRef(null);

  // Fetch suggestions for origin
  useEffect(() => {
    if (!originInput || originInput.length < 2) {
      setOriginSuggestions([]);
      return;
    }
    const timer = setTimeout(async () => {
      const results = await searchAirports(originInput);
      setOriginSuggestions(results);
    }, 200);
    return () => clearTimeout(timer);
  }, [originInput]);

  // Fetch suggestions for destination
  useEffect(() => {
    if (!destInput || destInput.length < 2) {
      setDestSuggestions([]);
      return;
    }
    const timer = setTimeout(async () => {
      const results = await searchAirports(destInput);
      setDestSuggestions(results);
    }, 200);
    return () => clearTimeout(timer);
  }, [destInput]);

  // Close dropdowns on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (originRef.current && !originRef.current.contains(e.target)) {
        setShowOriginDropdown(false);
      }
      if (destRef.current && !destRef.current.contains(e.target)) {
        setShowDestDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSwap = () => {
    const tempInput = originInput;
    const tempCode = originCode;
    setOriginInput(destInput);
    setOriginCode(destCode);
    setDestInput(tempInput);
    setDestCode(tempCode);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch({
      origin: originCode || originInput,
      destination: destCode || destInput,
      departure_date: departureDate,
      return_date: tripType === 'round_trip' ? returnDate : null,
      adults: parseInt(adults, 10),
      travel_class: cabinClass,
      direct_only: directOnly,
      sort_by: 'cheapest',
    });
  };

  return (
    <div className="search-card" id="flight-search-container">
      <form onSubmit={handleSubmit}>
        {/* Trip type selector */}
        <div className="trip-type-toggle">
          <label className={`radio-label ${tripType === 'one_way' ? 'checked' : ''}`}>
            <input
              type="radio"
              name="tripType"
              value="one_way"
              checked={tripType === 'one_way'}
              onChange={() => setTripType('one_way')}
            />
            One-way
          </label>
          <label className={`radio-label ${tripType === 'round_trip' ? 'checked' : ''}`}>
            <input
              type="radio"
              name="tripType"
              value="round_trip"
              checked={tripType === 'round_trip'}
              onChange={() => setTripType('round_trip')}
            />
            Round-trip
          </label>
        </div>

        {/* Origin, Swap, Destination, Dates Grid */}
        <div className="search-grid">
          {/* Origin Input */}
          <div className="input-box" ref={originRef}>
            <label className="input-label" htmlFor="origin-field">From</label>
            <input
              id="origin-field"
              className="input-field"
              type="text"
              placeholder="City or Airport (e.g. Kochi)"
              value={originInput}
              onChange={(e) => {
                setOriginInput(e.target.value);
                setShowOriginDropdown(true);
              }}
              onFocus={() => setShowOriginDropdown(true)}
              required
            />
            {showOriginDropdown && originSuggestions.length > 0 && (
              <div className="autocomplete-dropdown" id="origin-suggestions">
                {originSuggestions.map((item) => (
                  <div
                    key={item.iata}
                    className="autocomplete-item"
                    onClick={() => {
                      setOriginInput(`${item.city} (${item.iata})`);
                      setOriginCode(item.iata);
                      setShowOriginDropdown(false);
                    }}
                  >
                    <div className="autocomplete-main">
                      <span className="airport-city">{item.city}</span>
                      <span className="airport-name">{item.name}</span>
                    </div>
                    <span className="airport-code-badge">{item.iata}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Swap Button */}
          <button
            type="button"
            id="swap-route-btn"
            className="swap-btn"
            title="Swap Origin and Destination"
            onClick={handleSwap}
          >
            <ArrowLeftRight size={18} />
          </button>

          {/* Destination Input */}
          <div className="input-box" ref={destRef}>
            <label className="input-label" htmlFor="destination-field">To</label>
            <input
              id="destination-field"
              className="input-field"
              type="text"
              placeholder="City or Airport (e.g. Delhi)"
              value={destInput}
              onChange={(e) => {
                setDestInput(e.target.value);
                setShowDestDropdown(true);
              }}
              onFocus={() => setShowDestDropdown(true)}
              required
            />
            {showDestDropdown && destSuggestions.length > 0 && (
              <div className="autocomplete-dropdown" id="dest-suggestions">
                {destSuggestions.map((item) => (
                  <div
                    key={item.iata}
                    className="autocomplete-item"
                    onClick={() => {
                      setDestInput(`${item.city} (${item.iata})`);
                      setDestCode(item.iata);
                      setShowDestDropdown(false);
                    }}
                  >
                    <div className="autocomplete-main">
                      <span className="airport-city">{item.city}</span>
                      <span className="airport-name">{item.name}</span>
                    </div>
                    <span className="airport-code-badge">{item.iata}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Departure Date */}
          <div className="input-box">
            <label className="input-label" htmlFor="departure-date-field">Departure</label>
            <input
              id="departure-date-field"
              className="input-field"
              type="date"
              value={departureDate}
              min={new Date().toISOString().split('T')[0]}
              onChange={(e) => setDepartureDate(e.target.value)}
              required
            />
          </div>

          {/* Return Date */}
          <div className="input-box" style={{ opacity: tripType === 'round_trip' ? 1 : 0.45 }}>
            <label className="input-label" htmlFor="return-date-field">Return</label>
            <input
              id="return-date-field"
              className="input-field"
              type="date"
              value={returnDate}
              min={departureDate}
              disabled={tripType !== 'round_trip'}
              onChange={(e) => setReturnDate(e.target.value)}
              required={tripType === 'round_trip'}
            />
          </div>
        </div>

        {/* Secondary options row */}
        <div className="filters-row">
          <div className="filter-controls">
            {/* Passengers */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Users size={16} color="var(--text-muted)" />
              <select
                id="adults-select"
                className="select-box"
                value={adults}
                onChange={(e) => setAdults(e.target.value)}
              >
                {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((num) => (
                  <option key={num} value={num}>
                    {num} {num === 1 ? 'Adult' : 'Adults'}
                  </option>
                ))}
              </select>
            </div>

            {/* Cabin Class */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Briefcase size={16} color="var(--text-muted)" />
              <select
                id="cabin-class-select"
                className="select-box"
                value={cabinClass}
                onChange={(e) => setCabinClass(e.target.value)}
              >
                <option value="ECONOMY">Economy</option>
                <option value="PREMIUM_ECONOMY">Premium Economy</option>
                <option value="BUSINESS">Business</option>
                <option value="FIRST">First Class</option>
              </select>
            </div>

            {/* Direct Flights Only */}
            <label className="checkbox-label" htmlFor="direct-only-check">
              <input
                id="direct-only-check"
                type="checkbox"
                checked={directOnly}
                onChange={(e) => setDirectOnly(e.target.checked)}
              />
              Direct flights only
            </label>
          </div>

          {/* Search Button */}
          <button
            type="submit"
            id="search-flights-submit-btn"
            className="search-btn"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
                <span>Searching Flights...</span>
              </>
            ) : (
              <>
                <Search size={18} />
                <span>Search Flights</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
