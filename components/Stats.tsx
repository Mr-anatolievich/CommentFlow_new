
import React from 'react';
import type { Location } from '../types';

interface StatsProps {
    location: Location;
    commentCount: number;
    linkCount: number;
}

const StatCard: React.FC<{ icon: string; title: string; value: string; color: string }> = ({ icon, title, value, color }) => (
    <div className="card text-center p-3 rounded-xl flex-1">
        <div className={`text-2xl ${color}`}>{icon}</div>
        <div className="text-xs text-text-secondary mt-1">{title}</div>
        <div className="font-bold text-sm text-text-primary truncate">{value}</div>
    </div>
);

export const Stats: React.FC<StatsProps> = ({ location, commentCount, linkCount }) => {
    return (
        <div className="flex gap-2 animate-fade-in" style={{ animationDelay: '100ms' }}>
            <StatCard icon="🌍" title="Локація" value={location.name} color="" />
            <StatCard icon="💬" title="Коментарі" value={`${commentCount}/8`} color="" />
            <StatCard icon="🔗" title="Посилання" value={`${linkCount}`} color="" />
        </div>
    );
};
