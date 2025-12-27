const http = require('http');
const fs = require('fs');
const path = require('path');

const hostname = '127.0.0.1';
const port = 3000;

const server = http.createServer((req, res) => {
  let filePath = '';
  
  if (req.url === '/' || req.url === '/index.html') {
    filePath = path.join(__dirname, 'file_download.html');
  } else if (req.url.startsWith('/download/')) {
    // 处理下载请求
    const fileName = req.url.substring(10); // 移除 '/download/' 前缀
    filePath = path.join(__dirname, decodeURIComponent(fileName));
    
    // 设置强制下载的HTTP头
    const ext = path.extname(filePath).toLowerCase();
    const fileNameForDownload = path.basename(filePath);
    
    res.setHeader('Content-Type', 'application/octet-stream');
    res.setHeader('Content-Disposition', `attachment; filename="${encodeURIComponent(fileNameForDownload)}"`);
    res.setHeader('Content-Transfer-Encoding', 'binary');
    
    fs.createReadStream(filePath).pipe(res);
    return;
  } else {
    // 直接提供文件
    filePath = path.join(__dirname, decodeURIComponent(req.url));
    const extname = path.extname(filePath).toLowerCase();
    
    // 根据文件扩展名设置内容类型
    const mimeTypes = {
      '.html': 'text/html',
      '.js': 'text/javascript',
      '.css': 'text/css',
      '.json': 'application/json',
      '.png': 'image/png',
      '.jpg': 'image/jpg',
      '.gif': 'image/gif',
      '.wav': 'audio/wav',
      '.mp4': 'video/mp4',
      '.woff': 'application/font-woff',
      '.ttf': 'application/font-ttf',
      '.eot': 'application/vnd.ms-fontobject',
      '.otf': 'application/font-otf',
      '.svg': 'application/image/svg+xml',
      '.bcm': 'application/octet-stream',
      '.bat': 'application/octet-stream',
      '.py': 'text/plain'
    };
    
    const contentType = mimeTypes[extname] || 'application/octet-stream';
    res.setHeader('Content-Type', contentType);
  }
  
  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404);
        res.end('404 Not Found');
      } else {
        res.writeHead(500);
        res.end(`Server Error: ${err.code}`);
      }
    } else {
      res.writeHead(200);
      res.end(content, 'utf-8');
    }
  });
});

server.listen(port, hostname, () => {
  console.log(`服务器运行在 http://${hostname}:${port}/`);
  console.log('请在浏览器中打开上面的地址访问文件下载页面');
});