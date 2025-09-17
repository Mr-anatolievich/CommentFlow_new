import React from 'react';
import type { View } from '../types';

// Icons as simple functional components
const ChartBarIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
);
const UserIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
);
const ClipboardListIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>
);
const WrenchIcon: React.FC<{ className?: string }> = ({ className }) => (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
);

interface NavItemProps {
    view: View;
    icon: React.ReactNode;
    label: string;
    activeView: View;
    onClick: (view: View) => void;
}

const NavItem: React.FC<NavItemProps> = ({ view, icon, label, activeView, onClick }) => {
    const isActive = activeView === view;
    const classes = `
        flex flex-col items-center justify-center w-full pt-2 pb-1
        transition-colors duration-200
        ${isActive ? 'text-accent' : 'text-text-secondary hover:text-text-primary'}
    `;
    return (
        <button onClick={() => onClick(view)} className={classes}>
            {icon}
            <span className="text-xs mt-1 font-medium">{label}</span>
        </button>
    );
};

interface BottomNavBarProps {
    activeView: View;
    setActiveView: (view: View) => void;
}

export const BottomNavBar: React.FC<BottomNavBarProps> = ({ activeView, setActiveView }) => {
    const navItems = [
        { view: 'status', icon: <ChartBarIcon className="w-6 h-6" />, label: 'Статус' },
        { view: 'profile', icon: <UserIcon className="w-6 h-6" />, label: 'Профіль' },
        { view: 'tasks', icon: <ClipboardListIcon className="w-6 h-6" />, label: 'Завдання' },
        { view: 'admin', icon: <WrenchIcon className="w-6 h-6" />, label: 'Адмін' },
    ];
    return (
        <div className="fixed bottom-0 left-0 right-0 z-20">
            <nav className="card flex justify-around border-t border-b-0 border-x-0 rounded-t-2xl rounded-b-none pl-[env(safe-area-inset-left)] pr-[env(safe-area-inset-right)] pb-[env(safe-area-inset-bottom)]">
                 {navItems.map(item => (
                    <NavItem 
                        key={item.view}
                        view={item.view as View}
                        icon={item.icon}
                        label={item.label}
                        activeView={activeView}
                        onClick={setActiveView}
                    />
                ))}
            </nav>
        </div>
    );
};
