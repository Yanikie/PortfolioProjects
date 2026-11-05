<?php
// FocusBlok status. POST from the iPhone Shortcut (with X-API-Key), GET for the website.
// GET only returns on/off, never the time, so visitors can't read a daily rhythm from it.

// -------- Config --------
function load_env(string $path): void {
    if (!file_exists($path)) {
        http_response_code(500);
        echo json_encode(['error' => 'Server configuration missing']);
        exit;
    }
    foreach (file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
        if (str_starts_with(trim($line), '#')) continue;
        [$key, $val] = explode('=', $line, 2);
        $_ENV[trim($key)] = trim($val);
    }
}

load_env(dirname($_SERVER['DOCUMENT_ROOT']) . '/.env');

define('FOCUS_KEY', $_ENV['FOCUS_KEY'] ?? '');
define('DB_HOST', $_ENV['DB_HOST']);
define('DB_NAME', $_ENV['DB_NAME']);
define('DB_USER', $_ENV['DB_USER']);
define('DB_PASS', $_ENV['DB_PASS']);
if (strlen(FOCUS_KEY) < 32) { http_response_code(500); exit; }

header('Content-Type: application/json');
header('Cache-Control: no-store');

// -------- Rate limiting --------
// POST: 10 per minute per IP. GET: 30 per minute per IP.
function check_rate_limit(string $action): void {
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $max = $action === 'POST' ? 10 : 30;
    $window = 60;

    $dir = sys_get_temp_dir() . '/rl_focus';
    if (!is_dir($dir)) mkdir($dir, 0700, true);

    $file = $dir . '/' . $action . '_' . preg_replace('/[^a-f0-9:]/', '_', $ip);
    $now = time();
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
        echo json_encode(['error' => 'Too many requests']);
        exit;
    }

    $entries[] = $now;
    file_put_contents($file, implode("\n", $entries), LOCK_EX);
}

// -------- Database --------
function get_db(): PDO {
    $dsn = 'mysql:host=' . DB_HOST . ';dbname=' . DB_NAME . ';charset=utf8mb4';
    $db = new PDO($dsn, DB_USER, DB_PASS);
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // One row (id 1) with the current state
    $db->exec('CREATE TABLE IF NOT EXISTS focus_status (
        id         TINYINT UNSIGNED PRIMARY KEY,
        state      VARCHAR(3)   NOT NULL,
        changed_at INT UNSIGNED NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4');

    return $db;
}

// -------- POST: save the state --------
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    check_rate_limit('POST');

    $key = $_SERVER['HTTP_X_API_KEY'] ?? '';
    if (!hash_equals(FOCUS_KEY, $key)) {
        http_response_code(401);
        echo json_encode(['error' => 'Unauthorized']);
        exit;
    }

    $body = json_decode(file_get_contents('php://input'), true);
    $state = $body['state'] ?? null;
    if (!in_array($state, ['on', 'off'], true)) {
        http_response_code(400);
        echo json_encode(['error' => 'state must be "on" or "off"']);
        exit;
    }

    $stmt = get_db()->prepare('REPLACE INTO focus_status (id, state, changed_at) VALUES (1, ?, ?)');
    $stmt->execute([$state, time()]);

    echo json_encode(['ok' => true, 'state' => $state]);
    exit;
}

// -------- GET: current state --------
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    check_rate_limit('GET');

    $row = get_db()->query('SELECT state FROM focus_status WHERE id = 1')->fetch(PDO::FETCH_ASSOC);
    echo json_encode(['ok' => true, 'state' => $row ? $row['state'] : null]);
    exit;
}

http_response_code(405);
echo json_encode(['error' => 'Method not allowed']);
