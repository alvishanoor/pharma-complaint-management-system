import { useState, useRef, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { sendCopilotMessage, uploadCopilotDocument } from '../features/copilotSlice'

export default function CopilotBox() {
  const dispatch = useDispatch()
  const { messages, status } = useSelector((state) => state.copilot)
  const [input, setInput] = useState('')
  const scrollRef = useRef(null)
  const fileInputRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages])

  const handleSend = () => {
    const trimmed = input.trim()
    if (!trimmed || status === 'loading') return
    dispatch(sendCopilotMessage(trimmed))
    setInput('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleFileChange = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    dispatch(uploadCopilotDocument(file))
    e.target.value = ''
  }

  return (
    <div className="card copilot-card">
      <h2>AI Copilot</h2>
      <p className="copilot-hint">
        Paste a complaint, or upload a PDF/image/email — I'll fill/update the form for you.
      </p>

      <div className="copilot-messages" ref={scrollRef}>
        {messages.map((m, i) => (
          <div key={i} className={`copilot-msg ${m.role}`}>
            {m.text}
          </div>
        ))}
        {status === 'loading' && (
          <div className="copilot-msg assistant loading">Reading and extracting fields...</div>
        )}
      </div>

      <div className="copilot-input-row">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder='e.g. "Customer Ramesh Pharma reported an allergic reaction to Amoxicillin, batch BATCH-2026-0417" or "country is India"'
          rows={3}
        />
        <div className="copilot-actions">
          <input
            type="file"
            ref={fileInputRef}
            accept=".pdf,.txt,.eml,.md,.png,.jpg,.jpeg,.webp"
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
          <button
            type="button"
            className="secondary"
            onClick={() => fileInputRef.current?.click()}
            disabled={status === 'loading'}
          >
            Upload Document
          </button>
          <button onClick={handleSend} disabled={status === 'loading'}>
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
