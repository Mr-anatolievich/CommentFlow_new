import React from 'react';

export const StatusPage: React.FC = () => {
    return (
        <div className="card rounded-2xl p-6 text-center animate-fade-in">
            <h1 className="text-2xl font-bold text-text-primary">📊 Статус завдань</h1>
            <p className="text-text-secondary mt-2">Тут буде відображатися статус ваших активних та завершених завдань.</p>
        </div>
    );
};
