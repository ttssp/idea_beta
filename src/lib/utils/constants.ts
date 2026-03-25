export const APP_NAME = 'Agent Comm Control';
export const APP_DESCRIPTION = '代理原生通信控制层';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '/api';
export const SSE_URL = process.env.NEXT_PUBLIC_SSE_URL || '/api/sse';

export const IS_DEVELOPMENT = process.env.NODE_ENV === 'development';
export const IS_PRODUCTION = process.env.NODE_ENV === 'production';

export const USE_MOCK_API = process.env.NEXT_PUBLIC_USE_MOCK === 'true' || IS_DEVELOPMENT;

// Pagination
export const DEFAULT_PAGE_SIZE = 20;
export const MAX_PAGE_SIZE = 100;

// Real-time
export const SSE_RECONNECT_DELAY = 3000;
export const SSE_MAX_RECONNECT_ATTEMPTS = 5;

// Debounce
export const SEARCH_DEBOUNCE_MS = 300;
export const INPUT_DEBOUNCE_MS = 500;

// Animation
export const TOAST_DURATION = 5000;
export const MODAL_TRANSITION_MS = 200;
