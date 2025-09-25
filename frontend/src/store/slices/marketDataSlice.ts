import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface MarketDataState {
  data: any[];
  loading: boolean;
  error: string | null;
}

const initialState: MarketDataState = {
  data: [],
  loading: false,
  error: null,
};

const marketDataSlice = createSlice({
  name: 'marketData',
  initialState,
  reducers: {
    fetchMarketDataStart(state) {
      state.loading = true;
      state.error = null;
    },
    fetchMarketDataSuccess(state, action: PayloadAction<any[]>) {
      state.data = action.payload;
      state.loading = false;
    },
    fetchMarketDataFailure(state, action: PayloadAction<string>) {
      state.error = action.payload;
      state.loading = false;
    },
  },
});

export const {
  fetchMarketDataStart,
  fetchMarketDataSuccess,
  fetchMarketDataFailure,
} = marketDataSlice.actions;

export default marketDataSlice.reducer;
