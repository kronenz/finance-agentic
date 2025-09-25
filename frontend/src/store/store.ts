import { configureStore } from '@reduxjs/toolkit';
import marketDataReducer from './slices/marketDataSlice';
import positionReducer from './slices/positionSlice';
import signalReducer from './slices/signalSlice';

export const store = configureStore({
  reducer: {
    marketData: marketDataReducer,
    position: positionReducer,
    signal: signalReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
