<?php
/**
 * Заявки с лендинга СК-Ремонт (ск-ремонт.рф) → Telegram-бот заявок.
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
$src = $field('src', 40);
$interest = $field('interest', 60);

$digits = preg_replace('/\D/', '', $phone) ?? '';
if ($name === '' || strlen($digits) < 10 || strlen($digits) > 15) {
    out(422, ['ok' => false, 'error' => 'Укажите имя и телефон.']);
}

// невидимая проверка: одноразовый подписанный токен из token.php.
// Человек тратит на форму хотя бы пару секунд — мгновенная отправка отсекается.
$cfgKey = @include dirname(__DIR__) . '/lead_config.php';
$key = hash('sha256', (string) ($cfgKey['bot_token'] ?? 'skr') . '|skr-form-key');
$bad = static function () {
    out(422, ['ok' => false, 'error' => 'Форма устарела — обновите страницу и отправьте ещё раз.', 'token' => true]);
};
$parts = explode('.', (string) ($_POST['t'] ?? ''));
if (count($parts) !== 3) {
    $bad();
}
[$tkTime, $tkNonce, $tkSig] = $parts;
if (!ctype_digit($tkTime) || !ctype_xdigit($tkNonce) || !hash_equals(hash_hmac('sha256', $tkTime . '.' . $tkNonce, $key), $tkSig)) {
    $bad();
}
$age = time() - (int) $tkTime;
if ($age < 2 || $age > 7200) {
    $bad();
}
// одноразовость: метку нельзя переиспользовать
$nonceDir = dirname(__DIR__) . '/lead_nonce';
if (!is_dir($nonceDir)) {
    @mkdir($nonceDir, 0700);
}
$nonceFile = $nonceDir . '/' . $tkNonce;
if (is_file($nonceFile)) {
    $bad();
}
@touch($nonceFile);
if (random_int(1, 50) === 1) {   // изредка подчищаем старые метки
    foreach ((array) @glob($nonceDir . '/*') as $old) {
        if (is_string($old) && time() - (int) @filemtime($old) > 7200) {
            @unlink($old);
        }
    }
}

// код с картинки: одноразовый, живёт 10 минут
$capIn = strtoupper(preg_replace('/\s+/', '', (string) ($_POST['captcha'] ?? '')) ?? '');
$caps = (array) ($_SESSION['skr_caps'] ?? []);
unset($_SESSION['skr_caps']);   // коды одноразовые: после попытки все сгорают
$capMatch = false;
foreach ($caps as $c) {
    if (is_array($c) && $capIn !== '' && hash_equals(strtoupper((string) $c['c']), $capIn) && time() - (int) $c['t'] <= 600) {
        $capMatch = true;
        break;
    }
}
if (!$capMatch) {
    out(422, ['ok' => false, 'error' => 'Неверный код с картинки — попробуйте ещё раз.', 'captcha' => true]);
}

// не чаще одной заявки в 30 секунд с одного IP
$ip = (string) ($_SERVER['REMOTE_ADDR'] ?? '');
$rlDir = dirname(__DIR__) . '/lead_rl';
if (!is_dir($rlDir)) {
    @mkdir($rlDir, 0700);
}
$rlFile = $rlDir . '/' . md5($ip);
if (is_file($rlFile) && time() - (int) @filemtime($rlFile) < 90) {
    // заявка с этого адреса только что пришла: не дублируем её в Telegram,
    // но и ошибку не показываем — человек уже всё сделал правильно
    out(200, ['ok' => true, 'duplicate' => true, 'message' => 'Заявка уже у нас — перезвоним в течение рабочего дня.']);
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

$text = "🏗 Заявка — СК-Ремонт (ск-ремонт.рф)\n\n"
    . "Имя: {$name}\n"
    . "Телефон: {$phone}\n"
    . "Объект: {$type}\n"
    . 'Площадь: ' . ($area !== '' ? "{$area} м²" : '—') . "\n"
    . ($interest !== '' ? "Интерес: {$interest}\n" : '')
    . ($src !== '' ? "Форма: {$src}\n" : '')
    . ($utm ? "\nМетки: " . implode(', ', $utm) . "\n" : '')
    . "\n" . date('d.m.Y H:i') . ' МСК';

@file_put_contents(dirname(__DIR__) . '/leads.log', date('c') . "\t" . str_replace("\n", ' | ', $text) . "\n", FILE_APPEND | LOCK_EX);

$cfg = @include dirname(__DIR__) . '/lead_config.php';
$sent = false;
if (is_array($cfg) && !empty($cfg['bot_token']) && !empty($cfg['chat_id'])) {
    $ch = // с Beget api.telegram.org недоступен (27.10.2026) — шлём через пересылку на нашем VPS
    $ch = curl_init("https://deltamoscow.ru/tg-relay/bot{$cfg['bot_token']}/sendMessage");
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
