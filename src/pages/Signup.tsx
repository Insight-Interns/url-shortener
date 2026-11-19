import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { UserPlus, ArrowLeft } from "lucide-react";
import Navbar from "../components/Navbar";
import { SketchCard } from "../components/ui/SketchCard";
import { SketchInput } from "../components/ui/SketchInput";
import { SketchButton } from "../components/ui/SketchButton";
import GoogleSignInButton from "../components/GoogleSignInButton";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";

export const Signup: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errors, setErrors] = useState<{
    name?: string;
    email?: string;
    password?: string;
    confirmPassword?: string;
    form?: string;
  }>({});
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: {
      name?: string;
      email?: string;
      password?: string;
      confirmPassword?: string;
      form?: string;
    } = {};

    if (!name.trim()) {
      newErrors.name = "Full name is required";
    }

    if (!email.trim()) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = "Please enter a valid email";
    }

    if (!password) {
      newErrors.password = "Password is required";
    } else if (password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    } else if (!/[A-Z]/.test(password)) {
      newErrors.password = "Password must contain at least one uppercase letter";
    } else if (!/[a-z]/.test(password)) {
      newErrors.password = "Password must contain at least one lowercase letter";
    } else if (!/\d/.test(password)) {
      newErrors.password = "Password must contain at least one number";
    }

    if (password !== confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    setErrors(newErrors);

    if (Object.keys(newErrors).length === 0) {
      setIsLoading(true);
      try {
        const response = await api.post("/auth/register", {
          email: email.trim().toLowerCase(),
          password,
          full_name: name.trim(),
        });
        login(response.data.access_token, response.data.user);
        navigate("/dashboard", {
          replace: true,
          state: { authMessage: "Successfully signed in" },
        });
      } catch (err: any) {
        console.error("Registration failed", err);
        const detail = err.response?.data?.detail;
        setErrors({
          form: typeof detail === "string" ? detail : "Registration failed. Please try again.",
        });
      } finally {
        setIsLoading(false);
      }
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
                <UserPlus className="w-6 h-6 text-stone-900" />
              </div>
              <h1 className="text-3xl font-sketch font-bold text-stone-900">
                Create Account
              </h1>
              <p className="text-stone-600 text-sm mt-1">
                Start managing, customizing, and tracking links
              </p>
            </div>

            <form onSubmit={handleSubmit} className="flex flex-col gap-3.5">
              {errors.form && (
                <div className="p-3 bg-red-50 border border-red-500 rounded text-red-700 font-sketch text-sm">
                  {errors.form}
                </div>
              )}
              <SketchInput
                label="Full Name"
                type="text"
                placeholder="Jane Doe"
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  if (errors.name) setErrors((prev) => ({ ...prev, name: undefined }));
                }}
                error={errors.name}
                disabled={isLoading}
              />

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
                placeholder="At least 6 characters"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (errors.password) setErrors((prev) => ({ ...prev, password: undefined }));
                }}
                error={errors.password}
                disabled={isLoading}
              />

              <SketchInput
                label="Confirm Password"
                type="password"
                placeholder="Repeat password"
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  if (errors.confirmPassword) setErrors((prev) => ({ ...prev, confirmPassword: undefined }));
                }}
                error={errors.confirmPassword}
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
                  <UserPlus className="w-4 h-4" />
                  <span>{isLoading ? "Creating account..." : "Sign Up"}</span>
                </SketchButton>
              </div>

              <div className="flex items-center justify-between text-sm pt-2">
                <Link
                  to="/"
                  className="inline-flex items-center gap-1 font-sketch text-stone-600 hover:text-stone-900 underline"
                >
                  <ArrowLeft className="w-3.5 h-3.5" />
                  Back to Home
                </Link>

                <p className="text-stone-600 font-sans text-xs">
                  Already have an account?{" "}
                  <Link to="/login" className="font-sketch text-sm text-stone-900 underline font-semibold">
                    Log In
                  </Link>
                </p>
              </div>
            </form>
            <div className="my-4 flex items-center gap-3 text-xs text-stone-500">
              <span className="h-px flex-1 bg-stone-300" />
              <span>or</span>
              <span className="h-px flex-1 bg-stone-300" />
            </div>
            <GoogleSignInButton />
          </SketchCard>
        </div>
      </main>
    </div>
  );
};

export default Signup;

