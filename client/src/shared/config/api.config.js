/**
 * API Configuration
 * 
 * For LOCAL development (same device):
 *   API_BASE_URL = "http://localhost:8000"
 * 
 * For LAN access (other devices on network):
 *   API_BASE_URL = "http://YOUR_MACHINE_IP:8000"
 *   Example: "http://192.168.1.100:8000"
 * 
 * Get your machine IP:
 *   Windows: ipconfig (look for IPv4 Address)
 *   Mac/Linux: ifconfig or hostname -I
 */

// Auto-detect: Use localhost if on same machine, otherwise use current hostname
const getApiBaseUrl = () => {
  // Get current hostname/IP from browser
  const host = window.location.hostname;
  
  // If accessing from localhost, use localhost for API
  if (host === 'localhost' || host === '127.0.0.1') {
    return "http://localhost:8000";
  }
  
  // Otherwise, use the same host (LAN access)
  return `http://${host}:8000`;
};

export const API_BASE_URL = getApiBaseUrl();

console.log(`🌐 API Base URL: ${API_BASE_URL}`);
