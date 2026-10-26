import { FormEvent, useEffect, useMemo, useState } from 'react'

type Source = { id: string; title: string; excerpt: string; score: number }
type Analysis = {
  id: number
  title: string
  category: string
  severity: string
  confidence: string
  escalation: boolean
  summary: string
  steps: string[]
  sources: Source[]
  created_at: string
}

type TicketListItem = {
  id: number
  title: string
  category: string
  severity: string
  confidence: string
  escalation: boolean
  created_at: string
}

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

const EXAMPLES = [
  {
    label: 'Docker / Postgres',
    title: 'API cannot reach database',
    description:
      'The service works locally, but after Docker deployment it returns connection refused when connecting to Postgres.',
  },
  {
    label: 'DNS failure',
    title: 'Internal hostname is not resolving',
    description:
      'Users can reach the service by IP address, but requests fail when using the internal hostname after a network change.',
  },
  {
    label: 'CPU spike',
    title: 'API CPU usage jumps after deployment',
    description:
      'CPU utilization rises above 90% after the latest release and response times become slow during normal traffic.',
  },
]

export default function App() {
  const [title, setTitle] = useState(EXAMPLES[0].title)
  const [description, setDescription] = useState(EXAMPLES[0].description)
  const [result, setResult] = useState<Analysis | null>(null)
  const [history, setHistory] = useState<TicketListItem[]>([])
  const [loading, setLoading] = useState(false)
  const [historyLoading, setHistoryLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    void loadHistory()
  }, [])

  const escalationCount = useMemo(
    () => history.filter((ticket) => ticket.escalation).length,
    [history],
  )

  async function loadHistory() {
    setHistoryLoading(true)
    try {
      const response = await fetch(`${API}/api/tickets`)
      if (!response.ok) throw new Error('Could not load ticket history')
      setHistory(await response.json())
    } catch {
      // Keep the MVP usable even if history is temporarily unavailable.
    } finally {
      setHistoryLoading(false)
    }
  }

  async function loadTicket(id: number) {
    setError('')
    try {
      const response = await fetch(`${API}/api/tickets/${id}`)
      if (!response.ok) throw new Error('Could not load ticket')
      setResult(await response.json())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const response = await fetch(`${API}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description }),
      })
      if (!response.ok) throw new Error('Analysis request failed')
      setResult(await response.json())
      await loadHistory()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  function useExample(index: number) {
    setTitle(EXAMPLES[index].title)
    setDescription(EXAMPLES[index].description)
  }

  return (
    <main className="shell">
      <nav className="topbar">
        <div className="brandMark">SD</div>
        <div className="topbarCopy">
          <strong>SignalDesk AI</strong>
          <span>Support intelligence workspace</span>
        </div>
        <div className="apiStatus"><i /> API connected</div>
      </nav>

      <header className="hero">
        <div>
          <div className="eyebrow">AI-assisted support engineering</div>
          <h1>Turn incidents into <span>action.</span></h1>
          <p>
            Classify technical issues, surface evidence-backed troubleshooting steps,
            and route uncertain cases to a human before bad advice reaches production.
          </p>
        </div>
        <div className="heroStats">
          <Stat label="Tickets analyzed" value={history.length.toString()} />
          <Stat label="Escalations" value={escalationCount.toString()} />
          <Stat label="Decision mode" value="Evidence-first" />
        </div>
      </header>

      <section className="workspace">
        <aside className="leftRail">
          <form className="panel analyzePanel" onSubmit={submit}>
            <div className="panelHeading">
              <div>
                <div className="panelKicker">New incident</div>
                <h2>Analyze incident</h2>
              </div>
              <span className="liveBadge">Live</span>
            </div>

            <div className="exampleRow">
              {EXAMPLES.map((example, index) => (
                <button
                  className="exampleChip"
                  type="button"
                  key={example.label}
                  onClick={() => useExample(index)}
                >
                  {example.label}
                </button>
              ))}
            </div>

            <label>
              Title
              <input value={title} onChange={(e) => setTitle(e.target.value)} />
            </label>
            <label>
              Description
              <textarea rows={9} value={description} onChange={(e) => setDescription(e.target.value)} />
            </label>
            <button className="primaryButton" disabled={loading}>
              {loading ? 'Analyzing incident…' : 'Run support analysis'}
            </button>
            {error && <p className="error">{error}</p>}
          </form>

          <section className="panel historyPanel">
            <div className="panelHeading compact">
              <div>
                <div className="panelKicker">Support queue</div>
                <h2>Recent incidents</h2>
              </div>
              <span className="historyCount">{history.length}</span>
            </div>

            <div className="historyList">
              {historyLoading ? (
                <p className="muted">Loading ticket history…</p>
              ) : history.length === 0 ? (
                <p className="muted">Analyzed incidents will appear here.</p>
              ) : (
                history.slice(0, 6).map((ticket) => (
                  <button
                    key={ticket.id}
                    type="button"
                    className={`historyItem ${result?.id === ticket.id ? 'active' : ''}`}
                    onClick={() => void loadTicket(ticket.id)}
                  >
                    <div>
                      <strong>{ticket.title}</strong>
                      <span>{ticket.category} · {formatDate(ticket.created_at)}</span>
                    </div>
                    <span className={`dot ${tone(ticket.severity)}`} title={`${ticket.severity} severity`} />
                  </button>
                ))
              )}
            </div>
          </section>
        </aside>

        <section className="panel resultPanel">
          {!result ? (
            <div className="emptyState">
              <div className="emptyIcon">⌁</div>
              <h2>Analysis workspace</h2>
              <p>Submit an incident to see classification, severity, confidence, evidence, and next-step recommendations.</p>
            </div>
          ) : (
            <>
              <div className="resultMeta">
                <span>Ticket #{result.id}</span>
                <span>{formatDate(result.created_at)}</span>
              </div>

              <div className="metrics">
                <Metric label="Category" value={result.category} toneName="info" />
                <Metric label="Severity" value={result.severity} toneName={tone(result.severity)} />
                <Metric label="Confidence" value={result.confidence} toneName={confidenceTone(result.confidence)} />
                <Metric
                  label="Escalate"
                  value={result.escalation ? 'Yes' : 'No'}
                  toneName={result.escalation ? 'danger' : 'success'}
                />
              </div>

              <div className="resultIntro">
                <div>
                  <div className="panelKicker">Incident assessment</div>
                  <h2>{result.title}</h2>
                </div>
                <span className={`statusPill ${result.escalation ? 'danger' : 'success'}`}>
                  {result.escalation ? 'Human review required' : 'Safe to continue'}
                </span>
              </div>

              <p className="summary">{result.summary}</p>

              <section className="sectionBlock">
                <div className="sectionHeading">
                  <div>
                    <div className="panelKicker">Runbook</div>
                    <h3>Recommended workflow</h3>
                  </div>
                  <span>{result.steps.length} steps</span>
                </div>
                <div className="workflow">
                  {result.steps.map((step, index) => (
                    <article className="workflowStep" key={`${index}-${step}`}>
                      <span>{String(index + 1).padStart(2, '0')}</span>
                      <p>{step}</p>
                    </article>
                  ))}
                </div>
              </section>

              <section className="sectionBlock">
                <div className="sectionHeading">
                  <div>
                    <div className="panelKicker">Grounding</div>
                    <h3>Evidence</h3>
                  </div>
                  <span>{result.sources.length} sources</span>
                </div>
                <div className="sources">
                  {result.sources.map((source, index) => {
                    const percent = Math.round(source.score * 100)
                    return (
                      <article className={index === 0 ? 'primarySource' : ''} key={source.id}>
                        <div className="sourceHead">
                          <div>
                            <strong>{source.id}</strong>
                            {index === 0 && <span className="bestMatch">Best match</span>}
                          </div>
                          <span>{percent}% match</span>
                        </div>
                        <h4>{source.title}</h4>
                        <p>{source.excerpt}</p>
                        <div className="scoreTrack" aria-label={`${percent}% evidence match`}>
                          <span style={{ width: `${percent}%` }} />
                        </div>
                      </article>
                    )
                  })}
                </div>
              </section>
            </>
          )}
        </section>
      </section>
    </main>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="stat">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

function Metric({
  label,
  value,
  toneName,
}: {
  label: string
  value: string
  toneName: string
}) {
  return (
    <div className={`metric ${toneName}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

function tone(value: string) {
  const normalized = value.toLowerCase()
  if (normalized.includes('critical') || normalized.includes('high')) return 'danger'
  if (normalized.includes('medium') || normalized.includes('moderate')) return 'warning'
  return 'success'
}

function confidenceTone(value: string) {
  const normalized = value.toLowerCase()
  if (normalized.includes('high')) return 'success'
  if (normalized.includes('medium')) return 'warning'
  return 'danger'
}

function formatDate(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(date)
}
