/**
 * Notification management utilities
 */

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  timestamp: number;
  actions?: NotificationAction[];
}

export interface NotificationAction {
  label: string;
  action: () => void;
  style?: 'primary' | 'secondary' | 'danger';
}

export class NotificationManager {
  private notifications: Notification[] = [];
  private listeners: Array<(notifications: Notification[]) => void> = [];

  add(notification: Omit<Notification, 'id' | 'timestamp'>): string {
    const id = Math.random().toString(36).substr(2, 9);
    const newNotification: Notification = {
      ...notification,
      id,
      timestamp: Date.now(),
      duration: notification.duration || 5000,
    };

    this.notifications.push(newNotification);
    this.notifyListeners();

    if (newNotification.duration > 0) {
      setTimeout(() => {
        this.remove(id);
      }, newNotification.duration);
    }

    return id;
  }

  remove(id: string): void {
    this.notifications = this.notifications.filter(n => n.id !== id);
    this.notifyListeners();
  }

  clear(): void {
    this.notifications = [];
    this.notifyListeners();
  }

  getAll(): Notification[] {
    return [...this.notifications];
  }

  subscribe(listener: (notifications: Notification[]) => void): () => void {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notifyListeners(): void {
    this.listeners.forEach(listener => listener(this.getAll()));
  }
}

export const notificationManager = new NotificationManager();

export const notifications = {
  success: (title: string, message: string, duration?: number) =>
    notificationManager.add({ type: 'success', title, message, duration }),
  
  error: (title: string, message: string, duration?: number) =>
    notificationManager.add({ type: 'error', title, message, duration }),
  
  warning: (title: string, message: string, duration?: number) =>
    notificationManager.add({ type: 'warning', title, message, duration }),
  
  info: (title: string, message: string, duration?: number) =>
    notificationManager.add({ type: 'info', title, message, duration }),
  
  remove: (id: string) => notificationManager.remove(id),
  clear: () => notificationManager.clear(),
  getAll: () => notificationManager.getAll(),
  subscribe: (listener: (notifications: Notification[]) => void) => 
    notificationManager.subscribe(listener),
};

export function useNotifications() {
  const [notifications, setNotifications] = React.useState(notificationManager.getAll());

  React.useEffect(() => {
    const unsubscribe = notificationManager.subscribe(setNotifications);
    return unsubscribe;
  }, []);

  return {
    notifications,
    add: (notification: Omit<Notification, 'id' | 'timestamp'>) => 
      notificationManager.add(notification),
    remove: (id: string) => notificationManager.remove(id),
    clear: () => notificationManager.clear(),
  };
}