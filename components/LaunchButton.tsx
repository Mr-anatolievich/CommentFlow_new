
import React from 'react';

interface LaunchButtonProps {
    isLoading: boolean;
    isDisabled: boolean;
    onClick: () => void;
}

const Spinner: React.FC = () => (
    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
);

export const LaunchButton: React.FC<LaunchButtonProps> = ({ isLoading, isDisabled, onClick }) => {
    const buttonClasses = `
        w-full text-white font-bold py-3.5 px-6 rounded-xl shadow-lg
        transform transition-all duration-300
        flex items-center justify-center min-h-[50px]
        ${isLoading ? 'cursor-wait' : ''}
        ${isDisabled ? 'opacity-50 cursor-not-allowed bg-gray-400 dark:bg-gray-600' : 'btn-primary hover:scale-105 hover:shadow-2xl'}
    `;

    return (
        <button onClick={onClick} disabled={isLoading || isDisabled} className={buttonClasses}>
            {isLoading ? (
                <>
                    <Spinner />
                    <span>Запускаємо...</span>
                </>
            ) : (
                <span>🚀 Запустити завдання</span>
            )}
        </button>
    );
};
