import React, { useState, useEffect } from "react";
import "./WebhookLogs.css";

const WebhookLogs = () => {
  // state management
  const [logs, setLogs] = useState([]);
  // hook to handle api request
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await fetch("http://localhost:5000/logs");
        const data = await response.json();
        setLogs(data);
      } catch (error) {
        console.error("Error fetching logs:", error);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 15000);
    return () => clearInterval(interval);
  }, []);

  const formatLog = (log) => {
    const { author, action, from_branch, to_branch, timestamp } = log;

    switch (action) {
      case "PUSH":
        return `${author} pushed to ${to_branch} on ${timestamp}`;
      case "PULL_REQUEST":
        return `${author} submitted a pull request from ${from_branch} to ${to_branch} on ${timestamp}`;
      case "MERGE":
        return `${author} merged branch ${from_branch} to ${to_branch} on ${timestamp}`;
      default:
        return "Unknown action";
    }
  };

  return (
    <div className="webhook-container">
      <h2 className="webhook-heading">Webhook Event Logs</h2>
      {logs.length === 0 ? (
        <p className="webhook-empty">No logs yet</p>
      ) : (
        <ul className="webhook-log-list">
          {logs.map((log) => (
            <li key={log.request_id} className="webhook-log-item">
              {formatLog(log)}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default WebhookLogs;
