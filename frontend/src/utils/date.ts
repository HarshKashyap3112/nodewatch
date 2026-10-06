export function parseUtcDate(dateStr?: string | null): Date | null {
  if (!dateStr) return null;
  let str = String(dateStr).trim();
  if (str && !str.endsWith('Z') && !str.includes('+')) {
    str += 'Z';
  }
  return new Date(str);
}

export function formatLocalTime(dateStr?: string | null): string {
  const d = parseUtcDate(dateStr);
  if (!d || isNaN(d.getTime())) return 'Never';
  return d.toLocaleTimeString();
}

export function formatLocalDateTime(dateStr?: string | null): string {
  const d = parseUtcDate(dateStr);
  if (!d || isNaN(d.getTime())) return 'Never';
  return d.toLocaleString();
}
