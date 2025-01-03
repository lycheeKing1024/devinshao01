import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const BASE_URL = 'https://api.bar-app.example.com';  // TODO: Configure for production

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const auth = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    await AsyncStorage.setItem('auth_token', response.data.token);
    return response.data;
  },
  logout: async () => {
    await AsyncStorage.removeItem('auth_token');
  },
};

export const menu = {
  getItems: async () => {
    const response = await api.get('/menu/items');
    return response.data;
  },
  getRecommendations: async () => {
    const response = await api.get('/menu/recommendations');
    return response.data;
  },
};

export const chat = {
  startConversation: async () => {
    const response = await api.post('/chat/start');
    return response.data;
  },
  sendMessage: async (conversationId: number, content: string) => {
    const response = await api.post(`/chat/${conversationId}/message`, { content });
    return response.data;
  },
};

export const voice = {
  createRoom: async (name: string, roomType: 'voice' | 'video') => {
    const response = await api.post('/live/rooms', { name, room_type: roomType });
    return response.data;
  },
  joinRoom: async (roomId: number) => {
    const response = await api.post(`/live/rooms/${roomId}/join`);
    return response.data;
  },
  leaveRoom: async (roomId: number) => {
    const response = await api.post(`/live/rooms/${roomId}/leave`);
    return response.data;
  },
};
