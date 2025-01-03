import React, { useState, useEffect } from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { Button, Card, Text, ActivityIndicator } from 'react-native-paper';
import { Room } from '../../api/types';
import * as api from '../../api/client';

export const VoiceScreen = () => {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentRoomId, setCurrentRoomId] = useState<number | null>(null);

  useEffect(() => {
    loadRooms();
  }, []);

  const loadRooms = async () => {
    try {
      // TODO: Implement room listing API
      setRooms([
        {
          id: 1,
          name: 'Cocktail Chat',
          channel_name: 'cocktail_chat_1',
          owner_id: 1,
          is_active: true,
          room_type: 'voice',
          max_participants: 10,
          current_participants: 3,
        },
      ]);
    } catch (error) {
      console.error('Failed to load rooms:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleJoinRoom = async (roomId: number) => {
    try {
      await api.voice.joinRoom(roomId);
      setCurrentRoomId(roomId);
    } catch (error) {
      console.error('Failed to join room:', error);
    }
  };

  const handleLeaveRoom = async () => {
    if (!currentRoomId) return;
    try {
      await api.voice.leaveRoom(currentRoomId);
      setCurrentRoomId(null);
    } catch (error) {
      console.error('Failed to leave room:', error);
    }
  };

  const handleCreateRoom = async () => {
    try {
      const room = await api.voice.createRoom('New Voice Room', 'voice');
      setRooms((prev) => [...prev, room]);
    } catch (error) {
      console.error('Failed to create room:', error);
    }
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Button
        mode="contained"
        onPress={handleCreateRoom}
        style={styles.createButton}
      >
        Create Voice Room
      </Button>
      <FlatList
        data={rooms}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <Card style={styles.card}>
            <Card.Content>
              <Text variant="titleLarge">{item.name}</Text>
              <Text variant="bodyMedium">
                Participants: {item.current_participants}/{item.max_participants}
              </Text>
              <Button
                mode="contained"
                onPress={() =>
                  currentRoomId === item.id
                    ? handleLeaveRoom()
                    : handleJoinRoom(item.id)
                }
                style={styles.joinButton}
              >
                {currentRoomId === item.id ? 'Leave Room' : 'Join Room'}
              </Button>
            </Card.Content>
          </Card>
        )}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  card: {
    marginBottom: 16,
  },
  createButton: {
    marginBottom: 16,
  },
  joinButton: {
    marginTop: 8,
  },
});
