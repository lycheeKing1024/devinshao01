import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { Button, TextInput, Text, Avatar } from 'react-native-paper';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { User } from '../../api/types';

export const ProfileScreen = () => {
  const [user, setUser] = useState<User>({
    id: 1,
    email: 'user@example.com',
    name: 'John Doe',
    preferences: {},
  });

  const handleLogout = async () => {
    try {
      await AsyncStorage.removeItem('auth_token');
      // TODO: Navigate to login screen
    } catch (error) {
      console.error('Failed to logout:', error);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Avatar.Text size={80} label={user.name.substring(0, 2)} />
        <Text variant="headlineSmall" style={styles.name}>
          {user.name}
        </Text>
        <Text variant="bodyMedium" style={styles.email}>
          {user.email}
        </Text>
      </View>

      <View style={styles.form}>
        <TextInput
          label="Name"
          value={user.name}
          onChangeText={(text) => setUser({ ...user, name: text })}
          mode="outlined"
          style={styles.input}
        />
        <TextInput
          label="Email"
          value={user.email}
          onChangeText={(text) => setUser({ ...user, email: text })}
          mode="outlined"
          style={styles.input}
          disabled
        />
      </View>

      <View style={styles.preferences}>
        <Text variant="titleLarge" style={styles.sectionTitle}>
          Preferences
        </Text>
        {/* TODO: Add preference toggles */}
      </View>

      <Button mode="contained" onPress={handleLogout} style={styles.logoutButton}>
        Logout
      </Button>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  header: {
    alignItems: 'center',
    marginBottom: 24,
  },
  name: {
    marginTop: 8,
  },
  email: {
    marginTop: 4,
    opacity: 0.7,
  },
  form: {
    marginBottom: 24,
  },
  input: {
    marginBottom: 16,
  },
  preferences: {
    marginBottom: 24,
  },
  sectionTitle: {
    marginBottom: 16,
  },
  logoutButton: {
    marginTop: 'auto',
  },
});
