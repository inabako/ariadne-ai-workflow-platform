import type { ReactNode } from "react";

import { APP_VERSION } from "@/lib/constants";

import { AppHeader } from "./AppHeader";
import { AppSidebar } from "./AppSidebar";

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="app-shell">
      <AppSidebar />
      <div className="shell-body">
        <AppHeader />
        <main className="main">{children}</main>
        <footer className="footer">Version {APP_VERSION}</footer>
      </div>
    </div>
  );
}
