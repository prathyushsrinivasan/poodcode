/// <reference types="node" />
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// Tauri expects a fixed dev port and disables clearing so Rust logs stay visible.
const host = process.env.TAURI_DEV_HOST;

export default defineConfig({
  plugins: [react()],
  // Prevent Vite from obscuring Rust errors.
  clearScreen: false,
  server: {
    port: 5173,
    strictPort: true,
    host: host || false,
    hmr: host ? { protocol: "ws", host, port: 5174 } : undefined,
    watch: {
      // Don't watch the Rust backend from the frontend dev server.
      ignored: ["**/src-tauri/**"],
    },
  },
  // Produce assets Tauri can bundle from ../dist.
  build: {
    target: "es2021",
    outDir: "dist",
    sourcemap: false,
    chunkSizeWarningLimit: 2000,
  },
  test: {
    environment: "node",
    include: ["src/**/*.{test,spec}.ts"],
  },
});
