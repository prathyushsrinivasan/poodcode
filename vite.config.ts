/// <reference types="node" />
import { readFileSync } from "node:fs";
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// Tauri expects a fixed dev port and disables clearing so Rust logs stay visible.
const host = process.env.TAURI_DEV_HOST;

const version = JSON.parse(
  readFileSync(new URL("./package.json", import.meta.url), "utf8")
).version as string;

export default defineConfig({
  plugins: [react()],
  // The About section shows the app version; reading package.json at build time
  // keeps it from drifting out of sync with a hand-written constant.
  define: { __APP_VERSION__: JSON.stringify(version) },
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
