function StatusBadge({ text, variant = "status" }) {
  const className = text.toLowerCase().replace(/\s+/g, "-");

  return (
    <span className={`badge ${variant}-badge ${className}`}>
      {text}
    </span>
  );
}

export default StatusBadge;