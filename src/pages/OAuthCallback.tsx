import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function OAuthCallback() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [message, setMessage] = useState("Completing Google sign-in...");

  useEffect(() => {
    const params = new URLSearchParams(window.location.hash.slice(1));
    const accessToken = params.get("access_token");
    window.history.replaceState(null, "", window.location.pathname);

    if (!accessToken) {
      setMessage("Google sign-in did not complete. Please try again.");
      return;
    }

    localStorage.setItem("auth_token", accessToken);
    api.get("/auth/me")
      .then(({ data }) => {
        login(accessToken, data);
        navigate("/dashboard", {
          replace: true,
          state: { authMessage: "Successfully signed in" },
        });
      })
      .catch(() => {
        localStorage.removeItem("auth_token");
        localStorage.removeItem("auth_user");
        setMessage("Could not verify your account. Please try again.");
      });
  }, [navigate, login]);

  return (
    <main className="min-h-screen flex items-center justify-center bg-[#faf8f5] px-4">
      <p className="font-sketch text-lg text-stone-800" role="status">{message}</p>
    </main>
  );
}
