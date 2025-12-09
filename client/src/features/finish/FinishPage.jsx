import { useNavigate } from "react-router-dom";
import TopBar from "../../shared/components/TopBar";
import { useSession } from "../session/SessionContext";
import cat_shop from "../../assets/cat_shop.png";
import house from "../../assets/japan_house.png";

export default function FinishPage() {
  const nav = useNavigate();
  const { userName, folder } = useSession();

  function stripDiacriticsAndSpaces(name) {
    if (!name) return name;
    // Normalize and remove combining diacritic marks
    const normalized = name.normalize("NFKD").replace(/\p{Diacritic}/gu, "");
    // Remove any non-alphanumeric characters (including spaces)
    return normalized.replace(/[^A-Za-z0-9]/g, "");
  }

  return (
    <div className="finish-screen theme-transition">
      <TopBar />
      <img class="bg-left" src={cat_shop} />
      <img class="bg-right" src={house} />
      <div className="center-box">
        <h2 className="finish-title">
          Thank you, {stripDiacriticsAndSpaces(userName) || "candidate"}!
        </h2>
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
