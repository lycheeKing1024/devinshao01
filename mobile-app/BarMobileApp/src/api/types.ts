export interface UserPreferences {
  alcoholContent: 'none' | 'low' | 'medium' | 'high';
  flavorPreferences: string[];
  allergies: string[];
  dietaryRestrictions: string[];
  sugarPreference: 'low' | 'medium' | 'high';
}

export interface User {
  id: number;
  email: string;
  name: string;
  age: number;
  gender?: string;
  preferences: UserPreferences;
  orderHistory: {
    itemId: number;
    date: string;
    rating?: number;
    feedback?: string;
  }[];
}

export interface MenuItem {
  id: number;
  name: string;
  description: string;
  price: number;
  category: string;
  alcohol_content: number;
  flavor_profile: string[];
  ingredients: string[];
  is_available: boolean;
}

export interface ChatMessage {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
}

export interface Room {
  id: number;
  name: string;
  channel_name: string;
  owner_id: number;
  is_active: boolean;
  room_type: 'voice' | 'video';
  max_participants: number;
  current_participants: number;
}
