<?php

define('OMNI_ACCESS_TOKEN', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwaG9uZU51bWJlciI6Iis5MTk1NjYwNTA4MTAiLCJwaG9uZU51bWJlcklkIjoiNzQ0MjM5ODM1NDMxNDc1IiwiaWF0IjoxNzUxNjMyODg1fQ.NGkpXjg0rt2r7PfamBdhXykN4lAI0RTLrGy5qz1BhEs');

define('OMNI_WHATSAPP_NUMBER', '+919566050810');
define('OMNI_API_BASE', 'https://wb.omni.tatatelebusiness.com/Messages');

define('TICKETING_API_BASE', 'https://nexus.imayahtech.com/api/ticketing.php');

// ─── SYSTEM INTEGRATIONS ──────────────────────────────────────────────────────
define('CAREER_PORTAL_WEBHOOK_URL', 'https://stagecareer.themadrassevasadan.org/school/offers/update-by-webhook');
define('CAREER_PORTAL_SECRET_TOKEN', 'admin@123'); // Match your FastAPI configurations

// ─── DEBUG HELPER ─────────────────────────────────────────────────────────────
function debugLog(string $checkpoint, $data = null): void
{
    $line = '[' . date('Y-m-d H:i:s') . '] CHECKPOINT: ' . $checkpoint;
    if ($data !== null) {
        $line .= ' | DATA: ' . print_r($data, true);
    }
    file_put_contents(__DIR__ . '/debug.log', $line . PHP_EOL, FILE_APPEND | LOCK_EX);
}

// ─── ENTRY POINT ─────────────────────────────────────────────────────────────

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    exit('Method Not Allowed');
}

$input = file_get_contents('php://input');
$data  = json_decode($input, true);

debugLog('Raw input', $input);

// Always respond 200 immediately so Omni doesn't retry
http_response_code(200);
echo 'OK';

if (function_exists('fastcgi_finish_request')) {
    fastcgi_finish_request();
} else {
    ob_flush();
    flush();
}

if (!isset($data['messages'])) {
    if (isset($data['statuses'])) {
        $status = $data['statuses'][0] ?? $data['statuses'];
        debugLog('status update received', $status);
    }
    debugLog('EXIT - no messages field found (likely a status update or malformed payload)', $data);
    exit;
}

$message = $data['messages']; // NOTE: object, not array — no [0] index
$from    = $message['from'] ?? null;

$contact     = $data['contacts'][0] ?? null;
$profileName = $contact['profile']['name'] ?? null;
$waId        = $contact['wa_id'] ?? $from;

$messageId   = $message['id'] ?? null;
$timestamp   = $message['timestamp'] ?? null;
$messageType = $message['type'] ?? null;

$messageBody = null;
switch ($messageType) {
    case 'text':
        $messageBody = $message['text']['body'] ?? null;
        break;
    case 'button':
        // Capture the structural background tracking payload string value if present, else fallback to button text
        $messageBody = $message['button']['payload'] ?? ($message['button']['text'] ?? null);
        break;
    case 'interactive':
        $messageBody = $message['interactive']['button_reply']['id']
            ?? $message['interactive']['button_reply']['title']
            ?? $message['interactive']['list_reply']['id']
            ?? null;
        break;
    case 'image':
    case 'video':
    case 'document':
    case 'audio':
        $messageBody = $message[$messageType]['caption'] ?? ('[' . $messageType . ' received]');
        break;
    default:
        $messageBody = '[unsupported message type: ' . $messageType . ']';
}

// ── Fetch existing user details from the ticketing system, by mobile number ──
$ticketingUser = fetchUserDetailsFromTicketing($from);

$userDetails = [
    'wa_id'          => $waId,
    'phone'          => $from,
    'name'           => $profileName,
    'message_id'     => $messageId,
    'message_type'   => $messageType,
    'message_body'   => $messageBody,
    'timestamp'      => $timestamp,
    'received_at'    => date('Y-m-d H:i:s'),
    'ticketing_user' => $ticketingUser, // null if not found / lookup failed
];

debugLog('userDetails bundled', $userDetails);

saveUserDetails($userDetails);

// ─── FORWARD AUTOMATED APPLICANT RESPONSE TO CAREER PORTAL ───────────────────
if (($messageType === 'button' || $messageType === 'interactive') && !empty($messageBody)) {
    $rawPayload = strtoupper(trim($messageBody));
    $mappedStatus = null;

    if ($rawPayload === 'ACCEPTED') {
        $mappedStatus = 'accepted';
    } elseif ($rawPayload === 'REJECTED') {
        $mappedStatus = 'rejected';
    }

    if ($mappedStatus !== null) {
        debugLog("Valid template button trigger hit. Handoff to career portal pipeline initiated.", [
            'phone'  => $from,
            'status' => $mappedStatus
        ]);
        forwardStatusToCareerPortal($from, $mappedStatus);
    }
}

