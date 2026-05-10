/**
 * SummaryCard.jsx
 *
 * Reusable KPI metric card component.
 * Displays dashboard summary stats such as:
 * - Total Transactions
 * - Review Queue
 * - Escalated
 * - Blocked
 *
 * Uses color variants and icons.
 */


import {
  BarChart3,
  ClipboardList,
  ShieldAlert,
  Ban,
  CheckCircle
} from "lucide-react";

const iconMap = {
  total: BarChart3,
  review: ClipboardList,
  escalated: ShieldAlert,
  blocked: Ban,
  approved: CheckCircle,
};

function SummaryCard({ title, value, subtitle, variant, iconKey }) {
  const Icon = iconMap[iconKey];

  return (
    <div className={`summary-card-kpi summary-card-kpi-${variant}`}>
      <div className="summary-card-kpi-top">
        <div className="summary-card-kpi-title-group">
          <div className="summary-card-kpi-icon">
            {Icon ? <Icon size={18} strokeWidth={2.2} /> : null}
          </div>
          <span className="summary-card-kpi-title">{title}</span>
        </div>

        <div className="summary-card-kpi-value">{value}</div>
      </div>

      <div className="summary-card-kpi-subtitle">{subtitle}</div>
    </div>
  );
}

export default SummaryCard;