<?php
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    exit('Method Not Allowed');
}

function clean_text(string $value): string {
    return trim(strip_tags($value));
}

function is_header_injection(string $value): bool {
    return preg_match('/[\r\n]/', $value) === 1;
}

$name = clean_text($_POST['name'] ?? '');
$email = trim($_POST['email'] ?? '');
$message = clean_text($_POST['message'] ?? '');
$honeypot = trim($_POST['website'] ?? '');

if ($honeypot !== '') {
    http_response_code(400);
    exit('Bad request');
}

if ($name === '' || $email === '' || $message === '') {
    header('Location: ../index.html?mail=failed');
    exit();
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL) || is_header_injection($email) || is_header_injection($name) || is_header_injection($message)) {
    header('Location: ../index.html?mail=failed');
    exit();
}

$to = 'yannick@hogetoorn.com';
$subject = 'New Contact Form Message';

$body = "Name: $name\n";
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

?>