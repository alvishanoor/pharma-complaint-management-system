import { useDispatch, useSelector } from 'react-redux'
import { updateField, resetForm } from '../features/formSlice'
import { submitComplaint } from '../features/complaintSlice'
import { resetChat } from '../features/copilotSlice'

export default function ComplaintForm() {
  const dispatch = useDispatch()
  const form = useSelector((state) => state.form.fields)
  const { status } = useSelector((state) => state.complaints)

  const handleChange = (e) => {
    dispatch(updateField({ name: e.target.name, value: e.target.value }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!form.customer_name || !form.complaint_text) return
    dispatch(submitComplaint(form))
  }

  const handleClear = () => {
    dispatch(resetForm())
    dispatch(resetChat())
  }

  return (
    <div className="card">
      <h2>Log Customer Complaint</h2>
      {form.attachment_filename && (
        <div className="attachment-badge">Attached: {form.attachment_filename.split('_').slice(1).join('_')}</div>
      )}
      <form onSubmit={handleSubmit}>
        <label>Customer Name *</label>
        <input
          name="customer_name"
          value={form.customer_name}
          onChange={handleChange}
          placeholder="e.g. Ramesh Pharma Distributors"
        />

        <label>Product Name</label>
        <input
          name="product_name"
          value={form.product_name}
          onChange={handleChange}
          placeholder="e.g. Paracetamol 500mg Tablets"
        />

        <label>Batch Number</label>
        <input
          name="batch_number"
          value={form.batch_number}
          onChange={handleChange}
          placeholder="e.g. BATCH-2026-0417"
        />

        

        <label>Country</label>
        <input
          name="country"
          value={form.country}
          onChange={handleChange}
          placeholder="e.g. India"
        />

        <label>Quantity Affected</label>
        <input
          name="quantity_affected"
          value={form.quantity_affected}
          onChange={handleChange}
          placeholder="e.g. 12 units / 1 batch"
        />

        <label>Complaint Description *</label>
        <textarea
          name="complaint_text"
          value={form.complaint_text}
          onChange={handleChange}
          rows={5}
          placeholder="Describe the issue reported by the customer..."
        />

        <div className="form-buttons">
          <button type="button" className="secondary" onClick={handleClear}>
            Clear
          </button>
          <button type="submit" disabled={status === 'loading'}>
            {status === 'loading' ? 'Analyzing with AI...' : 'Submit Complaint'}
          </button>
        </div>
      </form>
    </div>
  )
}
