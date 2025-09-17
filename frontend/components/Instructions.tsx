
import React from 'react';

const InstructionStep: React.FC<{ number: string; text: string }> = ({ number, text }) => (
    <li className="flex items-start space-x-3">
        <span className="text-xl font-bold text-accent">{number}</span>
        <span className="text-text-secondary pt-1">{text}</span>
    </li>
);

export const Instructions: React.FC = () => {
    return (
        <div className="card rounded-2xl p-4 animate-fade-in" style={{ animationDelay: '500ms' }}>
            <h3 className="font-bold text-text-primary mb-3">Як це працює?</h3>
            <ul className="space-y-2 text-sm">
                <InstructionStep number="1️⃣" text="Виберіть країну для проксі." />
                <InstructionStep number="2️⃣" text="Додайте коментарі (до 8 штук)." />
                <InstructionStep number="3️⃣" text="Вставте посилання на пости Facebook." />
                <InstructionStep number="4️⃣" text="Натисніть 'Запустити' і очікуйте." />
            </ul>
        </div>
    );
};