import CopilotBox from './components/CopilotBox'
import ComplaintForm from './components/ComplaintForm'
import ResultCard from './components/ResultCard'

export default function App() {
  return (
    <div className="app">
      <header>
        <h1>Pharma Customer Complaint Management System</h1>
        <p className="subtitle">AI-Powered QMS Complaint Intake & Risk Triage</p>
      </header>

      <main className="main-grid three-col">
        <CopilotBox />
        <ComplaintForm />
        <ResultCard />
      </main>
    </div>
  )
}