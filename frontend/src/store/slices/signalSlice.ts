import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface SignalState {
  signals: any[];
  loading: boolean;
  error: string | null;
}

const initialState: SignalState = {
  signals: [],
  loading: false,
  error: null,
};

const signalSlice = createSlice({
  name: 'signal',
  initialState,
  reducers: {
    fetchSignalsStart(state) {
      state.loading = true;
      state.error = null;
    },
    fetchSignalsSuccess(state, action: PayloadAction<any[]>) {
      state.signals = action.payload;
      state.loading = false;
    },
    fetchSignalsFailure(state, action: PayloadAction<string>) {
      state.error = action.payload;
      state.loading = false;
    },
  },
});

export const {
  fetchSignalsStart,
  fetchSignalsSuccess,
  fetchSignalsFailure,
} = signalSlice.actions;

export default signalSlice.reducer;
