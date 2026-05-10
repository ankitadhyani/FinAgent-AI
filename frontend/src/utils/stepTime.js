


export function convertStep(step) {
  const day = Math.floor((step - 1) / 24) + 1;
  const hour = ((step - 1) % 24) + 1;
  return `Day ${day}, Hr ${hour}`;
}