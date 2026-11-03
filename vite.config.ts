import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  esbuild: {
    target: "esnext",
    supported: {
      destructuring: true,
    },
  },
  build: {
    target: "esnext",
  },
  optimizeDeps: {
    esbuildOptions: {
      target: "esnext",
      supported: {
        destructuring: true,
      },
    },
  },
  server: {
    host: "127.0.0.1",
    port: 5173,
  },
});
