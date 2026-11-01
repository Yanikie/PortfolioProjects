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

function load_env(string $path): void {
    if (!file_exists($path)) {
        http_response_code(500);
        fail('Server configuration missing.');
    }

    foreach (file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) as $line) {
        $line = trim($line);
        if ($line === '' || str_starts_with($line, '#')) {
            continue;
        }

        [$key, $val] = explode('=', $line, 2);
        $_ENV[trim($key)] = trim($val);
    }
}

load_env(dirname(__DIR__) . '/.env');

// ── Only accept POST from here on ─────────────────────────────────────────────
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    exit('Method Not Allowed');
}

function wants_json(): bool {
    $accept = $_SERVER['HTTP_ACCEPT'] ?? '';
    $xhr = $_SERVER['HTTP_X_REQUESTED_WITH'] ?? '';
    return stripos($accept, 'application/json') !== false
        || strcasecmp($xhr, 'XMLHttpRequest') === 0;
}

function respond_json(array $data, int $status = 200): void {
    header('Content-Type: application/json; charset=utf-8');
    http_response_code($status);
    echo json_encode($data);
    exit;
}

function fail(string $message, int $status = 400): void {
    if (wants_json()) {
        respond_json(['success' => false, 'error' => $message], $status);
    }
    header('Location: ../index.html?mail=failed');
    exit;
}

function success(string $message = 'Email sent'): void {
    if (wants_json()) {
        respond_json(['success' => true, 'message' => $message], 200);
    }
    header('Location: ../index.html?mail=success');
    exit;
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
        header('Retry-After: ' . $window);
        fail('Rate limit exceeded. Please try again later.', 429);
    }

    $entries[] = $now;
    file_put_contents($file, implode("\n", $entries), LOCK_EX);
}

check_rate_limit();

// ── CSRF check ────────────────────────────────────────────────────────────────
$submitted_token = $_POST['csrf_token'] ?? '';
$session_token   = $_SESSION['csrf_token'] ?? '';

if ($session_token === '' || !hash_equals($session_token, $submitted_token)) {
    fail('CSRF token missing or invalid.', 403);
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
    fail('Bad request.');
}

if ($name === '' || $email === '' || $message === '') {
    fail('Please complete all required fields.');
}

if (strlen($message) > 4000) {
    fail('Message is too long.');
}

if (
    !filter_var($email, FILTER_VALIDATE_EMAIL)
    || is_header_injection($email)
    || is_header_injection($name)
    || is_header_injection($message)
) {
    fail('Invalid form input.');
}

// ── Send ──────────────────────────────────────────────────────────────────────
require_once __DIR__ . '/PHPMailer/src/Exception.php';
require_once __DIR__ . '/PHPMailer/src/PHPMailer.php';
require_once __DIR__ . '/PHPMailer/src/SMTP.php';

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

$to      = 'yannick@hogetoorn.com';
$subject = 'New Contact Form Message';

$body  = "Name: $name\n";
$body .= "Email: $email\n\n";
$body .= "Message:\n$message\n";

$mail = new PHPMailer(true);

try {
    $smtpUsername = $_ENV['SMTP_USERNAME'] ?? '';
    $smtpPassword = $_ENV['SMTP_PASSWORD'] ?? '';

    if ($smtpUsername === '' || $smtpPassword === '') {
        fail('SMTP credentials are not configured. Please set SMTP_USERNAME and SMTP_PASSWORD in .env.', 500);
    }

    $mail->isSMTP();
    $mail->Host       = 'mail.mijndomein.nl';
    $mail->SMTPAuth   = true;
    $mail->Username   = $smtpUsername;
    $mail->Password   = $smtpPassword;
    $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
    $mail->Port       = 587;

    $mail->setFrom('yannick@hogetoorn.com', 'Hogetoorn Website');
    $mail->addAddress($to, 'Yannick Hogetoorn');
    $mail->addReplyTo($email, $name);

    $mail->Subject = $subject;
    $mail->Body    = $body;
    $mail->AltBody = $body;
    $mail->CharSet = 'UTF-8';

    $mail->send();
    success('Message sent successfully.');
} catch (Exception $e) {
    fail('Mail delivery failed. ' . $mail->ErrorInfo);
}