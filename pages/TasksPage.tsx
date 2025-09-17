import React from 'react';
import type { Location, TelegramUser } from '../types';
import { UserInfo } from '../components/UserInfo';
import { LocationSelector } from '../components/LocationSelector';
import { CommentInput } from '../components/CommentInput';
import { LinkInput } from '../components/LinkInput';
import { LaunchButton } from '../components/LaunchButton';
import { Stats } from '../components/Stats';
import { Instructions } from '../components/Instructions';

interface TasksPageProps {
    user: TelegramUser;
    locations: Location[];
    comments: string[];
    setComments: (comments: string[]) => void;
    links: string[];
    setLinks: (links: string[]) => void;
    selectedLocation: Location;
    setSelectedLocation: (location: Location) => void;
    isLoading: boolean;
    isTaskReady: boolean;
    handleLaunch: () => void;
}

export const TasksPage: React.FC<TasksPageProps> = ({
    user,
    locations,
    comments,
    setComments,
    links,
    setLinks,
    selectedLocation,
    setSelectedLocation,
    isLoading,
    isTaskReady,
    handleLaunch
}) => {
    return (
        <div className="space-y-4">
             <UserInfo user={user} />
            <Stats
                location={selectedLocation}
                commentCount={comments.filter(c => c.trim() !== '').length}
                linkCount={links.filter(l => l.trim() !== '').length}
            />
            <LocationSelector
                locations={locations}
                selectedLocation={selectedLocation}
                onSelect={setSelectedLocation}
            />
            <CommentInput comments={comments} setComments={setComments} />
            <LinkInput links={links} setLinks={setLinks} />
            <Instructions />
            <div className="pt-4">
                 <LaunchButton
                    isLoading={isLoading}
                    isDisabled={!isTaskReady}
                    onClick={handleLaunch}
                />
            </div>
        </div>
    );
};
