import React from 'react';

export const AdminPage: React.FC = () => {
    return (
        <div className="card rounded-2xl p-6 text-center animate-fade-in">
            <h1 className="text-2xl font-bold text-text-primary">🔧 Адмін панель</h1>
            <p className="text-text-secondary mt-2">Цей розділ доступний тільки для адміністраторів.</p>
        </div>
    );
};