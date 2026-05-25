const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const csv = require('csv-parse/sync');

const app = express();
const PORT = 3000;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Multer config for file uploads
const upload = multer({
  dest: 'uploads/',
  fileFilter: (req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase();
    if (ext === '.csv' || ext === '.json') cb(null, true);
    else cb(new Error('Only CSV or JSON files allowed'));
  },
  limits: { fileSize: 10 * 1024 * 1024 }
});

// Ensure data directory exists
const DATA_FILE = path.join(__dirname, 'data', 'sensor_data.json');
if (!fs.existsSync(path.join(__dirname, 'data'))) {
  fs.mkdirSync(path.join(__dirname, 'data'), { recursive: true });
}
if (!fs.existsSync(path.join(__dirname, 'uploads'))) {
  fs.mkdirSync(path.join(__dirname, 'uploads'), { recursive: true });
}

// Initialize with placeholder data if no data exists
function initializePlaceholderData() {
  const now = Date.now();
  const readings = [];
  for (let i = 120; i >= 0; i--) {
    const t = now - i * 60000;
    readings.push({
      timestamp: new Date(t).toISOString(),
      temperature: parseFloat((19 + 4 * Math.sin(i / 20) + (Math.random() - 0.5) * 0.6).toFixed(2)),
      humidity: parseFloat((52 + 10 * Math.cos(i / 25) + (Math.random() - 0.5) * 1.2).toFixed(2)),
      pressure: parseFloat((1013.2 + 2 * Math.sin(i / 40) + (Math.random() - 0.5) * 0.4).toFixed(2))
    });
  }
  return { readings, uploadedAt: new Date().toISOString(), source: 'placeholder' };
}

if (!fs.existsSync(DATA_FILE)) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(initializePlaceholderData(), null, 2));
}

// Serve index for all non-API routes (SPA)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`\n  Portfolio running at http://localhost:${PORT}\n`);
});