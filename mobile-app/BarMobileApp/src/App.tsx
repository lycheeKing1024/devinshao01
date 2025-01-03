import React from 'react';
import { Provider as PaperProvider } from 'react-native-paper';
import { RootNavigator } from './src/navigation/RootNavigator';

export default function App() {
  return (
    <PaperProvider>
      <RootNavigator />
    </PaperProvider>
  );
}
