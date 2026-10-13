<?php
/**
 * Невидимая проверка формы.
 * Выдаёт одноразовый подписанный токен: время + nonce + HMAC.
 */
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('X-Robots-Tag: noindex, nofollow');

$cfgFile = dirname(__DIR__) . '/lead_config.php';
if (!is_file($cfgFile)) {
    $cfgFile = dirname(__DIR__, 2) . '/lead_config.php';
}
$cfg = is_file($cfgFile) ? (@include $cfgFile) : [];
if (!is_array($cfg)) {
    $cfg = [];
}
$key = hash('sha256', (string) ($cfg['bot_token'] ?? 'skr') . '|skr-form-key');

$ts = (string) time();
$nonce = bin2hex(random_bytes(8));
$sig = hash_hmac('sha256', $ts . '.' . $nonce, $key);

echo json_encode(['t' => $ts . '.' . $nonce . '.' . $sig], JSON_UNESCAPED_UNICODE);
