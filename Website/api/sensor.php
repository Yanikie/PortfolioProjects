<?php
// ── Config ────────────────────────────────────────────────────────────────────
function load_env(string $path): void {
    if (!file_exists($path)) {
        http_response_code(500);
        echo json_encode(['error' => 'Server configuration missing']);
        exit;
    }
    foreach (file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
        if (str_starts_with(trim($line), '#')) continue; // skip comments
        [$key, $val] = explode('=', $line, 2);
        $_ENV[trim($key)] = trim($val);
    }
}

load_env(dirname($_SERVER['DOCUMENT_ROOT']) . '/.env');

define('API_KEY',   $_ENV['API_KEY']);
define('DB_HOST',   $_ENV['DB_HOST']);
define('DB_NAME',   $_ENV['DB_NAME']);
define('DB_USER',   $_ENV['DB_USER']);
define('DB_PASS',   $_ENV['DB_PASS']);
define('DAYS_KEEP', 7);


// ── CORS / headers ────────────────────────────────────────────────────────────
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: https://hogetoorn.com');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, X-API-Key');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }

// ── DB bootstrap ─────────────────────────────────────────────────────────────
function get_db(): PDO {
    $dsn = 'mysql:host=' . DB_HOST . ';dbname=' . DB_NAME . ';charset=utf8mb4';
    $db  = new PDO($dsn, DB_USER, DB_PASS);
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Create table if it doesn't exist yet
    $db->exec('CREATE TABLE IF NOT EXISTS readings (
        id          INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        recorded_at INT UNSIGNED     NOT NULL,
        temperature FLOAT            NOT NULL,
        humidity    FLOAT            NOT NULL,
        pressure    FLOAT            NOT NULL,
        INDEX idx_recorded_at (recorded_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4');

    return $db;
}

// ── The POST and GET handlers below are identical to the previous version ─────
// (paste them in unchanged from the SQLite version)