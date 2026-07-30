import { useSelector } from 'react-redux'

const riskColor = {
  High: '#dc2626',
  Medium: '#d97706',
  Low: '#16a34a',
}

export default function ResultCard() {
  const { latestResult, status, error } = useSelector((state) => state.complaints)

  if (status === 'loading') {
    return <div className="card">Running LangGraph workflow (completeness check to risk classification)...</div>
  }

  if (status === 'failed') {
    return <div className="card error">Error: {error}</div>
  }

  if (!latestResult) {
    return <div className="card muted">Submit a complaint to see the AI Copilot Risk Assessment here.</div>
  }

  return (
    <div className="card">
      <h2>AI Copilot Risk Assessment</h2>

      {!latestResult.is_complete && (
        <div className="warning-box">
          <strong>Incomplete Complaint</strong>
          <p>Missing fields: {latestResult.missing_fields?.join(', ') || 'N/A'}</p>
          <p>Risk classification skipped until required info is provided.</p>
        </div>
      )}

      {latestResult.is_complete && (
        <div>
          <div
            className="risk-badge"
            style={{ backgroundColor: riskColor[latestResult.risk_level] || '#6b7280' }}
          >
            {latestResult.risk_level || 'Unclassified'} Risk
          </div>
          <p className="reasoning">{latestResult.risk_reasoning}</p>
        </div>
      )}

      <div className="detail-grid two-col">
        
        <div>
          <span className="detail-label">Country</span>
          <span className="detail-value">{latestResult.country || '-'}</span>
        </div>
        <div>
          <span className="detail-label">Quantity Affected</span>
          <span className="detail-value">{latestResult.quantity_affected || '-'}</span>
        </div>
      </div>

      {latestResult.attachment_filename && (
        <div className="attachment-link">
          <a
            href={`http://localhost:8000/uploads/${latestResult.attachment_filename}`}
            target="_blank"
            rel="noreferrer"
          >
            View attached document
          </a>
        </div>
      )}

      <div className="meta">
        <p><strong>Status:</strong> {latestResult.status}</p>
        <p><strong>Complaint ID:</strong> #{latestResult.id}</p>
      </div>
    </div>
  )
}

