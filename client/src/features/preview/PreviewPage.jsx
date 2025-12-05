import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../session/SessionContext";
import TopBar from "../../shared/components/TopBar";

export default function PreviewPage() {
  const videoRef = useRef();
  const nav = useNavigate();
  const { token } = useSession();
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) {
      nav("/");
    }
  }, [token, nav]);

  useEffect(() => {
    let stream;
    async function startPreview() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        if (videoRef.current) videoRef.current.srcObject = stream;
      } catch (e) {
        setError("Permission denied or no devices");
      }
    }
    startPreview();
    return () => {
      if (stream) stream.getTracks().forEach((t) => t.stop());
    };
  }, []);

  return (
    <div className="preview-screen theme-transition">
      <TopBar className="preview-topbar" />
      <div className="preview-window theme-transition">
        <div className="preview-header">
          <div>
            <p className="preview-title">Ready to join?</p>
            <p className="preview-subtitle">
              Check your camera and microphone before you begin.
            </p>
          </div>
          <div className="preview-status">
            <span className="status-dot" />
            Devices are ready
          </div>
        </div>

        <div className="preview-video-wrapper">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="preview-video"
          />
          {error && <p className="preview-error">{error}</p>}
        </div>

        <div className="preview-actions">
          <button className="preview-btn secondary" onClick={() => nav("/")}>
            Back
          </button>
          <button className="preview-btn primary" onClick={() => nav("/guide")}>
            Interview Instructions
          </button>
        </div>
      </div>
    </div>
  );
}
