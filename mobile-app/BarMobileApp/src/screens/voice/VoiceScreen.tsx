import React, { useState, useEffect, useRef } from 'react';
import { View, StyleSheet, FlatList, Platform } from 'react-native';
import { Button, Card, Text, ActivityIndicator, Portal, Modal } from 'react-native-paper';
import { Room, RoomState, RoomParticipant } from '../../types/room';
import * as api from '../../api/client';

// Temporary type definitions until react-native-webrtc is installed
type RTCPeerConnection = any;
type MediaStream = any;

interface RTCView {
  streamURL: string;
  style: any;
  objectFit: 'contain' | 'cover';
}

const mediaDevices = {
  getUserMedia: async (constraints: { audio: boolean; video: boolean }) => {
    console.warn('WebRTC not yet implemented');
    return null;
  }
};

export const VoiceScreen = () => {
  const [roomState, setRoomState] = useState<RoomState>({
    rooms: [],
    currentRoom: null,
    isLoading: true,
    error: null,
    participants: []
  });
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [remoteStream, setRemoteStream] = useState<MediaStream | null>(null);
  const [showCallModal, setShowCallModal] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoEnabled, setIsVideoEnabled] = useState(true);
  const peerConnection = useRef<RTCPeerConnection | null>(null);

  useEffect(() => {
    loadRooms();
  }, []);

  const loadRooms = async () => {
    try {
      setRoomState(prev => ({ ...prev, isLoading: true, error: null }));
      // TODO: Replace with actual API call when available
      const mockRooms: Room[] = [
        {
          id: 1,
          name: 'Cocktail Chat',
          channel_name: 'cocktail_chat_1',
          owner_id: 1,
          is_active: true,
          room_type: 'voice',
          max_participants: 10,
          current_participants: 3,
          participants: [],
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ];
      setRoomState(prev => ({ 
        ...prev, 
        rooms: mockRooms,
        isLoading: false 
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load rooms';
      setRoomState(prev => ({ 
        ...prev, 
        error: errorMessage,
        isLoading: false 
      }));
    }
  };

  const setupWebRTC = async () => {
    try {
      // Temporarily disabled until WebRTC package is installed
      console.warn('WebRTC functionality is temporarily disabled');
      return null;

      /* WebRTC implementation will be added here after package installation
      const stream = await mediaDevices.getUserMedia({
        audio: true,
        video: true
      });
      setLocalStream(stream);

      const configuration = { 
        iceServers: [
          { urls: 'stun:stun.l.google.com:19302' }
        ]
      };
      
      peerConnection.current = new RTCPeerConnection(configuration);
      
      stream.getTracks().forEach((track: MediaStreamTrack) => {
        peerConnection.current?.addTrack(track, stream);
      });

      peerConnection.current.ontrack = (event: RTCTrackEvent) => {
        setRemoteStream(event.streams[0]);
      };

      return stream;
      */
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Error setting up WebRTC';
      setRoomState(prev => ({ ...prev, error }));
      return null;
    }
  };

  const handleJoinRoom = async (roomId: number) => {
    try {
      setRoomState(prev => ({ ...prev, isLoading: true, error: null }));
      const response = await api.voice.joinRoom(roomId);
      const room = roomState.rooms.find(r => r.id === roomId);
      if (!room) throw new Error('Room not found');
      
      setRoomState(prev => ({ 
        ...prev, 
        currentRoom: room,
        isLoading: false,
        participants: [...prev.participants, {
          id: Date.now(),
          user: { id: 1, name: 'Current User', email: '', preferences: {} },
          room_id: roomId,
          joined_at: new Date().toISOString(),
          connection_status: 'connected'
        }]
      }));
      setShowCallModal(true);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to join room';
      setRoomState(prev => ({ 
        ...prev, 
        error: errorMessage,
        isLoading: false 
      }));
    }
  };

  const handleLeaveRoom = async () => {
    if (!roomState.currentRoom) return;
    try {
      setRoomState(prev => ({ ...prev, isLoading: true, error: null }));
      await api.voice.leaveRoom(roomState.currentRoom.id);
      
      setRoomState(prev => ({ 
        ...prev, 
        currentRoom: null,
        isLoading: false,
        participants: prev.participants.filter(p => p.room_id !== roomState.currentRoom?.id)
      }));
      setShowCallModal(false);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to leave room';
      setRoomState(prev => ({ 
        ...prev, 
        error: errorMessage,
        isLoading: false 
      }));
    }
  };

  const handleCreateRoom = async () => {
    try {
      setRoomState(prev => ({ ...prev, isLoading: true, error: null }));
      const room = await api.voice.createRoom('New Voice Room', 'voice');
      setRoomState(prev => ({ 
        ...prev, 
        rooms: [...prev.rooms, room],
        isLoading: false 
      }));
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to create room';
      setRoomState(prev => ({ 
        ...prev, 
        error: errorMessage,
        isLoading: false 
      }));
    }
  };

  if (roomState.isLoading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" />
        <Text style={styles.loadingText}>Loading rooms...</Text>
      </View>
    );
  }
  
  if (roomState.error) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>{roomState.error}</Text>
        <Button mode="contained" onPress={loadRooms} style={styles.retryButton}>
          Retry
        </Button>
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
        data={roomState.rooms}
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
                  roomState.currentRoom?.id === item.id
                    ? handleLeaveRoom()
                    : handleJoinRoom(item.id)
                }
                style={styles.joinButton}
                loading={roomState.isLoading}
                disabled={roomState.isLoading}
              >
                {roomState.currentRoom?.id === item.id ? 'Leave Room' : 'Join Room'}
              </Button>
            </Card.Content>
          </Card>
        )}
      />

      <Portal>
        <Modal
          visible={showCallModal}
          onDismiss={handleLeaveRoom}
          contentContainerStyle={styles.modalContent}
        >
          <View style={styles.callContainer}>
            {/* Video streams will be enabled after WebRTC package installation */}
            <View style={styles.localStream}>
              <Text style={styles.streamText}>Local Video Preview</Text>
              {localStream && <Text style={styles.streamStatus}>Local Stream Active</Text>}
            </View>
            <View style={styles.remoteStream}>
              <Text style={styles.streamText}>Remote Video Preview</Text>
              {remoteStream && <Text style={styles.streamStatus}>Remote Stream Active</Text>}
            </View>
            <View style={styles.controlsContainer}>
              <Button
                mode="contained"
                onPress={() => setIsMuted(!isMuted)}
                style={[styles.controlButton, isMuted && styles.controlButtonActive]}
              >
                {isMuted ? 'Unmute' : 'Mute'}
              </Button>
              <Button
                mode="contained"
                onPress={() => setIsVideoEnabled(!isVideoEnabled)}
                style={[styles.controlButton, !isVideoEnabled && styles.controlButtonActive]}
              >
                {isVideoEnabled ? 'Disable Video' : 'Enable Video'}
              </Button>
              <Button
                mode="contained"
                onPress={handleLeaveRoom}
                style={[styles.controlButton, styles.endCallButton]}
              >
                End Call
              </Button>
            </View>
            <Button
              mode="contained"
              onPress={handleLeaveRoom}
              style={styles.endCallButton}
            >
              End Call
            </Button>
          </View>
        </Modal>
      </Portal>
    </View>
  );
};

