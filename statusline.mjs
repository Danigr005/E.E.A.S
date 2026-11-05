// Status line: model · context (tokens used / auto-compact window) · cache hit · 5h and 7d usage.
// Input: Claude Code's session JSON on stdin. Keep it light: it runs on every refresh.
import { readFileSync } from 'node:fs';
import { homedir } from 'node:os';

let raw = '';
process.stdin.on('data', (c) => (raw += c)).on('end', () => {
  let j = {};
  try { j = JSON.parse(raw); } catch { /* no data: print whatever we have */ }

  const cw = j.context_window ?? {};
  const size = cw.context_window_size ?? 0;
  const used = Math.round(((cw.used_percentage ?? 0) / 100) * size);

  let compactAt = Infinity;
  try {
    const s = JSON.parse(readFileSync(`${homedir()}/.claude/settings.json`, 'utf8'));
    if (Number.isFinite(s.autoCompactWindow)) compactAt = s.autoCompactWindow;
  } catch { /* no settings: fall back to the window size */ }
  const win = Math.min(size || Infinity, compactAt);

  const k = (n) => (n >= 1000 ? `${Math.round(n / 1000)}k` : `${n}`);
  const parts = [`[${j.model?.display_name ?? '?'}]`];
  if (Number.isFinite(win)) parts.push(`ctx ${k(used)}/${k(win)}`);

  const hit = j.prompt_cache?.hit_ratio;
  if (hit != null) parts.push(`cache ${Math.round(hit * 100)}%`);

  const rl = j.rate_limits ?? {};
  const h5 = rl.five_hour?.used_percentage ?? rl['5h']?.used_percentage;
  const d7 = rl.seven_day?.used_percentage;
  if (h5 != null) parts.push(`5h ${Math.floor(h5)}%`);
  if (d7 != null) parts.push(`7d ${Math.floor(d7)}%`);

  const fill = Number.isFinite(win) && win > 0 ? used / win : 0;
  let out = parts.join(' · ');
  if (fill >= 0.8) out += ' · /compact now';
  else if (fill >= 0.6) out += ' · /compact soon';
  process.stdout.write(out);
});
