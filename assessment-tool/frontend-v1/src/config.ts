// Auto-detect environment and set API URL
const getApiBaseUrl = (): string => {
  // Check if we're in Codespaces
  const hostname = window.location.hostname;
  
  if (hostname.includes('github.dev') || hostname.includes('githubpreview.dev')) {
    // Codespaces: Replace port 3000 with 8000 to get backend URL
    const backendUrl = window.location.origin.replace('-3000.', '-8000.');
    return `${backendUrl}/api`;  // Changed from /api/v1 to /api
  }
  
  // Local development or production
  return '/api';  // Changed from /api/v1 to /api
};

export const API_BASE_URL = getApiBaseUrl();

console.log('API Base URL:', API_BASE_URL);
