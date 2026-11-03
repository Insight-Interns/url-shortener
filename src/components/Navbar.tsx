import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Link2, LogIn, Home as HomeIcon } from "lucide-react";
import { SketchButton } from "./ui/SketchButton";

export const Navbar: React.FC = () => {
  const location = useLocation();

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

        <nav className="flex items-center gap-3">
          {location.pathname !== "/" && (
            <Link to="/">
              <SketchButton size="sm" variant="secondary">
                <HomeIcon className="w-4 h-4" />
                <span>Home</span>
              </SketchButton>
            </Link>
          )}

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
        </nav>
      </div>
    </header>
  );
};

export default Navbar;

