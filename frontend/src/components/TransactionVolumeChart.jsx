import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

const axisTick = { fontSize: 12, fill: "#94a3b8", fontWeight: 600 };
const axisLabel = { fill: "#94a3b8", fontSize: 12, fontWeight: 700 };
const gridColor = "rgba(148, 163, 184, 0.16)";

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;

  const data = payload[0]?.payload;

  return (
    <div className="chart-tooltip">
      <p className="tooltip-title">{label}</p>

      <div className="tooltip-main-stats">
        <div className="tooltip-row">
          <span>Total Transactions</span>
          <strong>{data.total}</strong>
        </div>
        <div className="tooltip-row">
          <span>Flagged Transactions</span>
          <strong>{data.flagged}</strong>
        </div>
      </div>

      <div className="tooltip-divider"></div>

      <div className="tooltip-breakdown">
        <div className="tooltip-row approve-row">
          <span>APPROVE</span>
          <strong>{data.approve}</strong>
        </div>
        <div className="tooltip-row review-row">
          <span>REVIEW</span>
          <strong>{data.review}</strong>
        </div>
        <div className="tooltip-row escalate-row">
          <span>ESCALATE</span>
          <strong>{data.escalate}</strong>
        </div>
        <div className="tooltip-row block-row">
          <span>BLOCK</span>
          <strong>{data.block}</strong>
        </div>
      </div>
    </div>
  );
}

function TransactionVolumeChart({ data }) {
  return (
    <div className="chart-section">
      <div className="chart-card">
        <div className="chart-header">
          <h2>Transaction Volume</h2>
          <p>Transaction activity and flagged risk trend across timestamps.</p>
        </div>

        <div className="chart-plot">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data}
              margin={{ top: 26, right: 18, left: 4, bottom: 30 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />

              <XAxis
                dataKey="timestamp"
                interval="preserveStartEnd"
                minTickGap={20}
                tick={axisTick}
                axisLine={{ stroke: "rgba(148, 163, 184, 0.24)" }}
                tickLine={false}
                label={{
                  value: "Timestamp",
                  position: "insideBottom",
                  offset: -14,
                  style: axisLabel,
                }}
              />

              <YAxis
                allowDecimals={false}
                domain={[0, "dataMax + 1"]}
                tick={axisTick}
                axisLine={{ stroke: "rgba(148, 163, 184, 0.24)" }}
                tickLine={false}
                label={{
                  value: "Transaction Count",
                  angle: -90,
                  position: "insideLeft",
                  style: { ...axisLabel, textAnchor: "middle" },
                }}
              />

              <Tooltip content={<CustomTooltip />} />
              <Legend
                verticalAlign="top"
                align="right"
                wrapperStyle={{
                  top: 0,
                  right: 20,
                  color: "#cbd5e1",
                  fontSize: 13,
                  fontWeight: 700,
                }}
              />

              <Line
                type="linear"
                dataKey="total"
                stroke="#60a5fa"
                strokeWidth={2.5}
                dot={{ r: 4, strokeWidth: 2, fill: "#0b1220" }}
                activeDot={{ r: 6, strokeWidth: 2, fill: "#60a5fa" }}
                name="Total Transactions"
              />

              <Line
                type="linear"
                dataKey="flagged"
                stroke="#f97316"
                strokeWidth={2.5}
                dot={{ r: 4, strokeWidth: 2, fill: "#0b1220" }}
                activeDot={{ r: 6, strokeWidth: 2, fill: "#f97316" }}
                name="Flagged Transactions"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default TransactionVolumeChart;
