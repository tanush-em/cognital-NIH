/**
 * API service for Agent Dashboard backend integration
 */
class ApiService {
  constructor() {
    this.baseUrl = 'http://localhost:5000/api';
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}`);
      }
      
      return data;
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Escalation endpoints
  async getEscalations(status = 'pending', limit = 50) {
    return this.request(`/escalations?status=${status}&limit=${limit}`);
  }

  async assignEscalation(escalationId, agentId) {
    return this.request(`/escalations/${escalationId}/assign`, {
      method: 'POST',
      body: JSON.stringify({ agent_id: agentId }),
    });
  }

  async assignEscalationBySession(sessionId, agentId) {
    return this.request(`/escalations/assign-by-session`, {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, agent_id: agentId }),
    });
  }

  // Session endpoints
  async getSessions(status = 'all', limit = 50) {
    return this.request(`/sessions?status=${status}&limit=${limit}`);
  }

  async getSessionSummary(sessionId) {
    return this.request(`/sessions/${sessionId}/summary`);
  }


  // Agent endpoints
  async getAgents() {
    return this.request('/agents');
  }

  async updateAgentAvailability(agentId, isAvailable) {
    return this.request(`/agents/${agentId}/availability`, {
      method: 'PUT',
      body: JSON.stringify({ is_available: isAvailable }),
    });
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }
}

// Create and export singleton instance
const apiService = new ApiService();
export default apiService;
