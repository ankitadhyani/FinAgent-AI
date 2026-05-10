import "../styles/sidebar.css";

import {
  LayoutDashboard,
  ArrowLeftRight,
  Radar,
  FolderSearch,
  FileText,
  SlidersHorizontal
} from "lucide-react";


const Sidebar = ({ activePage, setActivePage }) => {
  const menu = [
    { label: "Overview", icon: LayoutDashboard },
    { label: "Transactions", icon: ArrowLeftRight },
    { label: "Fraud Detection", icon: Radar },
    { label: "Investigations", icon: FolderSearch },
    { label: "Reports", icon: FileText },
    { label: "Rules & Models", icon: SlidersHorizontal }
  ];

  return (
    <aside className="sidebar">
        <div className="sidebar-brand">
            <div className="brand-icon">
                <img src="/finagent-logo.png" alt="logo" className="brand-logo" />
            </div>

            <div className="brand-text">
                <span className="brand-main">FinAgent</span>
                <span className="brand-sub">Risk Intelligence</span>
            </div>
        </div>

      <nav className="sidebar-nav">
        {menu.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.label}
              className={`sidebar-item ${activePage === item.label ? "active" : ""}`}
              onClick={() => setActivePage(item.label)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
};

export default Sidebar;
