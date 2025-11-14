let mediaRecorder;
let recordedChunks = [];
let currentQuestion = 0;
const questions = [
  "Introduce yourself briefly.",
  "Why are you interested in this position?",
  "Describe a challenge you faced and how you overcame it.",
];

let sessionFolder = "";
let token = "";
let userName = "";

const startBtn = document.getElementById("start-btn");
const recordBtn = document.getElementById("record-btn");
const nextBtn = document.getElementById("next-btn");
const finishBtn = document.getElementById("finish-btn");

const statusText = document.getElementById("status");
const uploadStatus = document.getElementById("upload-status");
const questionEl = document.getElementById("question");
const preview = document.getElementById("preview");

let progressBar;

startBtn.onclick = async () => {
  token = document.getElementById("token").value.trim();
  userName = document.getElementById("username").value.trim();
  if (!token || !userName) {
    alert("Please enter both token and name!");
    return;
  }

  const verify = await fetch("http://127.0.0.1:8000/api/verify-token", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });

  if (!verify.ok) {
    statusText.innerText = "❌ Invalid token!";
    return;
  }

  const res = await fetch("http://127.0.0.1:8000/api/session/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, userName }),
  });

  const data = await res.json();
  sessionFolder = data.folder;
  document.getElementById("start-section").classList.add("hidden");
  document.getElementById("record-section").classList.remove("hidden");

  questionEl.innerText = questions[currentQuestion];
  initCamera();
};

async function initCamera() {
  const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
  preview.srcObject = stream;
  mediaRecorder = new MediaRecorder(stream);
  mediaRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) recordedChunks.push(e.data);
  };
  mediaRecorder.onstop = uploadVideo;
}

recordBtn.onclick = () => {
  if (mediaRecorder.state === "inactive") {
    recordedChunks = [];
    mediaRecorder.start();
    recordBtn.innerText = "⏹ Stop Recording";
    nextBtn.disabled = true;
  } else {
    mediaRecorder.stop();
    recordBtn.innerText = "🎥 Start Recording";
  }
};

nextBtn.onclick = () => {
  if (currentQuestion < questions.length - 1) {
    currentQuestion++;
    questionEl.innerText = questions[currentQuestion];
    uploadStatus.innerText = "";
    if (progressBar) progressBar.remove();
    nextBtn.disabled = true;
  } else {
    alert("You have reached the last question!");
  }
};

finishBtn.onclick = async () => {
  const res = await fetch("http://127.0.0.1:8000/api/session/finish", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      token,
      folder: sessionFolder,
      questionsCount: questions.length,
    }),
  });
  const data = await res.json();
  if (data.ok) {
    alert("✅ Interview session finished!");
    location.reload();
  }
};

async function uploadVideo() {
  uploadStatus.innerText = "📤 Uploading...";
  if (progressBar) progressBar.remove();
  progressBar = document.createElement("progress");
  progressBar.max = 100;
  progressBar.value = 0;
  uploadStatus.after(progressBar);

  const blob = new Blob(recordedChunks, { type: "video/webm" });

  const uploadOnce = () => new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "http://127.0.0.1:8000/api/upload-one");

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        progressBar.value = (e.loaded / e.total) * 100;
      }
    };

    xhr.onload = () => {
      if (xhr.status === 200) resolve(JSON.parse(xhr.responseText));
      else reject(new Error("Upload failed"));
    };

    xhr.onerror = () => reject(new Error("Network error"));

    const formData = new FormData();
    formData.append("token", token);
    formData.append("folder", sessionFolder);
    formData.append("questionIndex", currentQuestion + 1);
    formData.append("video", blob, `Q${currentQuestion + 1}.webm`);
    xhr.send(formData);
  });

  let attempts = 0;
  const maxRetries = 3;
  while (attempts < maxRetries) {
    try {
      const data = await uploadOnce();
      if (data.ok) {
        uploadStatus.innerText = `✅ Uploaded: ${data.savedAs}`;
        progressBar.value = 100;
        nextBtn.disabled = false;
        return;
      }
      throw new Error("Upload failed");
    } catch (err) {
      attempts++;
      if (attempts < maxRetries) {
        const waitTime = 1000 * Math.pow(2, attempts);
        uploadStatus.innerText = `⚠️ Upload failed, retrying in ${waitTime / 1000}s... (Attempt ${attempts}/${maxRetries})`;
        await new Promise(r => setTimeout(r, waitTime));
      } else {
        uploadStatus.innerText = "❌ Upload failed after 3 retries. Please try again manually.";
        progressBar.value = 0;
      }
    }
  }
}
