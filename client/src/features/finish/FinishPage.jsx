import { useNavigate } from 'react-router-dom'
import TopBar from '../../shared/components/TopBar'
import { useSession } from '../session/SessionContext'

export default function FinishPage() {
  const nav = useNavigate()
  const { userName, folder } = useSession()

  return (
    <div className="finish-screen theme-transition">
      <TopBar />

      <div className="finish-frame">
        <div className="finish-card theme-transition">
          <h2 className="finish-title">Thank you, {userName || 'candidate'}!</h2>
          <p className="finish-subtitle">
            Your interview has been successfully completed and stored.
          </p>

          <div className="finish-meta">
            <span className="finish-label">Storage folder</span>
            <span className="finish-value">
              {folder || 'Folder will appear here once generated.'}
            </span>
          </div>

          <div className="finish-actions">
            <button
              className="preview-btn primary"
              type="button"
              onClick={() => nav('/')}
            >
              Close &amp; return to start
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}