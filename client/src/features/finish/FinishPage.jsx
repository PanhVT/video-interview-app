import { useNavigate } from "react-router-dom";
import TopBar from "../../shared/components/TopBar";
import { useSession } from "../session/SessionContext";
import cat_shop from "../../assets/cat_shop.png";
import house from "../../assets/japan_house.png";

export default function FinishPage() {
  const nav = useNavigate();
  const { userName, folder } = useSession();

  return (
    <div className="finish-screen theme-transition">
      <TopBar />
      <img class="bg-left" src={cat_shop} />
      <img class="bg-right" src={house} />
      <div className="center-box">
        <h2 className="finish-title">Thank you, {userName || "candidate"}!</h2>
        <p className="finish-subtitle">
          Your interview has been successfully completed and stored.
        </p>

        <div className="finish-meta">
          <span className="finish-label">Storage folder</span>
          <span className="finish-value">
            {folder || "Folder will appear here once generated."}
          </span>
        </div>

        <div className="finish-actions">
          <button
            className="btn primary"
            type="button"
            onClick={() => nav("/")}
          >
            Close &amp; return to start
          </button>
        </div>
      </div>
    </div>
  );
}
