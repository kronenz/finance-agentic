import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface PositionState {
  positions: any[];
  loading: boolean;
  error: string | null;
}

const initialState: PositionState = {
  positions: [],
  loading: false,
  error: null,
};

const positionSlice = createSlice({
  name: 'position',
  initialState,
  reducers: {
    fetchPositionsStart(state) {
      state.loading = true;
      state.error = null;
    },
    fetchPositionsSuccess(state, action: PayloadAction<any[]>) {
      state.positions = action.payload;
      state.loading = false;
    },
    fetchPositionsFailure(state, action: PayloadAction<string>) {
      state.error = action.payload;
      state.loading = false;
    },
  },
});

export const {
  fetchPositionsStart,
  fetchPositionsSuccess,
  fetchPositionsFailure,
} = positionSlice.actions;

export default positionSlice.reducer;
