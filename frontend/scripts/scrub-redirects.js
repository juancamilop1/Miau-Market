/** Quita _redirects del dist: Workers lo rechaza (infinite loop) con SPA assets. */
const fs = require('fs');
const path = require('path');
const targets = [
  path.join(__dirname, '..', 'dist', 'frontend', 'browser', '_redirects'),
  path.join(__dirname, '..', 'dist', 'frontend', '_redirects'),
];
for (const p of targets) {
  if (fs.existsSync(p)) {
    fs.unlinkSync(p);
    console.log(`[scrub-redirects] removed ${p}`);
  }
}
