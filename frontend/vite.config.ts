import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Vite configuration
export default defineConfig({

  // React and Tailwind plugins
  plugins: [
    react(),
    tailwindcss(),
  ],

  // Local development API proxy
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },

});