import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { LogIn, ArrowLeft } from "lucide-react";
import Navbar from "../components/Navbar";
import { SketchCard } from "../components/ui/SketchCard";
import { SketchInput } from "../components/ui/SketchInput";
import { SketchButton } from "../components/ui/SketchButton";

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: { email?: string; password?: string } = {};

    if (!email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = "Please enter a valid email";
    }

    if (!password) {
      newErrors.password = "Password is required";
    } else if (password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
    }

    setErrors(newErrors);

    if (Object.keys(newErrors).length === 0) {
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
        navigate("/");
      }, 700);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#faf8f5]">
      <Navbar />

      <main className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          <SketchCard variant="white">
            <div className="text-center mb-6">
              <div className="inline-flex p-2 bg-amber-100 border-2 border-stone-800 rounded-full mb-2">
                <LogIn className="w-6 h-6 text-stone-900" />
              </div>
              <h1 className="text-3xl font-sketch font-bold text-stone-900">
                Welcome Back
              </h1>
              <p className="text-stone-600 text-sm mt-1">
                Log in to manage and track your shortened links
              </p>
            </div>

            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <SketchInput
                label="Email Address"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (errors.email) setErrors((prev) => ({ ...prev, email: undefined }));
                }}
                error={errors.email}
                disabled={isLoading}
              />

              <SketchInput
                label="Password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (errors.password) setErrors((prev) => ({ ...prev, password: undefined }));
                }}
                error={errors.password}
                disabled={isLoading}
              />

              <div className="pt-2">
                <SketchButton
                  type="submit"
                  variant="primary"
                  size="md"
                  className="w-full"
                  disabled={isLoading}
                >
                  <LogIn className="w-4 h-4" />
                  <span>{isLoading ? "Signing in..." : "Sign In"}</span>
                </SketchButton>
              </div>

              <div className="flex items-center justify-between text-sm mt-3">
                <Link
                  to="/"
                  className="inline-flex items-center gap-1 font-sketch text-stone-600 hover:text-stone-900 underline"
                >
                  <ArrowLeft className="w-3.5 h-3.5" />
                  Back to Home
                </Link>

                <p className="text-stone-600 font-sans text-xs">
                  Don't have an account?{" "}
                  <Link to="/signup" className="font-sketch text-sm text-stone-900 underline font-semibold">
                    Sign Up
                  </Link>
                </p>
              </div>
            </form>
          </SketchCard>
        </div>
      </main>
    </div>
  );
};

export default Login;

