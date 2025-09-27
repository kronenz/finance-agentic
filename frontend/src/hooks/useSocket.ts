import { useEffect, useState, useRef } from 'react';
import io, { Socket } from 'socket.io-client';

// 백엔드 WebSocket URL (환경에 맞게 수정)
const SOCKET_URL = process.env.NODE_ENV === 'production' ? window.location.origin : 'ws://localhost:8001';

/**
 * 특정 이벤트에 대한 WebSocket 연결 및 데이터 수신을 처리하는 커스텀 훅
 * @param event - 구독할 이벤트 이름
 * @returns { data, isConnected }
 */
export const useSocket = <T,>(event: string) => {
  const [data, setData] = useState<T | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    // 이미 연결된 소켓이 있으면 재사용
    if (socketRef.current) {
      socketRef.current.disconnect();
    }

    const socket: Socket = io(SOCKET_URL, {
      transports: ['websocket'],
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });
    socketRef.current = socket;

    socket.on('connect', () => {
      setIsConnected(true);
      console.log(`Socket connected: ${socket.id}`);
    });

    socket.on('disconnect', (reason) => {
      setIsConnected(false);
      console.log(`Socket disconnected: ${reason}`);
    });

    socket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
      setIsConnected(false);
    });

    socket.on(event, (newData: T) => {
      setData(newData);
    });

    // 컴포넌트 언마운트 시 소켓 연결 해제
    return () => {
      socket.disconnect();
    };
  }, [event]);

  return { data, isConnected };
};
