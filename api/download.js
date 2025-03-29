import path from 'path';
import fs from 'fs';

export default function handler(req, res) {
  const filePath = path.join(process.cwd(), 'public/downloads/speedflow.exe');
  const fileStream = fs.createReadStream(filePath);
  
  res.setHeader('Content-Type', 'application/octet-stream');
  res.setHeader('Content-Disposition', 'attachment; filename=speedflow.exe');
  
  fileStream.pipe(res);
}
