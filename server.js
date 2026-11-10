// 极简静态服务器：服务 public/ 目录，支持 --port / --host 参数转发
const http = require('http');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
function argVal(names, dflt) {
  for (let i = 0; i < args.length; i++) {
    for (const n of names) {
      if (args[i] === n && args[i + 1]) return args[i + 1];
      if (args[i].startsWith(n + '=')) return args[i].slice(n.length + 1);
    }
  }
  return dflt;
}
const PORT = parseInt(argVal(['--port', '-p'], process.env.PORT || '7100'), 10);
const HOST = argVal(['--host', '-h'], process.env.HOST || '127.0.0.1');
const ROOT = path.join(__dirname, 'public');

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.mp4': 'video/mp4',
  '.mp3': 'audio/mpeg'
};

http.createServer((req, res) => {
  let urlPath = decodeURIComponent(req.url.split('?')[0]);
  if (urlPath.endsWith('/')) urlPath += 'index.html';
  const filePath = path.join(ROOT, path.normalize(urlPath).replace(/^([.][.][/\\])+/, ''));
  if (!filePath.startsWith(ROOT)) { res.writeHead(403); res.end('Forbidden'); return; }
  fs.readFile(filePath, (err, data) => {
    if (err) { res.writeHead(404); res.end('Not Found'); return; }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(filePath).toLowerCase()] || 'application/octet-stream' });
    res.end(data);
  });
}).listen(PORT, HOST, () => {
  console.log(`薪火 · 非遗数字展馆  →  http://${HOST}:${PORT}/`);
});
