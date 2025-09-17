export interface TelegramUser {
  id: number;
  firstName: string;
  lastName?: string;
  username: string;
  photoUrl: string;
}

export interface Location {
  id: string;
  name: string;
  flag: string;
}

export type View = 'tasks' | 'status' | 'profile' | 'admin';
