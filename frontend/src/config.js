// CONFIGURATION FILE - API URL FORCED TO CORRECT VALUE

// FORCED API URL - NEVER CHANGE THIS
export const API_BASE_URL = 'http://127.0.0.1:8001/api';

// Multiple validation checks
export const getApiUrl = () => {
  const forcedUrl = 'http://127.0.0.1:8001/api';
  
  // Log everything for debugging
  console.error('🔧 CONFIG FILE LOADED');
  console.error('🔧 FORCED URL:', forcedUrl);
  
  // Ensure we never accidentally use 8050
  if (forcedUrl.includes('8050')) {
    console.error('❌ CRITICAL ERROR: Config contains 8050!');
    throw new Error('Invalid API URL configuration');
  }
  
  console.error('✅ CONFIG: Returning correct URL:', forcedUrl);
  return forcedUrl;
};

// Export default URL
export default API_BASE_URL;