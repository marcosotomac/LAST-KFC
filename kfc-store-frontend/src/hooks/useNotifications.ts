import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'order' | 'alert' | 'info';
  timestamp: Date;
}

export const useNotifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const playSound = useCallback(() => {
    const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjGH0fPTgjMGHm7A7+OZSA0PVqzn77BdGAg+ltryxnMpBSh+zO/aizsIGGS57OihUBELTKXh8bllHAU2jdXzzn0vBSp9yu/djzwKF2W99+mcSw0NTaXl8LVkGwc7ktXzxnUsBSl+yO/dkDsJHGy/7+OXRw0OUKfo8LFeFQpEnN7yuXAoBiR7x+/hjj0JGWu+7eSaRw0PTaLl8LNgGgY8j9TzxHQrBSiAyO/dkz0JHWy/7+KYSA0PTKPl8LNfGgY8j9TzxHQrBSiAyO/dkz0JHWy/7+KYSA0PTKPl8LNfGgY8j9TzxHQrBSiAyO/dkz0JHWy/7+KYSA0PTKPl8LNfGgY8j9TzxHQrBSiAyO/dkz0JHWy/7+KYSA0PTKPl8LNfGg==');
    audio.play().catch(e => console.log('Sound play failed:', e));
  }, []);

  const addNotification = useCallback((notification: Omit<Notification, 'id' | 'timestamp'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
    };

    setNotifications(prev => [newNotification, ...prev].slice(0, 50));
    
    // Show toast
    if (notification.type === 'order') {
      toast.success(notification.title, {
        description: notification.message,
      });
      playSound();
    } else if (notification.type === 'alert') {
      toast.warning(notification.title, {
        description: notification.message,
      });
    } else {
      toast.info(notification.title, {
        description: notification.message,
      });
    }
  }, [playSound]);

  return {
    notifications,
    addNotification,
  };
};
