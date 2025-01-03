import React, { useState, useEffect, useRef } from 'react';
import { View, FlatList, StyleSheet } from 'react-native';
import { TextInput, Button, Card, Text } from 'react-native-paper';
import { ChatMessage } from '../../api/types';
import * as api from '../../api/client';

export const ChatScreen = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState<number | null>(null);
  const flatListRef = useRef<FlatList>(null);

  useEffect(() => {
    startConversation();
  }, []);

  const startConversation = async () => {
    try {
      const conversation = await api.chat.startConversation();
      setConversationId(conversation.id);
    } catch (error) {
      console.error('Failed to start conversation:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || !conversationId) return;

    try {
      const response = await api.chat.sendMessage(conversationId, input);
      setMessages((prev) => [...prev, response.message]);
      setInput('');
      flatListRef.current?.scrollToEnd();
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  return (
    <View style={styles.container}>
      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <Card
            style={[
              styles.messageCard,
              item.role === 'user' ? styles.userMessage : styles.aiMessage,
            ]}
          >
            <Card.Content>
              <Text variant="bodyMedium">{item.content}</Text>
            </Card.Content>
          </Card>
        )}
        style={styles.messageList}
      />
      <View style={styles.inputContainer}>
        <TextInput
          value={input}
          onChangeText={setInput}
          mode="outlined"
          placeholder="Type a message..."
          style={styles.input}
        />
        <Button mode="contained" onPress={sendMessage}>
          Send
        </Button>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  messageList: {
    flex: 1,
    padding: 16,
  },
  messageCard: {
    marginBottom: 8,
  },
  userMessage: {
    marginLeft: 32,
  },
  aiMessage: {
    marginRight: 32,
    backgroundColor: '#f0f0f0',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 16,
    alignItems: 'center',
  },
  input: {
    flex: 1,
    marginRight: 8,
  },
});
