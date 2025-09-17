
import React from 'react';
import type { Location } from '../types';

interface LocationSelectorProps {
    locations: Location[];
    selectedLocation: Location;
    onSelect: (location: Location) => void;
}

export const LocationSelector: React.FC<LocationSelectorProps> = ({ locations, selectedLocation, onSelect }) => {
    
    const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const selectedId = event.target.value;
        const location = locations.find(loc => loc.id === selectedId);
        if (location) {
            onSelect(location);
        }
    };

    return (
        <div className="card rounded-2xl p-4 animate-fade-in" style={{ animationDelay: '200ms' }}>
            <label htmlFor="location-select" className="block text-sm font-medium text-text-secondary mb-2">
                🌍 Вибір локації
            </label>
            <div className="relative">
                <select
                    id="location-select"
                    value={selectedLocation.id}
                    onChange={handleChange}
                    className="w-full appearance-none bg-card-bg/50 dark:bg-card-bg/20 border border-white/20 dark:border-gray-600 rounded-lg py-3 px-4 leading-tight focus:outline-none focus:ring-2 focus:ring-accent text-text-primary"
                >
                    {locations.map((location) => (
                        <option key={location.id} value={location.id}>
                            {location.flag} {location.name}
                        </option>
                    ))}
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-text-secondary">
                    <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                        <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/>
                    </svg>
                </div>
            </div>
        </div>
    );
};