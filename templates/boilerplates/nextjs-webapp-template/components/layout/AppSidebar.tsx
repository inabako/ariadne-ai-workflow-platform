import { Activity, BarChart3, Home, Settings } from "lucide-react";

import { APP_NAME } from "@/lib/constants";

const navItems = [
  { label: "Overview", icon: Home, active: true },
  { label: "Metrics", icon: BarChart3, active: false },
  { label: "Events", icon: Activity, active: false },
  { label: "Settings", icon: Settings, active: false },
];

export function AppSidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-title">{APP_NAME}</span>
        <span className="brand-subtitle">Next.js template</span>
      </div>
      <nav className="nav-list" aria-label="Primary navigation">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <a
              className={item.active ? "nav-item active" : "nav-item"}
              href={item.active ? "#overview" : "#"}
              key={item.label}
            >
              <Icon aria-hidden="true" />
              <span>{item.label}</span>
            </a>
          );
        })}
      </nav>
    </aside>
  );
}
