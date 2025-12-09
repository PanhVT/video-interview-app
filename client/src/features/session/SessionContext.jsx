import React, { createContext, useContext, useState } from "react";

const SessionContext = createContext();
export function SessionProvider({ children }) {
  const [token, setToken] = useState("");
  const [userName, setUserName] = useState("");
  const [folder, setFolder] = useState("");
  const [questions] = useState([
    "Tell us about yourself.",
    "Why do you want this role?",
    "Describe a challenging project and how you handled it.",
    "How do you work in a team?",
    "Any questions for us?",
  ]);
  return (
    <SessionContext.Provider
      value={{
        token,
        setToken,
        userName,
        setUserName,
        folder,
        setFolder,
        questions,
      }}
    >
      {children}
    </SessionContext.Provider>
  );
}
export function useSession() {
  return useContext(SessionContext);
}
