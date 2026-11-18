import React, { useState, useRef, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { Link2, LogIn, Home as HomeIcon, History, User as UserIcon, LogOut, ChevronDown } from "lucide-react";
import { SketchButton } from "./ui/SketchButton";
import { useAuth } from "../context/AuthContext";

export const Navbar: React.FC = () => {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="w-full border-b-2 border-stone-800 bg-[#fdfbf7] py-3.5 px-4 sm:px-8">
      <div className="max-w-4xl mx-auto flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group">
          <div className="p-1.5 bg-amber-200 border-2 border-stone-800 rounded">
            <Link2 className="w-5 h-5 text-stone-900 group-hover:rotate-12 transition-transform" />
          </div>
          <span className="font-sketch text-2xl font-bold tracking-wide text-stone-900">
            ShortLinker
          </span>
        </Link>

        <nav className="flex items-center gap-2 sm:gap-3">
          {location.pathname !== "/" && (
            <Link to="/">
              <SketchButton size="sm" variant="secondary">
                <HomeIcon className="w-4 h-4" />
                <span className="hidden sm:inline">Home</span>
              </SketchButton>
            </Link>
          )}

          <Link to="/history">
            <SketchButton
              size="sm"
              variant={location.pathname === "/history" ? "primary" : "secondary"}
            >
              <History className="w-4 h-4" />
              <span>History</span>
            </SketchButton>
          </Link>

          {/* If authenticated: Show Name & Email Badge with Logout */}
          {isAuthenticated && user ? (
            <div className="relative" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => setDropdownOpen((prev) => !prev)}
                className="flex items-center gap-2 px-3 py-1.5 bg-amber-100 hover:bg-amber-200 border-2 border-stone-800 rounded transition-colors cursor-pointer text-left"
              >
                <div className="w-7 h-7 rounded-full bg-amber-300 border border-stone-800 flex items-center justify-center font-sketch font-bold text-stone-900 text-sm shrink-0">
                  {(user.full_name || user.email).charAt(0).toUpperCase()}
                </div>
                <div className="flex flex-col text-left max-w-[130px] sm:max-w-[180px] leading-tight">
                  <span className="font-sketch font-bold text-stone-900 text-sm truncate">
                    {user.full_name || user.email.split("@")[0]}
                  </span>
                  <span className="text-[11px] font-sans text-stone-600 truncate">
                    {user.email}
                  </span>
                </div>
                <ChevronDown className="w-4 h-4 text-stone-700 shrink-0" />
              </button>

              {/* Dropdown Menu */}
              {dropdownOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-white border-2 border-stone-800 rounded shadow-lg p-2 z-50">
                  <div className="px-3 py-2 border-b border-stone-200 mb-2">
                    <p className="font-sketch font-bold text-stone-900 text-sm truncate">
                      {user.full_name || "User"}
                    </p>
                    <p className="text-xs font-sans text-stone-500 truncate">
                      {user.email}
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() => {
                      setDropdownOpen(false);
                      logout();
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm font-sketch font-bold text-red-700 hover:bg-red-50 rounded transition-colors cursor-pointer"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Log Out</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            /* If not authenticated: Show Login & Sign Up buttons */
            <>
              {location.pathname !== "/login" && location.pathname !== "/signup" && (
                <>
                  <Link to="/login">
                    <SketchButton size="sm" variant="secondary">
                      <LogIn className="w-4 h-4" />
                      <span>Login</span>
                    </SketchButton>
                  </Link>
                  <Link to="/signup">
                    <SketchButton size="sm" variant="primary">
                      <span>Sign Up</span>
                    </SketchButton>
                  </Link>
                </>
              )}

              {location.pathname === "/login" && (
                <Link to="/signup">
                  <SketchButton size="sm" variant="primary">
                    <span>Sign Up</span>
                  </SketchButton>
                </Link>
              )}

              {location.pathname === "/signup" && (
                <Link to="/login">
                  <SketchButton size="sm" variant="primary">
                    <LogIn className="w-4 h-4" />
                    <span>Login</span>
                  </SketchButton>
                </Link>
              )}
            </>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Navbar;

