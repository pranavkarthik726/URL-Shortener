import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  // Bind IPv4 loopback explicitly: on some machines "localhost" resolves to
  // the IPv6 loopback (::1) first, which the browser can't reach if only
  // the IPv4 side is listening (and the reverse, if only IPv6 listens).
  server: {
    host: "127.0.0.1",
  },
});
