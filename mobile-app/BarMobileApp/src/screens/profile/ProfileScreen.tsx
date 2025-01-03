import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Button, TextInput, Text, Avatar, Chip, SegmentedButtons } from 'react-native-paper';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { User, UserPreferences } from '../../api/types';
import * as api from '../../api/client';

export const ProfileScreen = () => {
  const [user, setUser] = useState<User>({
    id: 1,
    email: 'user@example.com',
    name: 'John Doe',
    age: 21,
    preferences: {
      alcoholContent: 'medium',
      flavorPreferences: [],
      allergies: [],
      dietaryRestrictions: [],
      sugarPreference: 'medium'
    },
    orderHistory: []
  });
  
  const [loading, setLoading] = useState(true);
  const [selectedFlavor, setSelectedFlavor] = useState('');

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
        
        <Text variant="titleMedium" style={styles.subsectionTitle}>
          Alcohol Content Preference
        </Text>
        <SegmentedButtons
          value={user.preferences.alcoholContent}
          onValueChange={value => 
            setUser({
              ...user,
              preferences: { ...user.preferences, alcoholContent: value as 'none' | 'low' | 'medium' | 'high' }
            })
          }
          buttons={[
            { value: 'none', label: 'None' },
            { value: 'low', label: 'Low' },
            { value: 'medium', label: 'Medium' },
            { value: 'high', label: 'High' }
          ]}
          style={styles.segmentedButton}
        />

        <Text variant="titleMedium" style={styles.subsectionTitle}>
          Sugar Preference
        </Text>
        <SegmentedButtons
          value={user.preferences.sugarPreference}
          onValueChange={value => 
            setUser({
              ...user,
              preferences: { ...user.preferences, sugarPreference: value as 'low' | 'medium' | 'high' }
            })
          }
          buttons={[
            { value: 'low', label: 'Low' },
            { value: 'medium', label: 'Medium' },
            { value: 'high', label: 'High' }
          ]}
          style={styles.segmentedButton}
        />

        <Text variant="titleMedium" style={styles.subsectionTitle}>
          Flavor Preferences
        </Text>
        <View style={styles.chipContainer}>
          {user.preferences.flavorPreferences.map((flavor, index) => (
            <Chip
              key={index}
              onClose={() => {
                const newPreferences = {
                  ...user.preferences,
                  flavorPreferences: user.preferences.flavorPreferences.filter((_, i) => i !== index)
                };
                setUser({ ...user, preferences: newPreferences });
              }}
              style={styles.chip}
            >
              {flavor}
            </Chip>
          ))}
        </View>
        <View style={styles.addFlavorContainer}>
          <TextInput
            label="Add Flavor"
            value={selectedFlavor}
            onChangeText={setSelectedFlavor}
            style={styles.addFlavorInput}
          />
          <Button
            mode="contained"
            onPress={() => {
              if (selectedFlavor.trim()) {
                const newPreferences = {
                  ...user.preferences,
                  flavorPreferences: [...user.preferences.flavorPreferences, selectedFlavor.trim()]
                };
                setUser({ ...user, preferences: newPreferences });
                setSelectedFlavor('');
              }
            }}
          >
            Add
          </Button>
        </View>

        <Text variant="titleMedium" style={styles.subsectionTitle}>
          Allergies & Restrictions
        </Text>
        <TextInput
          label="Allergies (comma-separated)"
          value={user.preferences.allergies.join(', ')}
          onChangeText={text => {
            const allergies = text.split(',').map(item => item.trim()).filter(Boolean);
            setUser({
              ...user,
              preferences: { ...user.preferences, allergies }
            });
          }}
          mode="outlined"
          style={styles.input}
        />
        <TextInput
          label="Dietary Restrictions (comma-separated)"
          value={user.preferences.dietaryRestrictions.join(', ')}
          onChangeText={text => {
            const restrictions = text.split(',').map(item => item.trim()).filter(Boolean);
            setUser({
              ...user,
              preferences: { ...user.preferences, dietaryRestrictions: restrictions }
            });
          }}
          mode="outlined"
          style={styles.input}
        />
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
  subsectionTitle: {
    marginTop: 16,
    marginBottom: 8,
  },
  segmentedButton: {
    marginBottom: 16,
  },
  chipContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 8,
  },
  chip: {
    margin: 4,
  },
  addFlavorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  addFlavorInput: {
    flex: 1,
    marginRight: 8,
  },
  logoutButton: {
    marginTop: 'auto',
  },
});
