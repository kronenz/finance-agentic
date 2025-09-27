import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('authToken');
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: ['User', 'Trading', 'Portfolio', 'Alerts'],
  endpoints: (builder) => ({
    // Auth endpoints
    login: builder.mutation({
      query: (credentials) => ({
        url: '/api/v1/auth/login',
        method: 'POST',
        body: credentials,
      }),
    }),
    logout: builder.mutation({
      query: () => ({
        url: '/api/v1/auth/logout',
        method: 'POST',
      }),
    }),
    getCurrentUser: builder.query({
      query: () => '/api/v1/auth/me',
      providesTags: ['User'],
    }),

    // Trading endpoints
    getTradingSignals: builder.query({
      query: () => '/api/v1/trading/signals',
      providesTags: ['Trading'],
    }),
    getPositions: builder.query({
      query: () => '/api/v1/trading/positions',
      providesTags: ['Trading'],
    }),
    getTradingHistory: builder.query({
      query: () => '/api/v1/trading/history',
      providesTags: ['Trading'],
    }),

    // Portfolio endpoints
    getPortfolio: builder.query({
      query: () => '/api/v1/portfolio',
      providesTags: ['Portfolio'],
    }),
    getPerformance: builder.query({
      query: () => '/api/v1/portfolio/performance',
      providesTags: ['Portfolio'],
    }),

    // Market data endpoints
    getMarketData: builder.query({
      query: (symbol) => `/api/v1/market/${symbol}`,
    }),
    getVWAPData: builder.query({
      query: (symbol) => `/api/v1/market/${symbol}/vwap`,
    }),
    getVolumeProfile: builder.query({
      query: (symbol) => `/api/v1/market/${symbol}/volume-profile`,
    }),

    // Risk management endpoints
    getRiskMetrics: builder.query({
      query: () => '/api/v1/risk/metrics',
      providesTags: ['Portfolio'],
    }),

    // Monitoring endpoints
    getAlerts: builder.query({
      query: () => '/api/v1/monitoring/alerts',
      providesTags: ['Alerts'],
    }),
    getAgentStatus: builder.query({
      query: () => '/api/v1/monitoring/agents',
      providesTags: ['Alerts'],
    }),
  }),
});

export const {
  useLoginMutation,
  useLogoutMutation,
  useGetCurrentUserQuery,
  useGetTradingSignalsQuery,
  useGetPositionsQuery,
  useGetTradingHistoryQuery,
  useGetPortfolioQuery,
  useGetPerformanceQuery,
  useGetMarketDataQuery,
  useGetVWAPDataQuery,
  useGetVolumeProfileQuery,
  useGetRiskMetricsQuery,
  useGetAlertsQuery,
  useGetAgentStatusQuery,
} = api;
