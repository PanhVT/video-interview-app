import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { verifyToken } from "../../shared/api/verifyToken";
import { useSession } from "../session/SessionContext";
import TopBar from "../../shared/components/TopBar";

export default function LoginPage() {
  const nav = useNavigate();
  const { setToken, setUserName } = useSession();
  const [tokenInput, setTokenInput] = useState("");
  const [nameInput, setNameInput] = useState("");
  const [error, setError] = useState("");

  const onStart = async () => {
    setError("");
    if (!tokenInput || !nameInput) {
      setError("Vui lòng nhập token và tên");
      return;
    }
    try {
      const res = await verifyToken(tokenInput);
      if (res.ok) {
        setToken(tokenInput);
        setUserName(nameInput);
        nav("/preview");
      } else {
        // Hiển thị error message chi tiết hơn
        const errorMsg = res.error || res.detail || "Token không hợp lệ";
        setError(errorMsg);
      }
    } catch (e) {
      console.error("Login error:", e);
      setError(
        "Không thể kết nối đến server. Vui lòng kiểm tra server có đang chạy không."
      );
    }
  };

  return (
    <div className="login-screen theme-transition">
      <TopBar />
      <div className="login-inner app-container">
        <div className="login-left">
          <h2 className="login-title">
            <span className="title-main">WEB INTERVIEW</span>
            <br />
            <span className="title-sub">RECORDER</span>
          </h2>

          <div className="login-form">
            <div className="field">
              <input
                placeholder="Enter interview token"
                value={tokenInput}
                onChange={(e) => setTokenInput(e.target.value)}
              />
            </div>

            <div className="field">
              <input
                placeholder="Enter full name"
                value={nameInput}
                onChange={(e) => setNameInput(e.target.value)}
              />
            </div>

            <div style={{ marginTop: 18 }}>
              <button className="btn-primary" onClick={onStart}>
                START SESSION
              </button>
            </div>

            {error && <p className="error">{error}</p>}
          </div>
        </div>

        <div className="login-right">
          {/* Right side artwork provided via CSS background (cat_tower.jpg) */}
        </div>
      </div>
    </div>
  );
}
