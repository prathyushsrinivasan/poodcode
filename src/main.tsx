import React from "react";
import ReactDOM from "react-dom/client";
import { HashRouter } from "react-router-dom";
import App from "./App";
import "./styles/global.css";

function mount() {
  ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
      <HashRouter>
        <App />
      </HashRouter>
    </React.StrictMode>
  );
}

// `npm run dev:mock` serves the UI from JSON fixtures instead of Tauri, so the
// app can be opened in an ordinary browser. The literal comparison is what lets
// a production build drop the import (and the 17 MB of seeds behind it)
// entirely — `import.meta.env.VITE_MOCK` is substituted at build time.
if (import.meta.env.VITE_MOCK === "1") {
  import("./dev/mockBackend").then(({ installMockBackend }) => {
    installMockBackend();
    mount();
  });
} else {
  mount();
}
