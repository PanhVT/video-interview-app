import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import TopBar from "../../shared/components/TopBar";
import { useSession } from "../session/SessionContext";

export default function InstructionsPage() {
  const nav = useNavigate();
  const { token, questions } = useSession();

  useEffect(() => {
    if (!token) nav("/");
  }, [token, nav]);

  const totalQuestions = questions?.length || 5;

  return (
    <div className="guide-screen theme-transition">
      <TopBar />

      <div className="guide-frame">
        <div className="guide-card theme-transition">
          <h2 className="guide-title">Interview guide</h2>
          <p className="guide-subtitle">
            Here&apos;s how your recording session will work.
          </p>

          <ul className="guide-list">
            <li>
              <span className="guide-label">Questions</span>
              <span className="guide-text">
                You will answer <strong>{totalQuestions}</strong> questions in
                order, one by one.
              </span>
            </li>
            <li>
              <span className="guide-label">Time per question</span>
              <span className="guide-text">
                Each question has a <strong>2 minute</strong> countdown. When
                time is up, the recording automatically stops and uploads.
              </span>
            </li>
            <li>
              <span className="guide-label">Start / Stop</span>
              <span className="guide-text">
                Use the <strong>Start</strong> button to begin recording and the
                same button (now labeled <strong>Stop now</strong>) to end
                early. Your answer will immediately start uploading.
              </span>
            </li>
            <li>
              <span className="guide-label">Upload result</span>
              <span className="guide-text">
                After each question you&apos;ll see whether the upload was{" "}
                <strong>successful</strong> or
                <strong> failed</strong>. If it fails, use{" "}
                <strong>Reload upload</strong> to try again.
              </span>
            </li>
            <li>
              <span className="guide-label">One-time retry</span>
              <span className="guide-text">
                For each question you may <strong>Retake</strong> your answer{" "}
                <strong>once</strong> after a successful upload. The new
                recording will replace the previous file.
              </span>
            </li>
            <li>
              <span className="guide-label">Finish</span>
              <span className="guide-text">
                After you have successfully uploaded all answers, use{" "}
                <strong>Finish interview</strong> to complete your session.
              </span>
            </li>
          </ul>

          <div className="guide-actions">
            <button className="btn secondary" onClick={() => nav("/preview")}>
              Back
            </button>
            <button className="btn primary" onClick={() => nav("/interview")}>
              Start Interview
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
