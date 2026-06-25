import { RefreshCw } from "lucide-react";

import { APP_NAME } from "@/lib/constants";

export function AppHeader() {
  return (
    <header className="header">
      <div>
        <div className="header-title">{APP_NAME}</div>
        <div className="header-meta">Dashboard shell</div>
      </div>
      <RefreshCw aria-label="Refresh status" size={20} />
    </header>
  );
}
