import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Button, Text } from 'react-native-paper';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { MainTabParamList } from '../../navigation/types';

type Props = NativeStackScreenProps<MainTabParamList, 'Home'>;

export const HomeScreen: React.FC<Props> = () => {
  return (
    <View style={styles.container}>
      <Text variant="headlineMedium" style={styles.title}>Welcome to Bar App</Text>
      <Button
        mode="contained"
        onPress={() => {}}
        style={styles.button}
      >
        Scan QR Code
      </Button>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    marginBottom: 24,
  },
  button: {
    marginTop: 16,
  },
});
