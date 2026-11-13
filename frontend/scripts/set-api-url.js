/**
 * Inyecta API_URL (env) en environment.prod.ts e index.html antes del build de Pages.
 * Uso: API_URL=https://xxx.onrender.com npm run build:pages
 */
const fs = require('fs');
const path = require('path');

const DEFAULT_API = 'https://miau-market-api.onrender.com';
const apiUrl = (process.env.API_URL || DEFAULT_API).trim().replace(/\/$/, '');
const envFile = path.join(__dirname, '..', 'src', 'environments', 'environment.prod.ts');
const indexFile = path.join(__dirname, '..', 'src', 'index.html');

const envContent = `export const environment = {
  production: true,
  apiUrl: '${apiUrl.replace(/'/g, "\\'")}',
};
`;
fs.writeFileSync(envFile, envContent, 'utf8');
console.log(`[set-api-url] environment.prod.ts apiUrl=${apiUrl || '(vacio)'}`);

if (fs.existsSync(indexFile)) {
  let html = fs.readFileSync(indexFile, 'utf8');
  html = html.replace(
    /<meta name="miau-api" content="[^"]*">/,
    `<meta name="miau-api" content="${apiUrl}">`
  );
  fs.writeFileSync(indexFile, html, 'utf8');
}