const styles = StyleSheet.create({
  streamText: {
    color: '#FFFFFF',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 8,
  },
  streamStatus: {
    color: '#4CAF50',
    fontSize: 14,
    textAlign: 'center',
  },
  controlButtonActive: {
    backgroundColor: '#FF5722',
  },
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
  modalContent: {
    backgroundColor: 'white',
    margin: 0,
    padding: 0,
    flex: 1,
  },
  callContainer: {
    flex: 1,
    backgroundColor: 'black',
  },
  localStream: {
    position: 'absolute',
    width: 100,
    height: 150,
    top: 16,
    right: 16,
    zIndex: 2,
    borderRadius: 8,
    overflow: 'hidden',
  },
  remoteStream: {
    flex: 1,
  },
  endCallButton: {
    position: 'absolute',
    bottom: 32,
    alignSelf: 'center',
    backgroundColor: '#FF4444',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666',
  },
  errorText: {
    color: '#FF4444',
    fontSize: 16,
    marginBottom: 16,
    textAlign: 'center',
  },
  retryButton: {
    marginTop: 8,
  },
  participantList: {
    maxHeight: 200,
    marginVertical: 16,
  },
  participantItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  participantName: {
    flex: 1,
    marginLeft: 8,
  },
  controlsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 16,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
  },
  controlButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
