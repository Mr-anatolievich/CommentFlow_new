import React from 'react';
import type { TelegramUser } from '../types';

interface ProfilePageProps {
    user: TelegramUser;
}

export const ProfilePage: React.FC<ProfilePageProps> = ({ user }) => {
    return (
        <div className="card rounded-2xl p-6 text-center animate-fade-in">
             <img src={user.photoUrl} alt="User Avatar" className="w-24 h-24 rounded-full border-4 border-white/50 mx-auto" />
            <h1 className="text-2xl font-bold text-text-primary mt-4">👤 {user.firstName} {user.lastName}</h1>
             <p className="text-sm text-text-secondary">@{user.username}</p>
            <p className="text-xs text-text-secondary/70 mt-1">ID: {user.id}</p>
            <p className="text-text-secondary mt-4">Тут буде відображатися ваша профільна інформація та налаштування.</p>
        </div>
    );
};