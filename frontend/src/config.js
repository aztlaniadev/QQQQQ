// CONFIGURATION FILE - API URL FORCED FOR WINDOWS PORT 8030

// FORCED API URL FOR WINDOWS - NEVER CHANGE THIS
export const API_BASE_URL = 'http://localhost:8030/api';

// Multiple validation checks
export const getApiUrl = () => {
  const forcedUrl = 'http://localhost:8030/api';
  
  // Log everything for debugging
  console.error('🔧 CONFIG FILE LOADED - WINDOWS VERSION');
  console.error('🔧 WINDOWS FORCED URL:', forcedUrl);
  
  // Ensure we never accidentally use wrong ports
  if (forcedUrl.includes('8050') || forcedUrl.includes('8001')) {
    console.error('❌ CRITICAL ERROR: Config contains wrong port!');
    throw new Error('Invalid API URL configuration - should be 8030');
  }
  
  console.error('✅ CONFIG: Returning Windows URL (8030):', forcedUrl);
  return forcedUrl;
};

// Export default URL
export default API_BASE_URL;