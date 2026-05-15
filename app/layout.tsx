import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";


export const metadata: Metadata = {
  title: "Annapurna | Authentic Meal Planning",
  description: "India-first, culture-aware AI meal planner and grocery assistant.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className="antialiased"
        suppressHydrationWarning
      >
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
