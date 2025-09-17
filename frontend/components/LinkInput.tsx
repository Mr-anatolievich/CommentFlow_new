
import React from 'react';

interface LinkInputProps {
    links: string[];
    setLinks: React.Dispatch<React.SetStateAction<string[]>>;
}

const TrashIcon: React.FC<{ className?: string }> = ({ className }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="3 6 5 6 21 6"></polyline>
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
    </svg>
);

export const LinkInput: React.FC<LinkInputProps> = ({ links, setLinks }) => {
    const handleLinkChange = (index: number, value: string) => {
        const newLinks = [...links];
        newLinks[index] = value;
        setLinks(newLinks);
    };

    const addLink = () => {
        setLinks([...links, '']);
    };

    const removeLink = (index: number) => {
        if (links.length > 1) {
            const newLinks = links.filter((_, i) => i !== index);
            setLinks(newLinks);
        }
    };

    return (
        <div className="card rounded-2xl p-4 animate-fade-in" style={{ animationDelay: '400ms' }}>
            <h3 className="font-bold text-text-primary mb-3">🔗 Посилання Facebook</h3>
            <div className="space-y-3">
                {links.map((link, index) => (
                    <div key={index} className="flex items-center space-x-2">
                        <input
                            type="url"
                            value={link}
                            onChange={(e) => handleLinkChange(index, e.target.value)}
                            placeholder={`https://facebook.com/post/...`}
                            className="flex-grow w-full bg-card-bg/50 dark:bg-card-bg/20 border border-white/20 dark:border-gray-600 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-accent text-text-primary"
                        />
                        {links.length > 1 && (
                            <button onClick={() => removeLink(index)} className="p-2 text-danger hover:bg-danger/20 rounded-full transition-colors">
                               <TrashIcon className="w-5 h-5" />
                            </button>
                        )}
                    </div>
                ))}
            </div>
            <button onClick={addLink} className="w-full mt-4 text-sm font-semibold text-accent hover:bg-accent/10 rounded-lg py-2 transition-colors">
                ➕ Додати посилання
            </button>
        </div>
    );
};