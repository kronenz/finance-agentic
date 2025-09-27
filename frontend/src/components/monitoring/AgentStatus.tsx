import React, { useState, useEffect } from 'react';

// Define TypeScript interfaces for our data structures
interface Agent {
  is_running: boolean;
  agent_name: string;
}

interface AgentStatusData {
  timestamp: string;
  is_running: boolean;
  agents: Record<string, Agent>;
  redis_status: string;
  message_queues: Record<string, number>;
}

interface AgentMetricsData {
  status: string;
  messages_processed: number;
  error_count: number;
  last_activity: string;
}

interface MetricsData {
  system: any;
  agents: {
    data_collection_agent: AgentMetricsData;
    data_analysis_agent: AgentMetricsData;
    prediction_agent: AgentMetricsData;
  };
  database: any;
  redis: any;
}

interface Alert {
  id: string;
  title: string;
  status: string;
  source: string;
  timestamp: string;
}

const AgentStatus: React.FC = () => {
  const [agentStatus, setAgentStatus] = useState<AgentStatusData | null>(null);
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      const [statusRes, metricsRes, alertsRes] = await Promise.all([
        fetch('/api/v1/ai/status'),
        fetch('/api/v1/monitoring/metrics'),
        fetch('/api/v1/monitoring/alerts'),
      ]);

      if (!statusRes.ok || !metricsRes.ok || !alertsRes.ok) {
        throw new Error('Failed to fetch monitoring data');
      }

      const statusData = await statusRes.json();
      const metricsData = await metricsRes.json();
      const alertsData = await alertsRes.json();

      setAgentStatus(statusData);
      setMetrics(metricsData);
      setAlerts(alertsData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Poll every 5 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="p-4 bg-gray-800 rounded-lg">Loading agent status...</div>;
  }

  if (error) {
    return <div className="p-4 bg-red-800 rounded-lg">Error: {error}</div>;
  }

  return (
    <div className="p-4 bg-gray-900 text-white rounded-lg space-y-6">
      <h2 className="text-2xl font-bold mb-4">AI Agent Monitoring Dashboard</h2>

      {/* Agent Status Section */}
      <div className="bg-gray-800 p-4 rounded-lg">
        <h3 className="text-xl font-semibold mb-3">Agent Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {agentStatus?.agents && Object.entries(agentStatus.agents).map(([agentId, agent]) => (
            <div key={agentId} className={`p-3 rounded-md ${agent.is_running ? 'bg-green-600' : 'bg-red-600'}`}>
              <p className="font-bold">{agent.agent_name}</p>
              <p>Status: {agent.is_running ? 'Running' : 'Stopped'}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Performance Metrics Section */}
      <div className="bg-gray-800 p-4 rounded-lg">
        <h3 className="text-xl font-semibold mb-3">Performance Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {metrics?.agents && Object.entries(metrics.agents).map(([agentName, agentMetrics]) => (
            <div key={agentName} className="bg-gray-700 p-3 rounded-md">
              <p className="font-bold capitalize">{agentName.replace(/_/g, ' ')}</p>
              <p>Messages Processed: {agentMetrics.messages_processed}</p>
              <p>Error Count: {agentMetrics.error_count}</p>
              <p>Last Activity: {new Date(agentMetrics.last_activity).toLocaleString()}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Task Queue Section */}
      <div className="bg-gray-800 p-4 rounded-lg">
        <h3 className="text-xl font-semibold mb-3">Task Queues</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {agentStatus?.message_queues && Object.entries(agentStatus.message_queues).map(([queueName, count]) => (
            <div key={queueName} className="bg-gray-700 p-3 rounded-md">
              <p className="font-bold">{queueName}</p>
              <p>Pending Tasks: {count}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Error Logs / Alerts Section */}
      <div className="bg-gray-800 p-4 rounded-lg">
        <h3 className="text-xl font-semibold mb-3">Recent Alerts</h3>
        <div className="space-y-2">
          {alerts.length > 0 ? (
            alerts.slice(0, 5).map(alert => (
              <div key={alert.id} className="bg-red-700 p-3 rounded-md">
                <p><span className="font-bold">[{alert.source}]</span> {alert.title}</p>
                <p className="text-sm text-gray-300">{new Date(alert.timestamp).toLocaleString()} - Status: {alert.status}</p>
              </div>
            ))
          ) : (
            <p className="text-gray-400">No recent alerts.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AgentStatus;