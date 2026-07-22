import type { Metadata } from "next";
import "./globals.css";
import ThemeControls from "@/components/theme/ThemeControls";

export const metadata: Metadata = {
  title: "BUILD. DO. HAVE.™",
  description: "Turn what you know into something you own.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        {children}
        <ThemeControls />
      </body>
    </html>
  );
}
