import type { Metadata } from "next";
import "./globals.css";
import LayoutShell from "./layout-shell";
import { AuthProvider } from "@/lib/auth-context";

export const metadata: Metadata = {
  title: "Spotify Aura — Discovery Companion",
  description: "AI-native music discovery MVP — real Spotify catalog, real Claude reasoning.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <LayoutShell>{children}</LayoutShell>
        </AuthProvider>
      </body>
    </html>
  );
}
