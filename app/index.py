from fastapi import APIRouter, Request, Response, BackgroundTasks
import json
import os
import requests
from datetime import datetime
import logging
from app.core.config import settings

router = APIRouter()

logger = logging.getLogger(__name__)

# ─── OMNI / WHATSAPP CONFIG ───────────────────────────────────────────────────
OMNI_ACCESS_TOKEN = settings.OMNI_PORTAL_API_KEY
OMNI_WHATSAPP_NUMBER = settings.OMNI_WHATSAPP_NUMBER
OMNI_API_BASE = 'https://wb.omni.tatatelebusiness.com/Messages'

# ─── CAREER PORTAL CONFIG ─────────────────────────────────────────────────────
CAREER_PORTAL_WEBHOOK_URL = 'https://stagecareer.themadrassevasadan.org/school/offers/update-by-webhook'
CAREER_PORTAL_SECRET_TOKEN = 'admin@123'

# ─── STORAGE PATHS ────────────────────────────────────────────────────────────
USER_DETAILS_FILE = os.path.join(os.path.dirname(__file__), 'user_details.json')

# ─── UTILITY FUNCTIONS ────────────────────────────────────────────────────────
def debugLog(msg, data=None):
    logger.debug(f"{msg}: {data}")

def logError(msg):
    logger.error(msg)

def fetchUserDetailsFromTicketing(phone):
    # TODO: Implement actual lookup from ticketing system
    return None

def extractMessageBody(messageType, message):
    if messageType == 'text':
        return message.get('text', {}).get('body')
    elif messageType == 'button':
        button = message.get('button', {})
        return button.get('payload') or button.get('text')
    elif messageType == 'interactive':
        interactive = message.get('interactive', {})
        reply = interactive.get('button_reply') or interactive.get('list_reply') or {}
        return reply.get('id') or reply.get('title')
    elif messageType in ('image', 'video', 'document', 'audio'):
        return message.get(messageType, {}).get('caption') or f"[{messageType} received]"
    else:
        return f"[unsupported message type: {messageType}]"

def forwardStatusToCareerPortal(phone, status):
    payload = {
        'phone': phone,
        'status': status
    }
    headers = {
        'Content-Type': 'application/json',
        'X-Webhook-Token': CAREER_PORTAL_SECRET_TOKEN,
        'Accept': 'application/json'
    }
    try:
        response = requests.patch(CAREER_PORTAL_WEBHOOK_URL, json=payload, headers=headers, timeout=15)
        debugLog('Career Portal Update Response', {
            'http_code': response.status_code,
            'response': response.text,
        })
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logError(f"Failed sending status updates to portal for phone: {phone}. Error: {e}")

def sendOmniReply(to, text):
    url = f"{OMNI_API_BASE}/messages"
    payload = {
        'to': to,
        'type': 'text',
        'text': {'body': text},
        'from': OMNI_WHATSAPP_NUMBER,
    }
    logger.debug(f"Sending Omni reply payload: {payload}")
    headers = {
        'Authorization': f'Bearer {OMNI_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    logger.info(f"Access Token: {OMNI_ACCESS_TOKEN}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logError(f"sendOmniReply to {to} failed | Error: {e}")

def saveUserDetails(details):
    existing = []
    if os.path.exists(USER_DETAILS_FILE):
        try:
            with open(USER_DETAILS_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                if content:
                    existing = json.loads(content)
        except Exception as e:
            logError(f"Error reading {USER_DETAILS_FILE}: {e}")
            
    if not isinstance(existing, list):
        existing = []
        
    existing.append(details)
    
    try:
        with open(USER_DETAILS_FILE, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logError(f"Error writing {USER_DETAILS_FILE}: {e}")

# ─── WEBHOOK PROCESSING ───────────────────────────────────────────────────────
def process_webhook(data: dict):
    if 'messages' not in data:
        if 'statuses' in data:
            status = data['statuses'][0] if isinstance(data['statuses'], list) else data['statuses']
            debugLog('status update received', status)
        debugLog('EXIT - no messages field found (likely a status update or malformed payload)', data)
        return

    # In PHP, message was parsed as an object (not list). In Omni WhatsApp API it might be a single object or list
    message = data['messages']
    if isinstance(message, list):
        message = message[0]

    from_phone = message.get('from')
    contacts = data.get('contacts', [])
    contact = contacts[0] if contacts else {}
    
    profileName = contact.get('profile', {}).get('name')
    waId = contact.get('wa_id') or from_phone
    
    messageId = message.get('id')
    timestamp = message.get('timestamp')
    messageType = message.get('type')
    
    messageBody = extractMessageBody(messageType, message)
    
    ticketingUser = fetchUserDetailsFromTicketing(from_phone)
    
    userDetails = {
        'wa_id': waId,
        'phone': from_phone,
        'name': profileName,
        'message_id': messageId,
        'message_type': messageType,
        'message_body': messageBody,
        'timestamp': timestamp,
        'received_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'ticketing_user': ticketingUser,
    }
    
    debugLog('userDetails bundled', userDetails)
    saveUserDetails(userDetails)
    
    if messageType in ('button', 'interactive') and messageBody:
        rawPayload = str(messageBody).strip().upper()
        mappedStatus = None
        
        if 'ACCEPT' in rawPayload:
            mappedStatus = 'accepted'
        elif 'REJECT' in rawPayload:
            mappedStatus = 'rejected'
            
        if mappedStatus:
            debugLog("Valid template button trigger hit. Handoff to career portal pipeline initiated.", {
                'phone': from_phone,
                'status': mappedStatus
            })
            forwardStatusToCareerPortal(from_phone, mappedStatus)
            
    if messageType == 'text':
        text = str(messageBody).strip().lower()

# ─── ENTRY POINT ──────────────────────────────────────────────────────────────
@router.post("/webhook")
async def webhook_endpoint(request: Request, background_tasks: BackgroundTasks):
    """
    Webhook endpoint to receive Omni / WhatsApp messages.
    Returns 200 OK immediately and processes the message in the background.
    """
    try:
        body = await request.body()
        data = json.loads(body)
        debugLog('Raw input', body.decode('utf-8'))
        
        # Fast response (similar to PHP's fastcgi_finish_request)
        background_tasks.add_task(process_webhook, data)
        
        return Response(content="OK", status_code=200)
    except json.JSONDecodeError:
        return Response(content="Invalid JSON", status_code=400)