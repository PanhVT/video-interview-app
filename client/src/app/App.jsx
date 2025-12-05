import { Routes, Route } from "react-router-dom";
import LoginPage from "../features/auth/loginPage";
import PreviewPage from "../features/preview/PreviewPage";
import InterviewPage from "../features/interview/InterviewPage";
import InstructionsPage from "../features/interview/InstructionsPage";
import FinishPage from "../features/finish/FinishPage";
import { SessionProvider } from "../features/session/SessionContext";

export default function App() {
  return (
    <SessionProvider>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/preview" element={<PreviewPage />} />
        <Route path="/guide" element={<InstructionsPage />} />
        <Route path="/interview" element={<InterviewPage />} />
        <Route path="/finish" element={<FinishPage />} />
      </Routes>
    </SessionProvider>
  );
}
