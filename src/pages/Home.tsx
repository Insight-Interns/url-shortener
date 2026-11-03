import React, { useState } from "react";
import Navbar from "../components/Navbar";
import URLForm from "../components/URLForm";
import ShortURLResult from "../components/ShortURLResult";
import { ShortenURLRequest, ShortenURLResponse } from "../types";
import { api } from "../services/api";

export const Home: React.FC = () => {
  const [result, setResult] = useState<ShortenURLResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  const handleShorten = async (data: ShortenURLRequest) => {
    setIsLoading(true);
    setApiError(null);

    try {
      // Call backend API if running
      const response = await api.post("/shorten", data);
      setResult(response.data);
    } catch (err: any) {
      console.warn("Backend API not reachable or returned error, using local fallback preview:", err);
      // Clean fallback demo for local frontend testing
      const alias = data.custom_alias || Math.random().toString(36).substring(2, 8);
      const host = window.location.origin;
      setResult({
        short_url: `${host}/${alias}`,
        original_url: data.url,
        created_at: new Date().toISOString(),
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#faf8f5]">
      <Navbar />

      <main className="flex-1 max-w-2xl mx-auto w-full px-4 py-12 flex flex-col items-center">
        {/* Hero Section */}
        <div className="text-center mb-8">
          <span className="inline-block px-3 py-1 bg-amber-100 border border-stone-800 rounded-full font-sketch text-xs text-amber-900 font-semibold mb-3">
            By Apps & Integeration Team Interns✏️
          </span>
          <h1 className="text-4xl sm:text-5xl font-sketch font-bold text-stone-900 tracking-tight mb-2">
            Make Short Work of Long Links
          </h1>
          <p className="text-stone-600 font-sans text-sm sm:text-base max-w-md mx-auto">
            Clean, memorable, and quick. Paste your lengthy destination URL below and grab your link in seconds.
          </p>
        </div>

        {/* Shortener Form */}
        <div className="w-full space-y-6">
          <URLForm onSubmit={handleShorten} isLoading={isLoading} />

          {apiError && (
            <div className="p-3 bg-red-50 border border-red-500 rounded text-red-700 font-sketch text-sm">
              {apiError}
            </div>
          )}

          {result && <ShortURLResult result={result} />}
        </div>
      </main>

      <footer className="py-6 text-center text-xs text-stone-500 border-t border-stone-200">
       
      </footer>
    </div>
  );
};

export default Home;

