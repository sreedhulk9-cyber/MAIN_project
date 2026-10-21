import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import { sendChatMessage } from '../services/api';

const EXAMPLE_PROMPTS = [
  "Find flights from Kochi to Delhi tomorrow.",
  "Find the cheapest flight from Kochi to Bangalore on 15 November 2026.",
  "Compare flights from Kochi to Mumbai for two adults.",
  "Find direct flights from Delhi to Kochi.",
  "Find round-trip flights from Kochi to Dubai, departing on 15 November and returning on 22 November 2026.",
  "What is 25 multiplied by 8?",
  "Explain what an AI agent is in three sentences."
];

export default function ChatBox() {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'agent',
      agent: 'flight_agent',
      text: "Hello! I am your AgentOS Flight Assistant. You can ask me to search flights, compare airfares, check direct routes, or even perform math calculations and topic research. How can I assist your journey today?"
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (textToSend) => {
    const text = textToSend || input;
    if (!text.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: text.trim(),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const data = await sendChatMessage(userMessage.text);
      const agentReply = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        agent: data.agent,
        text: data.response,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, agentReply]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'agent',
          agent: 'system',
          text: `Error processing request: ${err.message}`,
          isError: true
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container" id="agentos-chat-container">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-info">
          <div className="chat-avatar">
            <Bot size={22} />
          </div>
          <div>
            <div className="chat-agent-title">AgentOS Conversational Assistant</div>
            <div className="chat-agent-subtitle">Autonomous routing across Flight, Calculator & Researcher agents</div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages" id="chat-messages-box">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`chat-bubble ${msg.sender === 'user' ? 'user' : 'agent'}`}
          >
            {msg.sender === 'agent' && (
              <div className="bubble-meta">
                <span className="bubble-agent-badge">{msg.agent || 'AgentOS'}</span>
                {msg.time && <span>{msg.time}</span>}
              </div>
            )}
            <div style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</div>
          </div>
        ))}

        {isLoading && (
          <div className="chat-bubble agent" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
            <span style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
              AgentOS reasoning & coordinating tools...
            </span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompt Chips */}
      <div className="chat-chips-row">
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
          <Sparkles size={12} /> Try:
        </span>
        {EXAMPLE_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            className="chip-btn"
            onClick={() => handleSend(prompt)}
            disabled={isLoading}
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input Bar */}
      <form
        className="chat-input-bar"
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
      >
        <input
          id="chat-message-input"
          className="chat-input-field"
          type="text"
          placeholder="Ask anything (e.g., 'Find flights from Kochi to Delhi tomorrow' or 'What is 25 * 8?')..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
        />
        <button
          type="submit"
          id="chat-send-btn"
          className="chat-send-btn"
          disabled={!input.trim() || isLoading}
          title="Send message"
        >
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}
