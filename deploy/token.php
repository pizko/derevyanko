<?php
/**
 * Невидимая проверка формы вместо картинки с кодом.
 * Выдаёт одноразовый подписанный токен: время выпуска + случайная метка + HMAC.
 * send.php проверяет подпись, возраст токена и то, что метка ещё не использовалась.
 * Ключ подписи выводится из токена бота (лежит вне webroot) — отдельный секрет не нужен.
 */
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('X-Robots-Tag: noindex, nofollow');

$cfg = @include dirname(__DIR__) . '/lead_config.php';
$key = hash('sha256', (string) ($cfg['bot_token'] ?? 'skr') . '|skr-form-key');

$ts = time();
$nonce = bin2hex(random_bytes(8));
$sig = hash_hmac('sha256', $ts . '.' . $nonce, $key);

echo json_encode(['t' => $ts . '.' . $nonce . '.' . $sig]);
