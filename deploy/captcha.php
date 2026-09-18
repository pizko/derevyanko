<?php
/** Капча формы лендинга: SVG-картинка, код в сессии (проверяет send.php). */
declare(strict_types=1);
session_start();
$chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ';
$code = '';
for ($i = 0; $i < 5; $i++) {
    $code .= $chars[random_int(0, strlen($chars) - 1)];
}
$_SESSION['skr_captcha'] = $code;
$_SESSION['skr_captcha_t'] = time();

header('Content-Type: image/svg+xml; charset=UTF-8');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('X-Robots-Tag: noindex, nofollow');

$noise = '';
for ($i = 0; $i < 7; $i++) {
    $noise .= sprintf('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="rgba(167,15,39,.55)" stroke-width="1.4"/>',
        random_int(0, 160), random_int(0, 52), random_int(0, 160), random_int(0, 52));
}
$letters = '';
$x = 14;
foreach (str_split($code) as $ch) {
    $y = random_int(32, 40);
    $letters .= sprintf('<text x="%d" y="%d" transform="rotate(%d %d %d)" font-family="Arial,sans-serif" font-size="26" font-weight="700" fill="#EDEAE4">%s</text>',
        $x, $y, random_int(-14, 14), $x, $y, $ch);
    $x += 28;
}
echo '<svg xmlns="http://www.w3.org/2000/svg" width="160" height="52" viewBox="0 0 160 52">'
   . '<rect width="160" height="52" fill="#14161A"/>' . $noise . $letters . '</svg>';
