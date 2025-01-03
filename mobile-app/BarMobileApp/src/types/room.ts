import { User } from '../api/types';

export interface Room {
  id: number;
  name: string;
  channel_name: string;
  owner_id: number;
  is_active: boolean;
  room_type: 'voice' | 'video';
  max_participants: number;
  current_participants: number;
  participants?: RoomParticipant[];
  created_at?: string;
  updated_at?: string;
}

export interface RoomParticipant {
  id: number;
  user: User;
  room_id: number;
  joined_at: string;
  is_speaking?: boolean;
  is_muted?: boolean;
  is_video_enabled?: boolean;
  connection_status: 'connecting' | 'connected' | 'disconnected';
}

export interface RoomState {
  rooms: Room[];
  currentRoom: Room | null;
  isLoading: boolean;
  error: string | null;
  participants: RoomParticipant[];
}

export interface RoomActions {
  joinRoom: (roomId: number) => Promise<void>;
  leaveRoom: () => Promise<void>;
  createRoom: (name: string, type: 'voice' | 'video') => Promise<void>;
  toggleMute: () => void;
  toggleVideo: () => void;
}
