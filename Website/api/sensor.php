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
if (strlen(API_KEY) < 32) { http_response_code(500); exit; }

// ── Rate limiting ─────────────────────────────────────────────────────────────
// Uses a small flat file so no extra dependencies are needed.
// POST (sensor writes): max 5 requests per minute per IP.
// GET  (dashboard reads): max 30 requests per minute per IP.
function check_rate_limit(string $action): void {
    $ip      = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $limits  = ['POST' => 5, 'GET' => 30];   // requests allowed per window
    $window  = 60;                             // seconds
    $max     = $limits[$action] ?? 10;

    $dir     = sys_get_temp_dir() . '/rl_sensor';
    if (!is_dir($dir)) mkdir($dir, 0700, true);

    // One file per IP + action, e.g. /tmp/rl_sensor/POST_127_0_0_1
    $file    = $dir . '/' . $action . '_' . preg_replace('/[^a-f0-9:]/', '_', $ip);
    $now     = time();
    $entries = [];

    if (file_exists($file)) {
        $entries = array_filter(
            explode("\n", trim(file_get_contents($file))),
            fn($t) => is_numeric($t) && ($now - (int)$t) < $window
        );
    }

    if (count($entries) >= $max) {
        header('Retry-After: ' . $window);
        http_response_code(429);
        echo json_encode(['error' => 'Too many requests – slow down']);
        exit;
    }

    $entries[] = $now;
    file_put_contents($file, implode("\n", $entries), LOCK_EX);
}

// ── CORS / headers ────────────────────────────────────────────────────────────
// In production the origin must be https://hogetoorn.com.
// Add APP_ENV=development to your .env when working locally so the dashboard
// can reach the API from http://localhost without changing this file.
$allowed_origin = 'https://hogetoorn.com';
$request_origin = $_SERVER['HTTP_ORIGIN'] ?? '';

$is_dev = (($_ENV['APP_ENV'] ?? '') === 'development');
$origin_ok = ($request_origin === $allowed_origin)
          || ($is_dev && in_array($request_origin, ['http://localhost', 'http://127.0.0.1'], true));

header('Content-Type: application/json');
if ($origin_ok) {
    header('Access-Control-Allow-Origin: ' . $request_origin);
    header('Vary: Origin'); // tell caches that the response differs by origin
}
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

// ── POST: ingest a new reading ────────────────────────────────────────────────
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    check_rate_limit('POST');

    $key = $_SERVER['HTTP_X_API_KEY'] ?? '';
    if (!hash_equals(API_KEY, $key)) {
        http_response_code(401);
        echo json_encode(['error' => 'Unauthorized']);
        exit;
    }

    $body = json_decode(file_get_contents('php://input'), true);
    $t = isset($body['temperature']) ? (float)$body['temperature'] : null;
    $h = isset($body['humidity'])    ? (float)$body['humidity']    : null;
    $p = isset($body['pressure'])    ? (float)$body['pressure']    : null;

    if ($t === null || $h === null || $p === null) {
        http_response_code(400);
        echo json_encode(['error' => 'Missing fields: temperature, humidity, pressure']);
        exit;
    }

    if ($t < -50 || $t > 80 || $h < 0 || $h > 100 || $p < 800 || $p > 1100) { 
        http_response_code(422);
        exit;
    }
    $db  = get_db();
    $now = time();

    // Insert new reading
    $stmt = $db->prepare('INSERT INTO readings (recorded_at, temperature, humidity, pressure) VALUES (?, ?, ?, ?)');
    $stmt->execute([$now, $t, $h, $p]);

    // Prune old data
    $cutoff = $now - (DAYS_KEEP * 86400);
    $db->prepare('DELETE FROM readings WHERE recorded_at < ?')->execute([$cutoff]);

    http_response_code(201);
    echo json_encode(['ok' => true, 'recorded_at' => $now]);
    exit;
}

// ── GET: return last 7 days of readings ───────────────────────────────────────
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    check_rate_limit('GET');

    $db     = get_db();
    $cutoff = time() - (DAYS_KEEP * 86400);

    $stmt = $db->prepare('SELECT recorded_at, temperature, humidity, pressure
                          FROM readings WHERE recorded_at >= ?
                          ORDER BY recorded_at ASC
                          LIMIT 10080');
    $stmt->execute([$cutoff]);
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // Build typed arrays for the dashboard
    $timestamps   = [];
    $temperatures = [];
    $humidities   = [];
    $pressures    = [];

    foreach ($rows as $r) {
        $timestamps[]   = (int)$r['recorded_at'];
        $temperatures[] = (float)$r['temperature'];
        $humidities[]   = (float)$r['humidity'];
        $pressures[]    = (float)$r['pressure'];
    }

    // Latest reading for the stat cards
    $latest = !empty($rows) ? end($rows) : null;

    echo json_encode([
        'ok'          => true,
        'count'       => count($rows),
        'latest'      => $latest ? [
            'recorded_at' => (int)$latest['recorded_at'],
            'temperature' => (float)$latest['temperature'],
            'humidity'    => (float)$latest['humidity'],
            'pressure'    => (float)$latest['pressure'],
        ] : null,
        'series' => [
            'timestamps'   => $timestamps,
            'temperatures' => $temperatures,
            'humidities'   => $humidities,
            'pressures'    => $pressures,
        ]
    ]);
    exit;
}

http_response_code(405);
echo json_encode(['error' => 'Method not allowed']);