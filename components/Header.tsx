
import React from 'react';

const RobotIcon: React.FC<{ className?: string }> = ({ className }) => (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zM8.5 12c.83 0 1.5-.67 1.5-1.5S9.33 9 8.5 9 7 9.67 7 10.5 7.67 12 8.5 12zm7 0c.83 0 1.5-.67 1.5-1.5S16.33 9 15.5 9s-1.5.67-1.5 1.5.67 1.5 1.5 1.5zM12 16.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/>
    </svg>
);


export const Header: React.FC = () => {
    return (
        <header className="header-gradient text-white p-4 pt-6 shadow-lg safe-area">
            <div className="flex items-center space-x-3">
                <RobotIcon className="w-10 h-10" />
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">CommentFlow</h1>
                    <p className="text-sm text-white/80">Автоматизація коментарів у Facebook</p>
                </div>
            </div>
        </header>
    );
};
