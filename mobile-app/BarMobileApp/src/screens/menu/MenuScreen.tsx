import React, { useEffect, useState } from 'react';
import { View, FlatList, StyleSheet } from 'react-native';
import { Card, Text, ActivityIndicator, Button, Portal, Modal } from 'react-native-paper';
import { MenuItem } from '../../api/types';
import * as api from '../../api/client';
import { useNavigation } from '@react-navigation/native';

export const MenuScreen = () => {
  const [items, setItems] = useState<MenuItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<MenuItem | null>(null);
  const [orderModalVisible, setOrderModalVisible] = useState(false);
  const [orderLoading, setOrderLoading] = useState(false);
  const navigation = useNavigation();

  useEffect(() => {
    loadMenuItems();
  }, []);

  const loadMenuItems = async () => {
    try {
      const data = await api.menu.getItems();
      setItems(data);
    } catch (error) {
      console.error('Failed to load menu items:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  const handleOrder = async () => {
    if (!selectedItem) return;
    
    setOrderLoading(true);
    try {
      await api.orders.placeOrder({
        itemId: selectedItem.id,
        quantity: 1,
      });
      setOrderModalVisible(false);
      // Show success message or navigate to orders screen
    } catch (error) {
      console.error('Failed to place order:', error);
      // Show error message
    } finally {
      setOrderLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <FlatList
        data={items}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <Card style={styles.card}>
            <Card.Content>
              <Text variant="titleLarge">{item.name}</Text>
              <Text variant="bodyMedium">{item.description}</Text>
              <Text variant="bodyMedium">
                Alcohol Content: {item.alcohol_content}%
              </Text>
              <Text variant="labelLarge" style={styles.price}>
                ${item.price.toFixed(2)}
              </Text>
              <Button
                mode="contained"
                onPress={() => {
                  setSelectedItem(item);
                  setOrderModalVisible(true);
                }}
                style={styles.orderButton}
              >
                Order Now
              </Button>
            </Card.Content>
          </Card>
        )}
      />

      <Portal>
        <Modal
          visible={orderModalVisible}
          onDismiss={() => setOrderModalVisible(false)}
          contentContainerStyle={styles.modalContent}
        >
          {selectedItem && (
            <View>
              <Text variant="headlineSmall">Confirm Order</Text>
              <Text variant="bodyLarge" style={styles.modalItem}>
                {selectedItem.name}
              </Text>
              <Text variant="bodyMedium" style={styles.modalPrice}>
                ${selectedItem.price.toFixed(2)}
              </Text>
              <View style={styles.modalButtons}>
                <Button
                  mode="outlined"
                  onPress={() => setOrderModalVisible(false)}
                  style={styles.modalButton}
                >
                  Cancel
                </Button>
                <Button
                  mode="contained"
                  onPress={handleOrder}
                  loading={orderLoading}
                  style={styles.modalButton}
                >
                  Confirm Order
                </Button>
              </View>
            </View>
          )}
        </Modal>
      </Portal>
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
  price: {
    marginTop: 8,
  },
  orderButton: {
    marginTop: 8,
  },
  modalContent: {
    backgroundColor: 'white',
    padding: 20,
    margin: 20,
    borderRadius: 8,
  },
  modalItem: {
    marginTop: 16,
    marginBottom: 8,
  },
  modalPrice: {
    marginBottom: 24,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
  },
  modalButton: {
    marginLeft: 8,
  },
});
