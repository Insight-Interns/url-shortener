const apiBaseURL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

export default function GoogleSignInButton() {
  const startGoogleSignIn = () => {
    window.location.assign(`${apiBaseURL.replace(/\/$/, "")}/auth/google/login`);
  };

  return (
    <button
      type="button"
      onClick={startGoogleSignIn}
      className="w-full rounded border-2 border-stone-800 bg-white px-4 py-2.5 font-sketch font-semibold text-stone-900 hover:bg-amber-50 transition-colors"
    >
      Continue with Google
    </button>
  );
}
