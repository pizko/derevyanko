<?php
/**
 * Заявки с лендинга СК Деревянко → Telegram-бот заявок.
 * Токен и chat_id лежат ВНЕ webroot: ../lead_config.php (['bot_token' => ..., 'chat_id' => ...]).
 * Копия каждой заявки пишется в ../leads.log — на случай, если Telegram недоступен.
 */
declare(strict_types=1);
session_start();
mb_internal_encoding('UTF-8');
header('Content-Type: application/json; charset=utf-8');
header('X-Robots-Tag: noindex, nofollow');

function out(int $code, array $data): void
{
    http_response_code($code);
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    out(405, ['ok' => false, 'error' => 'method']);
}

$field = static function (string $k, int $max): string {
    $v = trim((string) ($_POST[$k] ?? ''));
    $v = preg_replace('/\s+/u', ' ', $v) ?? '';
    return mb_substr(strip_tags($v), 0, $max);
};

// ловушка для ботов: скрытое поле должно остаться пустым
if ($field('website', 100) !== '') {
    out(200, ['ok' => true]);
}

$name = $field('your-name', 80);
$phone = $field('your-phone', 40);
$types = ['Квартира', 'Дом', 'Офис', 'Коммерческое помещение', 'Другое'];
$type = $field('object-type', 40);
if (!in_array($type, $types, true)) {
    $type = 'Не указан';
}
$area = preg_replace('/[^\d.,]/', '', $field('object-area', 10)) ?? '';
$page = $field('page', 500);

$digits = preg_replace('/\D/', '', $phone) ?? '';
if ($name === '' || strlen($digits) < 10 || strlen($digits) > 15) {
    out(422, ['ok' => false, 'error' => 'Укажите имя и телефон.']);
}

// капча: код из captcha.php, одноразовый, живёт 10 минут
$capIn = strtoupper(preg_replace('/\s+/', '', (string) ($_POST['captcha'] ?? '')) ?? '');
$capOk = strtoupper((string) ($_SESSION['skr_captcha'] ?? ''));
$capT = (int) ($_SESSION['skr_captcha_t'] ?? 0);
unset($_SESSION['skr_captcha'], $_SESSION['skr_captcha_t']);
if ($capOk === '' || $capIn === '' || !hash_equals($capOk, $capIn) || time() - $capT > 600) {
    out(422, ['ok' => false, 'error' => 'Неверный код с картинки — попробуйте ещё раз.', 'captcha' => true]);
}

// не чаще одной заявки в 30 секунд с одного IP
$ip = (string) ($_SERVER['REMOTE_ADDR'] ?? '');
$rlDir = dirname(__DIR__) . '/lead_rl';
if (!is_dir($rlDir)) {
    @mkdir($rlDir, 0700);
}
$rlFile = $rlDir . '/' . md5($ip);
if (is_file($rlFile) && time() - (int) @filemtime($rlFile) < 30) {
    out(429, ['ok' => false, 'error' => 'Заявка уже отправлена, подождите немного.']);
}
@touch($rlFile);

// метки Директа из адреса страницы
$utm = [];
$q = (string) parse_url($page, PHP_URL_QUERY);
parse_str($q, $params);
foreach (['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 'yclid'] as $k) {
    if (!empty($params[$k])) {
        $utm[] = $k . '=' . mb_substr((string) $params[$k], 0, 120);
    }
}

$text = "🏗 Заявка — СК Деревянко (лендинг)\n\n"
    . "Имя: {$name}\n"
    . "Телефон: {$phone}\n"
    . "Объект: {$type}\n"
    . 'Площадь: ' . ($area !== '' ? "{$area} м²" : '—') . "\n"
    . ($utm ? "\nМетки: " . implode(', ', $utm) . "\n" : '')
    . "\n" . date('d.m.Y H:i') . ' МСК';

@file_put_contents(dirname(__DIR__) . '/leads.log', date('c') . "\t" . str_replace("\n", ' | ', $text) . "\n", FILE_APPEND | LOCK_EX);

$cfg = @include dirname(__DIR__) . '/lead_config.php';
$sent = false;
if (is_array($cfg) && !empty($cfg['bot_token']) && !empty($cfg['chat_id'])) {
    $ch = curl_init("https://api.telegram.org/bot{$cfg['bot_token']}/sendMessage");
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => http_build_query(['chat_id' => $cfg['chat_id'], 'text' => $text, 'disable_web_page_preview' => 'true']),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 8,
    ]);
    $res = curl_exec($ch);
    $sent = $res !== false && (int) curl_getinfo($ch, CURLINFO_HTTP_CODE) === 200;
    curl_close($ch);
}

if (!$sent) {
    out(502, ['ok' => false, 'error' => 'send']);
}
out(200, ['ok' => true, 'message' => 'Спасибо! Перезвоним в течение рабочего дня.']);
