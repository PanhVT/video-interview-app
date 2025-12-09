import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import useRecorder from "../../shared/hooks/useRecorder";
import { useSession } from "../session/SessionContext";
import { startSession } from "../../shared/api/startSession";
import { uploadOne } from "../../shared/api/uploadOne";
import { finishSession } from "../../shared/api/finishSession";
import TopBar from "../../shared/components/TopBar";
import white_cat from "../../assets/white_cat.png";
import black_cat from "../../assets/black_cat.png";

const MAX_TIME = 120;

export default function InterviewPage() {
  const {
    token,
    userName,
    folder,
    setFolder,
    setUserName,
    questions = [],
  } = useSession();
  const nav = useNavigate();

  const videoRef = useRef(null);
  const timerRef = useRef(null);
  const lastBlobRef = useRef(null);
  const [stream, setStream] = useState(null);

  const recorder = useRecorder();
  const [index, setIndex] = useState(0);
  const [status, setStatus] = useState("idle"); // idle | recording | uploading
  const [sessionStarted, setSessionStarted] = useState(false);
  const [timeLeft, setTimeLeft] = useState(MAX_TIME);
  const [uploadState, setUploadState] = useState("idle"); // idle | uploading | success | error
  const [message, setMessage] = useState("");

  const initialFlags = useMemo(
    () => Array(questions.length).fill(false),
    [questions.length]
  );
  const [retakeFlags, setRetakeFlags] = useState(initialFlags);
  const [completedFlags, setCompletedFlags] = useState(initialFlags);

  useEffect(() => {
    if (!token) nav("/");
  }, [token, nav]);

  useEffect(() => {
    if (!sessionStarted) return;
    let streamHandle;
    async function loadStream() {
      try {
        streamHandle = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: true,
        });
        setStream(streamHandle);
        if (videoRef.current) videoRef.current.srcObject = streamHandle;
      } catch (err) {
        console.error(err);
        alert("Unable to access camera/microphone");
      }
    }
    loadStream();
    return () => {
      if (streamHandle) streamHandle.getTracks().forEach((t) => t.stop());
    };
  }, [sessionStarted]);

  const clearTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const resetTimer = useCallback(() => setTimeLeft(MAX_TIME), []);

  const updateCompletedFlag = useCallback(
    (value) => {
      setCompletedFlags((prev) => {
        const next = [...prev];
        next[index] = value;
        return next;
      });
    },
    [index]
  );

  const stopAndUpload = useCallback(async () => {
    if (status !== "recording") return;
    clearTimer();
    setStatus("uploading");
    setUploadState("uploading");
    setMessage("Uploading answer...");

    const blob = await recorder.stop();
    if (!blob) {
      alert("Nothing recorded");
      setStatus("idle");
      setUploadState("idle");
      setMessage("");
      return;
    }
    lastBlobRef.current = blob;

    const response = await uploadOne({
      token,
      folder,
      questionIndex: index + 1,
      blob,
    });

    if (!response.ok) {
      setUploadState("error");
      setMessage("Upload failed. Please retry.");
      setStatus("idle");
      return;
    }

    setUploadState("success");
    setMessage("Upload successful.");
    setStatus("idle");
    updateCompletedFlag(true);
  }, [status, clearTimer, recorder, token, folder, index, updateCompletedFlag]);

  const handleStartRecording = useCallback(async () => {
    if (!stream) {
      alert("Camera not ready");
      return;
    }
    setStatus("recording");
    setUploadState("idle");
    setMessage("");
    resetTimer();
    await recorder.start(stream);
    clearTimer();
    timerRef.current = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearTimer();
          stopAndUpload();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }, [stream, recorder, clearTimer, resetTimer, stopAndUpload]);

  const toggleRecording = useCallback(() => {
    if (status === "recording") {
      stopAndUpload();
    } else {
      handleStartRecording();
    }
  }, [status, handleStartRecording, stopAndUpload]);

  useEffect(() => () => clearTimer(), [clearTimer]);

  async function handleStartSession() {
    const res = await startSession(token, userName);
    if (res.ok) {
      setFolder(res.folder);
      // Use server-provided sanitized username so client and server agree
      if (res.sanitizedUserName) setUserName(res.sanitizedUserName);
      setSessionStarted(true);
    } else {
      alert("Failed to start session");
    }
  }

  const handleRetryUpload = async () => {
    if (!lastBlobRef.current) {
      alert("No recording to upload.");
      return;
    }
    setUploadState("uploading");
    setMessage("Re-uploading answer...");
    const res = await uploadOne({
      token,
      folder,
      questionIndex: index + 1,
      blob: lastBlobRef.current,
    });
    if (!res.ok) {
      setUploadState("error");
      setMessage("Upload failed again. Please retry.");
      return;
    }
    setUploadState("success");
    setMessage("Upload successful.");
    updateCompletedFlag(true);
  };

  const handleRetake = () => {
    if (uploadState !== "success" || retakeFlags[index]) return;
    setRetakeFlags((prev) => {
      const next = [...prev];
      next[index] = true;
      return next;
    });
    updateCompletedFlag(false);
    lastBlobRef.current = null;
    setUploadState("idle");
    setMessage("");
    resetTimer();
  };

  const handleNextQuestion = () => {
    if (uploadState !== "success" || index >= questions.length - 1) return;
    setIndex((prev) => prev + 1);
    setUploadState("idle");
    setMessage("");
    lastBlobRef.current = null;
    resetTimer();
  };

  const handleFinish = async () => {
    const allRecorded = completedFlags.every(Boolean) && questions.length > 0;
    if (!allRecorded) return;
    clearTimer();
    await finishSession(token, folder, questions.length);
    nav("/finish");
  };

  const formattedTime = `${String(Math.floor(timeLeft / 60)).padStart(
    1,
    "0"
  )}:${String(timeLeft % 60).padStart(2, "0")}`;
  const canRetake = uploadState === "success" && !retakeFlags[index];
  const canNext = uploadState === "success" && index < questions.length - 1;
  const canFinish = completedFlags.every(Boolean) && questions.length > 0;

  if (!sessionStarted) {
    return (
      <div className="interview-start-screen theme-transition">
        <TopBar />
        <div className="start-card theme-transition">
          <h2>Interview</h2>
          <p>
            Make sure you're ready. The interview begins when you start
            recording.
          </p>
          <button className="btn primary" onClick={handleStartSession}>
            Start Session
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="interview-screen theme-transition">
      <TopBar />
      <img class="bg-left2" src={white_cat} />
      <img class="bg-right2" src={black_cat} />
      <div className="interview-frame">
        <div className="interview-content theme-transition">
          <div className="question-row">
            <div className="question-strip theme-transition">
              {questions.map((_, i) => (
                <div
                  key={i}
                  className={`question-pill ${i === index ? "active" : ""} ${
                    completedFlags[i] ? "done" : ""
                  }`}
                >
                  {i + 1}
                </div>
              ))}
            </div>
            <div className="prompt-card theme-transition">
              {questions[index] || "No question loaded."}
            </div>
          </div>

          <div className="video-stage theme-transition">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="interview-video"
            />

            <div
              className={`timer-pill ${
                timeLeft <= 30 && status === "recording" ? "warning" : ""
              }`}
            >
              {formattedTime}
            </div>

            {status === "uploading" && (
              <div className="uploading-state">Uploading answer...</div>
            )}
          </div>

          {message && (
            <div className={`upload-banner theme-transition ${uploadState}`}>
              <span>{message}</span>
              {uploadState === "error" && (
                <button onClick={handleRetryUpload}>Reload Upload</button>
              )}
              {uploadState === "success" && (
                <div className="upload-banner-actions">
                  {canRetake && (
                    <button onClick={handleRetake}>Retake (one time)</button>
                  )}
                  {canNext && (
                    <button onClick={handleNextQuestion}>Next Question</button>
                  )}
                  {canFinish && (
                    <button onClick={handleFinish}>Finish Interview</button>
                  )}
                </div>
              )}
            </div>
          )}
          {uploadState !== "success" && (
            <div className="interview-actions">
              <button
                className="pill-btn primary"
                onClick={toggleRecording}
                disabled={status === "uploading"}
              >
                {status === "recording" ? "Stop Now" : "Start"}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