if ($messageType === 'text') {
    $text = strtolower(trim($messageBody ?? ''));
    // Process optional text commands down here if needed
}

exit;

// ─── FUNCTIONS ────────────────────────────────────────────────────────────────

/**
 * Sends a secure validation PATCH request carrying selection responses straight
 * to the centralized career application management portal.
 */
function forwardStatusToCareerPortal(string $phone, string $status): void
{
    $payload = [
        'phone'  => $phone,
        'status' => $status
    ];

    $ch = curl_init(CAREER_PORTAL_WEBHOOK_URL);
    curl_setopt_array($ch, [
        CURLOPT_CUSTOMREQUEST  => 'PATCH',
        CURLOPT_POSTFIELDS     => json_encode($payload),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => 15,
        CURLOPT_HTTPHEADER     => [
            'Content-Type: application/json',
            'X-Webhook-Token: ' . CAREER_PORTAL_SECRET_TOKEN,
            'Accept: application/json'
        ],
    ]);

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $error    = curl_error($ch);
    curl_close($ch);

    debugLog('Career Portal Update Response', [
        'http_code' => $httpCode,
        'response'  => $response,
        'curl_err'  => $error
    ]);

    if ($error || $httpCode >= 400) {
        logError("Failed sending status updates to portal for phone: $phone. HTTP $httpCode. Error: $error");
    }
}

/**
 * Calls the ticketing API's GET endpoint with the mobile number to fetch
 * the most recent user details (name, email, company, unit_name) on file
 * in the ticketing_data table.
 */
function fetchUserDetailsFromTicketing(?string $mobile): ?array
{
    if (!$mobile) {
        return null;
    }

    $url = TICKETING_API_BASE . '?mobile=' . urlencode($mobile);

    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => 10,
        CURLOPT_HTTPHEADER     => [
            'Accept: application/json',
        ],
    ]);

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $error    = curl_error($ch);
    curl_close($ch);

    debugLog('fetchUserDetailsFromTicketing response', [
        'mobile'    => $mobile,
        'http_code' => $httpCode,
        'response'  => $response,
        'curl_err'  => $error,
    ]);

    if ($error) {
        logError("Ticketing API lookup failed for {$mobile} | cURL error: {$error}");
        return null;
    }

    $decoded = json_decode($response, true);

    if ($httpCode === 200 && !empty($decoded['success']) && isset($decoded['user'])) {
        return $decoded['user'];
    }

    if ($httpCode === 404) {
        debugLog('No ticketing record found for this mobile', $mobile);
        return null;
    }

    logError("Ticketing API unexpected response for {$mobile} | HTTP {$httpCode} | Body: {$response}");
    return null;
}

function sendOmniReply(string $to, string $text): void
{
    $url = OMNI_API_BASE . '/messages';

    $payload = [
        'to'                  => $to,
        'type'                => 'text',
        'text'                => ['body' => $text],
        'from'                => OMNI_WHATSAPP_NUMBER,
    ];

    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_POST           => true,
        CURLOPT_POSTFIELDS     => json_encode($payload),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => 10,
        CURLOPT_HTTPHEADER     => [
            'Authorization: Bearer ' . OMNI_ACCESS_TOKEN,
            'Content-Type: application/json',
            'Accept: application/json',
        ],
    ]);

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $error    = curl_error($ch);
    curl_close($ch);

    if ($error || $httpCode >= 400) {
        logError("sendOmniReply to $to failed | HTTP $httpCode | cURL: $error | Response: $response");
    }
}

/**
 * Saves full user + message details into user_details.json as a proper
 * JSON array — reads existing array, appends the new record, and rewrites
 * the file.
 */
function saveUserDetails(array $details): void
{
    $file = __DIR__ . '/user_details.json';

    $existing = [];
    if (file_exists($file)) {
        $raw = file_get_contents($file);
        $decoded = json_decode($raw, true);
        if (is_array($decoded)) {
            $existing = $decoded;
        }
    }

    $existing[] = $details;

    file_put_contents(
        $file,
        json_encode($existing, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE),
        LOCK_EX
    );
}

function logError(string $message): void
{
    file_put_contents(
        __DIR__ . '/omni_errors.log',
        date('c') . ' | ' . $message . PHP_EOL,
        FILE_APPEND | LOCK_EX
    );
}