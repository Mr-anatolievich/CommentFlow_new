
import React from 'react';
import type { TelegramUser } from '../types';

interface UserInfoProps {
    user: TelegramUser;
}

const CheckIcon: React.FC<{ className?: string }> = ({ className }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
        <polyline points="22 4 12 14.01 9 11.01"></polyline>
    </svg>
);

export const UserInfo: React.FC<UserInfoProps> = ({ user }) => {
    return (
        <div className="card rounded-2xl p-4 border-t-4 border-success animate-fade-in">
            <div className="flex items-center space-x-4">
                <img src={user.photoUrl} alt="User Avatar" className="w-12 h-12 rounded-full border-2 border-white/50" />
                <div className="flex-grow">
                    <div className="flex items-center space-x-1">
                        <h2 className="font-bold text-lg text-text-primary">Привіт, {user.firstName}!</h2>
                         <CheckIcon className="w-5 h-5 text-success" />
                    </div>
                    <p className="text-sm text-text-secondary">@{user.username}</p>
                    <p className="text-xs text-text-secondary/70 mt-1">ID: {user.id}</p>
                </div>
            </div>
        </div>
    );
};
