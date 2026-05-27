<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {

    $name = htmlspecialchars($_POST["name"]);
    $email = htmlspecialchars($_POST["email"]);
    $message = htmlspecialchars($_POST["message"]);

    $to = "yannick@hogetoorn.com";
    $subject = "New Contact Form Message";

    $body = "Name: $name\n";
    $body .= "Email: $email\n\n";
    $body .= "Message:\n$message";

    $headers = "From: $email";

    if (mail($to, $subject, $body, $headers)) {
        header("Location: ../index.html?mail=success");
        exit();
    } else {
        header("Location: ../index.html?mail=failed");
        exit();
    }
}

?>