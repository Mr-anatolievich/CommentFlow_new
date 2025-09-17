
import React, { useState, useMemo } from 'react';
import type { TelegramUser, Location, View } from './types';
import { Header } from './components/Header';
import { BottomNavBar } from './components/BottomNavBar';

// Import pages
import { TasksPage } from './pages/TasksPage';
import { StatusPage } from './pages/StatusPage';
import { ProfilePage } from './pages/ProfilePage';
import { AdminPage } from './pages/AdminPage';


// Mock Telegram user data
const mockUser: TelegramUser = {
  id: 123456789,
  firstName: 'React',
  lastName: 'Dev',
  username: 'react_dev',
  photoUrl: 'https://picsum.photos/id/237/100/100',
};

const locations: Location[] = [
    { id: 'ua', name: 'Україна', flag: '🇺🇦' },
    { id: 'us', name: 'США', flag: '🇺🇸' },
    { id: 'de', name: 'Німеччина', flag: '🇩🇪' },
    { id: 'fr', name: 'Франція', flag: '🇫🇷' },
    { id: 'gb', name: 'Велика Британія', flag: '🇬🇧' },
];

const App: React.FC = () => {
    const [activeView, setActiveView] = useState<View>('tasks');

    // State for the Tasks page
    const [comments, setComments] = useState<string[]>(['']);
    const [links, setLinks] = useState<string[]>(['']);
    const [selectedLocation, setSelectedLocation] = useState<Location>(locations[0]);
    const [isLoading, setIsLoading] = useState(false);

    const isTaskReady = useMemo(() => {
        const hasComments = comments.some(c => c.trim() !== '');
        const hasLinks = links.some(l => l.trim().startsWith('https://'));
        return hasComments && hasLinks && selectedLocation !== null;
    }, [comments, links, selectedLocation]);

    const handleLaunch = () => {
        if (!isTaskReady) return;
        setIsLoading(true);
        console.log("Launching task with:", { comments, links, selectedLocation });
        setTimeout(() => {
            setIsLoading(false);
            // Here you would handle success/error
        }, 3000);
    };

    const renderContent = () => {
        switch (activeView) {
            case 'tasks':
                return <TasksPage 
                    user={mockUser}
                    locations={locations}
                    comments={comments}
                    setComments={setComments}
                    links={links}
                    setLinks={setLinks}
                    selectedLocation={selectedLocation}
                    setSelectedLocation={setSelectedLocation}
                    isLoading={isLoading}
                    isTaskReady={isTaskReady}
                    handleLaunch={handleLaunch}
                />;
            case 'status':
                return <StatusPage />;
            case 'profile':
                return <ProfilePage user={mockUser}/>;
            case 'admin':
                return <AdminPage />;
            default:
                 return <TasksPage 
                    user={mockUser}
                    locations={locations}
                    comments={comments}
                    setComments={setComments}
                    links={links}
                    setLinks={setLinks}
                    selectedLocation={selectedLocation}
                    setSelectedLocation={setSelectedLocation}
                    isLoading={isLoading}
                    isTaskReady={isTaskReady}
                    handleLaunch={handleLaunch}
                />;
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900 font-sans text-text-primary">
            <Header />
            <main className="safe-area pb-32">
                {renderContent()}
            </main>
            <BottomNavBar activeView={activeView} setActiveView={setActiveView} />
        </div>
    );
};

export default App;