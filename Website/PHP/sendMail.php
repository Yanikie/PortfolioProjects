<?php
// ── Session (needed for CSRF token storage) ───────────────────────────────────
session_start();

// ────────────────────────────────────────────────────────────────────────────
// TOKEN GENERATION ENDPOINT
// When your HTML form page loads it hits this file with ?csrf=1 (GET) to
// receive a fresh token, which it stores in a hidden input.
// ────────────────────────────────────────────────────────────────────────────
if ($_SERVER['REQUEST_METHOD'] === 'GET' && ($_GET['csrf'] ?? '') === '1') {
    $token = bin2hex(random_bytes(32));
    $_SESSION['csrf_token'] = $token;
    header('Content-Type: application/json');
    echo json_encode(['token' => $token]);
    exit;
}

// ── Only accept POST from here on ─────────────────────────────────────────────
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    exit('Method Not Allowed');
}

// ── Rate limiting ─────────────────────────────────────────────────────────────
// Max 3 submissions per 10 minutes per IP.
function check_rate_limit(): void {
    $ip     = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $window = 600; // 10 minutes in seconds
    $max    = 3;

    $dir  = sys_get_temp_dir() . '/rl_mail';
    if (!is_dir($dir)) mkdir($dir, 0700, true);

    $file    = $dir . '/' . preg_replace('/[^a-f0-9:]/', '_', $ip);
    $now     = time();
    $entries = [];

    if (file_exists($file)) {
        $entries = array_filter(
            explode("\n", trim(file_get_contents($file))),
            fn($t) => is_numeric($t) && ($now - (int)$t) < $window
        );
    }

    if (count($entries) >= $max) {
        http_response_code(429);
        header('Retry-After: ' . $window);
        header('Location: ../index.html?mail=failed');
        exit;
    }

    $entries[] = $now;
    file_put_contents($file, implode("\n", $entries), LOCK_EX);
}

check_rate_limit();

// ── CSRF check ────────────────────────────────────────────────────────────────
$submitted_token = $_POST['csrf_token'] ?? '';
$session_token   = $_SESSION['csrf_token'] ?? '';

if ($session_token === '' || !hash_equals($session_token, $submitted_token)) {
    http_response_code(403);
    header('Location: ../index.html?mail=failed');
    exit;
}
// Burn the token so it can only be used once
unset($_SESSION['csrf_token']);

// ── Helper functions ──────────────────────────────────────────────────────────
function clean_text(string $value): string {
    return trim(strip_tags($value));
}

function is_header_injection(string $value): bool {
    return preg_match('/[\r\n]/', $value) === 1;
}

// ── Read and validate form fields ─────────────────────────────────────────────
$name     = clean_text($_POST['name']    ?? '');
$email    = trim($_POST['email']         ?? '');
$message  = clean_text($_POST['message'] ?? '');
$honeypot = trim($_POST['website']       ?? '');

if ($honeypot !== '') {
    http_response_code(400);
    exit('Bad request');
}

if ($name === '' || $email === '' || $message === '') {
    header('Location: ../index.html?mail=failed');
    exit();
}

if (strlen($message) > 4000) {
    header('Location: ../index.html?mail=failed');
    exit();
}

if (
    !filter_var($email, FILTER_VALIDATE_EMAIL)
    || is_header_injection($email)
    || is_header_injection($name)
    || is_header_injection($message)
) {
    header('Location: ../index.html?mail=failed');
    exit();
}

// ── Send ──────────────────────────────────────────────────────────────────────
$to      = 'yannick@hogetoorn.com';
$subject = 'New Contact Form Message';

$body  = "Name: $name\n";
$body .= "Email: $email\n\n";
$body .= "Message:\n$message\n";

$headers = [
    'From: noreply@hogetoorn.com',
    "Reply-To: $email",
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
];

if (mail($to, $subject, $body, implode("\r\n", $headers))) {
    header('Location: ../index.html?mail=success');
    exit();
} else {
    header('Location: ../index.html?mail=failed');
    exit();
}