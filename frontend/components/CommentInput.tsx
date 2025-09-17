
import React from 'react';

interface CommentInputProps {
    comments: string[];
    setComments: React.Dispatch<React.SetStateAction<string[]>>;
}

const TrashIcon: React.FC<{ className?: string }> = ({ className }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="3 6 5 6 21 6"></polyline>
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
    </svg>
);


export const CommentInput: React.FC<CommentInputProps> = ({ comments, setComments }) => {
    const maxComments = 8;

    const handleCommentChange = (index: number, value: string) => {
        const newComments = [...comments];
        newComments[index] = value;
        setComments(newComments);
    };

    const addComment = () => {
        if (comments.length < maxComments) {
            setComments([...comments, '']);
        }
    };

    const removeComment = (index: number) => {
        if (comments.length > 1) {
            const newComments = comments.filter((_, i) => i !== index);
            setComments(newComments);
        }
    };

    return (
        <div className="card rounded-2xl p-4 animate-fade-in" style={{ animationDelay: '300ms' }}>
            <h3 className="font-bold text-text-primary mb-3">💬 Коментарі ({comments.length}/{maxComments})</h3>
            <div className="space-y-3">
                {comments.map((comment, index) => (
                    <div key={index} className="flex items-center space-x-2">
                        <textarea
                            value={comment}
                            onChange={(e) => handleCommentChange(index, e.target.value)}
                            placeholder={`Коментар #${index + 1}`}
                            rows={1}
                            className="flex-grow w-full bg-card-bg/50 dark:bg-card-bg/20 border border-white/20 dark:border-gray-600 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-accent text-text-primary resize-y min-h-[40px]"
                        />
                        {comments.length > 1 && (
                            <button onClick={() => removeComment(index)} className="p-2 text-danger hover:bg-danger/20 rounded-full transition-colors">
                                <TrashIcon className="w-5 h-5" />
                            </button>
                        )}
                    </div>
                ))}
            </div>
            {comments.length < maxComments && (
                 <button onClick={addComment} className="w-full mt-4 text-sm font-semibold text-accent hover:bg-accent/10 rounded-lg py-2 transition-colors">
                    ➕ Додати коментар
                </button>
            )}
        </div>
    );
};