import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { sendMessage, getPatient } from '../api/client';

function ChatSession() {
  const { id } = useParams();
  const [patient, setPatient] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [currentPhase, setCurrentPhase] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchPatient = useCallback(async () => {
    try {
      const p = await getPatient(id);
      setPatient(p);
      setCurrentPhase(p.phase);
    } catch (err) {
      setError(err.message);
    }
  }, [id]);

  useEffect(() => {
    fetchPatient();
  }, [fetchPatient]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || sending) return;

    // Add user message to chat
    setMessages((prev) => [...prev, { role: 'user', content: text }]);
    setInput('');
    setSending(true);
    setError(null);

    try {
      const result = await sendMessage(id, text);

      // Add assistant response
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: result.response,
          safety_flagged: result.safety_flagged,
        },
      ]);

      setCurrentPhase(result.phase);
    } catch (err) {
      setError(err.message);
      // Remove the user message that failed
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setSending(false);
    }
  };

  return (
    <div>
      <div className="page-header" style={{ marginBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <Link to={`/patients/${id}`} className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.85rem' }}>
            &larr; Back
          </Link>
          <div>
            <h1 style={{ fontSize: '1.2rem' }}>
              Chat with {patient?.name || 'Patient'}
            </h1>
            <span style={{ fontSize: '0.8rem', color: '#888' }}>
              Phase: <span className={`phase-badge phase-${currentPhase}`}>{currentPhase}</span>
            </span>
          </div>
        </div>
      </div>

      {!patient?.consent_verified && (
        <div className="alert alert-warning">
          Patient consent has not been verified. The coach will not interact until consent is given.
        </div>
      )}

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div className="chat-container" style={{ padding: '0 24px' }}>
          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="empty-state" style={{ padding: '40px 0' }}>
                <h3>Start a conversation</h3>
                <p>Send a message to begin the coaching session.</p>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`chat-bubble ${msg.role} ${msg.safety_flagged ? 'safety-flagged' : ''}`}
              >
                {msg.content}
                {msg.safety_flagged && (
                  <div style={{ marginTop: 6, fontSize: '0.75rem', fontWeight: 600 }}>
                    SAFETY FLAGGED
                  </div>
                )}
              </div>
            ))}

            {sending && (
              <div className="chat-bubble assistant" style={{ opacity: 0.6 }}>
                Thinking...
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {error && (
            <div className="alert alert-danger" style={{ margin: '0 0 8px 0' }}>
              {error}
            </div>
          )}

          <div className="chat-input-area">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Type a message..."
              disabled={sending}
            />
            <button onClick={handleSend} disabled={sending || !input.trim()}>
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatSession;
