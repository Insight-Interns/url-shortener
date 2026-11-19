import React, { useState, useEffect, useMemo, useCallback } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  History,
  Calendar,
  ExternalLink,
  Trash2,
  Filter,
  PlusCircle,
  RefreshCw,
  Search,
  Lock,
  Crown,
} from "lucide-react";
import Navbar from "../components/Navbar";
import { SketchCard } from "../components/ui/SketchCard";
import { SketchButton } from "../components/ui/SketchButton";
import CopyButton from "../components/CopyButton";
import { URLHistoryItem } from "../types";
import { useAuth } from "../context/AuthContext";
import { api } from "../services/api";
import { normalizePlanTier, PLAN_DETAILS } from "../config/plans";

const MONTH_NAMES = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

export const HistoryPage: React.FC = () => {
  const { user, isAuthenticated, token } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const currentDate = new Date();
  const currentYear = currentDate.getFullYear().toString();
  const currentMonth = (currentDate.getMonth() + 1).toString().padStart(2, "0");

  const [links, setLinks] = useState<URLHistoryItem[]>([]);
  const [selectedYear, setSelectedYear] = useState<string>("all");
  const [selectedMonth, setSelectedMonth] = useState<string>("all");
  const [currentMonthOnly, setCurrentMonthOnly] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [loadError, setLoadError] = useState("");
  const [authMessage, setAuthMessage] = useState("");

  useEffect(() => {
    const message = (location.state as { authMessage?: string } | null)?.authMessage;
    if (message) {
      setAuthMessage(message);
      navigate(location.pathname, { replace: true, state: null });
    }
  }, [location.pathname, location.state, navigate]);

  useEffect(() => {
    if (!authMessage) return;
    const timeout = window.setTimeout(() => setAuthMessage(""), 2000);
    return () => window.clearTimeout(timeout);
  }, [authMessage]);

  // Fetch URLs created by the authenticated user from the backend API
  const fetchUserLinks = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const response = await api.get<URLHistoryItem[]>("/urls");
      setLinks(response.data);
      setLoadError("");
    } catch (err) {
      console.error("Failed to load user links from backend", err);
      setLinks([]);
      setLoadError("We couldn't load your saved links. Check your connection and try again.");
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchUserLinks();
    }
  }, [isAuthenticated, fetchUserLinks]);

  const handleDelete = async (item: URLHistoryItem) => {
    if (!item.id) return;
    try {
      await api.delete(`/urls/${item.id}`);
      setLinks((prev) => prev.filter((link) => link.id !== item.id));
      setLoadError("");
    } catch (error) {
      console.error("Failed to delete link on backend", error);
      setLoadError("We couldn't delete that link. Please refresh and try again.");
    }
  };

  // Extract available years from saved links (plus current year as default option)
  const availableYears = useMemo(() => {
    const years = new Set<string>();
    years.add(currentYear);
    links.forEach((link) => {
      if (link.created_at) {
        const d = new Date(link.created_at);
        if (!isNaN(d.getTime())) {
          years.add(d.getFullYear().toString());
        }
      }
    });
    return Array.from(years).sort((a, b) => Number(b) - Number(a));
  }, [links, currentYear]);

  // Filter links based on year, month, current-month toggle, and search
  const filteredLinks = useMemo(() => {
    return links.filter((link) => {
      const date = link.created_at ? new Date(link.created_at) : null;
      if (!date || isNaN(date.getTime())) return true;

      const linkYear = date.getFullYear().toString();
      const linkMonth = (date.getMonth() + 1).toString().padStart(2, "0");

      if (currentMonthOnly) {
        if (linkYear !== currentYear || linkMonth !== currentMonth) {
          return false;
        }
      } else {
        if (selectedYear !== "all" && linkYear !== selectedYear) {
          return false;
        }
        if (selectedMonth !== "all" && linkMonth !== selectedMonth) {
          return false;
        }
      }

      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const matchesLong = link.long_url?.toLowerCase().includes(query);
        const matchesShort = link.short_url?.toLowerCase().includes(query);
        const matchesCode = link.short_code?.toLowerCase().includes(query);
        if (!matchesLong && !matchesShort && !matchesCode) {
          return false;
        }
      }

      return true;
    });
  }, [
    links,
    currentMonthOnly,
    selectedYear,
    selectedMonth,
    currentYear,
    currentMonth,
    searchQuery,
  ]);

  const currentMonthLabel = `${MONTH_NAMES[currentDate.getMonth()]} ${currentYear}`;

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex flex-col bg-[#faf8f5]">
        <Navbar />
        <main className="flex-1 flex items-center justify-center px-4 py-12">
          <SketchCard variant="yellow" className="text-center p-8 max-w-md">
            <Lock className="w-10 h-10 text-amber-800 mx-auto mb-3" />
            <h2 className="font-sketch text-2xl font-bold text-stone-900 mb-2">
              Authentication Required
            </h2>
            <p className="text-stone-600 text-sm mb-6">
              Link history is private and only available to logged in users.
            </p>
            <div className="flex justify-center gap-3">
              <Link to="/login">
                <SketchButton size="md" variant="primary">
                  Log In
                </SketchButton>
              </Link>
              <Link to="/signup">
                <SketchButton size="md" variant="secondary">
                  Sign Up
                </SketchButton>
              </Link>
            </div>
          </SketchCard>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#faf8f5]">
      <Navbar />

      <main className="flex-1 max-w-4xl mx-auto w-full px-4 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="p-1.5 bg-amber-200 border-2 border-stone-800 rounded">
                <History className="w-5 h-5 text-stone-900" />
              </span>
              <h1 className="font-sketch text-3xl font-bold text-stone-900">
                Your Dashboard
              </h1>
            </div>
            <p className="text-stone-600 text-sm">
              Your links are saved to your account and available when you sign in.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Link to="/">
              <SketchButton size="sm" variant="primary">
                <PlusCircle className="w-4 h-4" />
                <span>Shorten New</span>
              </SketchButton>
            </Link>
          </div>
        </div>

        <SketchCard variant="yellow" className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="flex items-center gap-2 font-sketch font-bold text-stone-900">
              <Crown className="h-4 w-4 text-amber-800" />
              {PLAN_DETAILS[normalizePlanTier(user?.tier)].name} plan
            </p>
            <p className="text-sm text-stone-700">
              {PLAN_DETAILS[normalizePlanTier(user?.tier)].maxDays === null
                ? "Your links can stay active permanently."
                : `Your links can stay active for up to ${PLAN_DETAILS[normalizePlanTier(user?.tier)].maxDays} days.`}
            </p>
          </div>
          <Link to="/plans">
            <SketchButton size="sm" variant="secondary">Go Premium</SketchButton>
          </Link>
        </SketchCard>

        {loadError && <p className="mb-4 rounded border border-red-400 bg-red-50 p-3 text-sm text-red-700" role="alert">{loadError}</p>}

        {/* Filter Controls Card */}
        <SketchCard variant="white" className="mb-6">
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-stone-200 pb-3">
              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-stone-600" />
                <span className="font-sketch font-bold text-base text-stone-800">
                  Filters
                </span>
                {currentMonthOnly && (
                  <span className="text-xs px-2 py-0.5 bg-amber-100 border border-stone-800 rounded font-sketch text-amber-900">
                    Showing: {currentMonthLabel} only
                  </span>
                )}
              </div>

              {/* Show Current Month Only Switch */}
              <button
                type="button"
                onClick={() => setCurrentMonthOnly(!currentMonthOnly)}
                className={`flex items-center gap-2 px-3 py-1.5 border-2 border-stone-800 rounded font-sketch text-sm transition-colors cursor-pointer ${
                  currentMonthOnly
                    ? "bg-amber-300 text-stone-900 font-bold"
                    : "bg-stone-100 text-stone-600 hover:bg-stone-200"
                }`}
              >
                <Calendar className="w-4 h-4" />
                <span>
                  {currentMonthOnly ? "✓ Current Month Only" : "Show Current Month Only"}
                </span>
              </button>
            </div>

            {/* Year & Month Dropdowns (Disabled/Secondary when Current Month Only is selected) */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {/* Year Select */}
              <div>
                <label className="block text-xs font-sketch font-semibold text-stone-700 mb-1">
                  Year
                </label>
                <select
                  value={currentMonthOnly ? currentYear : selectedYear}
                  disabled={currentMonthOnly}
                  onChange={(e) => setSelectedYear(e.target.value)}
                  className="w-full border-2 border-stone-800 rounded px-3 py-2 bg-white text-stone-900 text-sm focus:outline-none disabled:opacity-50 disabled:bg-stone-100"
                >
                  <option value="all">All Years</option>
                  {availableYears.map((year) => (
                    <option key={year} value={year}>
                      {year}
                    </option>
                  ))}
                </select>
              </div>

              {/* Month Select */}
              <div>
                <label className="block text-xs font-sketch font-semibold text-stone-700 mb-1">
                  Month
                </label>
                <select
                  value={currentMonthOnly ? currentMonth : selectedMonth}
                  disabled={currentMonthOnly}
                  onChange={(e) => setSelectedMonth(e.target.value)}
                  className="w-full border-2 border-stone-800 rounded px-3 py-2 bg-white text-stone-900 text-sm focus:outline-none disabled:opacity-50 disabled:bg-stone-100"
                >
                  <option value="all">All Months</option>
                  {MONTH_NAMES.map((name, index) => {
                    const val = (index + 1).toString().padStart(2, "0");
                    return (
                      <option key={val} value={val}>
                        {name}
                      </option>
                    );
                  })}
                </select>
              </div>

              {/* Search query */}
              <div>
                <label className="block text-xs font-sketch font-semibold text-stone-700 mb-1">
                  Search URL or Code
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search link..."
                    className="w-full border-2 border-stone-800 rounded px-3 py-2 pl-8 bg-white text-stone-900 text-sm focus:outline-none"
                  />
                  <Search className="w-4 h-4 text-stone-400 absolute left-2.5 top-2.5" />
                </div>
              </div>
            </div>
          </div>
        </SketchCard>

        {/* Links List */}
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs text-stone-500 px-1">
            <span>
              Showing {filteredLinks.length} {filteredLinks.length === 1 ? "link" : "links"}
            </span>
            <button
              onClick={fetchUserLinks}
              disabled={isLoading}
              className="hover:text-stone-800 flex items-center gap-1 cursor-pointer disabled:opacity-50"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Refresh</span>
            </button>
          </div>

          {isLoading ? (
            <SketchCard variant="white" className="py-8 text-center text-stone-600">Loading your saved links…</SketchCard>
          ) : filteredLinks.length === 0 ? (
            <SketchCard variant="yellow" className="text-center py-10">
              <History className="w-10 h-10 text-stone-400 mx-auto mb-2" />
              <h3 className="font-sketch text-lg font-bold text-stone-800 mb-1">
                {links.length === 0 ? "No saved links yet" : "No Links Found"}
              </h3>
              <p className="text-xs text-stone-600 max-w-sm mx-auto mb-4">
                {links.length === 0
                  ? "Links you create while signed in will appear here."
                  : currentMonthOnly
                    ? `You haven't shortened any links during ${currentMonthLabel}.`
                    : "No links match the selected year and month filters."}
              </p>
              {currentMonthOnly && (
                <button
                  type="button"
                  onClick={() => setCurrentMonthOnly(false)}
                  className="inline-block px-3 py-1.5 bg-white border border-stone-800 rounded font-sketch text-xs text-stone-800 hover:bg-stone-50"
                >
                  Turn off "Current Month Only" to view all history
                </button>
              )}
            </SketchCard>
          ) : (
            filteredLinks.map((link) => {
              const dateStr = link.created_at
                ? new Date(link.created_at).toLocaleDateString(undefined, {
                    year: "numeric",
                    month: "short",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })
                : "Unknown date";

              return (
                <SketchCard
                  key={link.short_code}
                  variant="white"
                  className="transition-shadow hover:shadow-md"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div className="space-y-1 min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <a
                          href={link.short_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-amber-800 font-mono font-bold hover:underline flex items-center gap-1 text-base break-all"
                        >
                          {link.short_url}
                          <ExternalLink className="w-3.5 h-3.5 shrink-0" />
                        </a>
                        <span className="text-[11px] px-1.5 py-0.5 bg-stone-100 border border-stone-300 rounded font-mono text-stone-600 shrink-0">
                          code: {link.short_code}
                        </span>
                      </div>

                      <p
                        className="text-xs text-stone-600 truncate max-w-xl"
                        title={link.long_url}
                      >
                        <span className="font-semibold text-stone-700">Destination:</span>{" "}
                        {link.long_url}
                      </p>

                      <div className="flex items-center gap-3 text-[11px] text-stone-500 pt-1">
                        <span className="flex items-center gap-1">
                          <Calendar className="w-3 h-3 text-stone-400" />
                          {dateStr}
                        </span>
                        {link.expires_at && (
                          <span className="text-amber-700">
                            Expires: {new Date(link.expires_at).toLocaleDateString()}
                          </span>
                        )}
                        {!link.expires_at && <span className="text-green-700">Never expires</span>}
                        {typeof link.click_count === "number" && <span>{link.click_count} clicks</span>}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0 self-end sm:self-center">
                      <CopyButton text={link.short_url} />
                      <button
                        type="button"
                        onClick={() => handleDelete(link)}
                        title="Delete link"
                        className="p-2 border border-stone-300 rounded hover:bg-red-50 hover:border-red-400 text-stone-400 hover:text-red-600 transition-colors cursor-pointer"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </SketchCard>
              );
            })
          )}
        </div>
      </main>
      {authMessage && (
        <div
          className="fixed bottom-6 left-1/2 -translate-x-1/2 rounded-md border-2 border-stone-800 bg-amber-100 px-5 py-3 font-sketch font-semibold text-stone-900 shadow-lg"
          role="status"
          aria-live="polite"
        >
          {authMessage}
        </div>
      )}
    </div>
  );
};

export default HistoryPage;
