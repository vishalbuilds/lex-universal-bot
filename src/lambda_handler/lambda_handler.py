import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Lambda function to handle Lex bot interactions and route to expert when needed
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Extract Lex event details
    intent_name = event.get('sessionState', {}).get('intent', {}).get('name', '')
    slots = event.get('sessionState', {}).get('intent', {}).get('slots', {})
    session_attributes = event.get('sessionState', {}).get('sessionAttributes', {})
    
    # Check if expert response is needed
    if requires_expert_response(intent_name, slots, session_attributes):
        return route_to_expert(event)
    
    # Handle normal bot response
    return handle_bot_response(event)


def requires_expert_response(intent_name, slots, session_attributes):
    """
    Determine if the request needs to be routed to an expert
    """
    # Add your logic to determine when expert is needed
    expert_flag = session_attributes.get('needsExpert', 'false')
    complex_query = session_attributes.get('complexQuery', 'false')
    
    return expert_flag == 'true' or complex_query == 'true'


def route_to_expert(event):
    """
    Route the conversation to an expert and return appropriate Lex response
    """
    import time
    session_attributes = event.get('sessionState', {}).get('sessionAttributes', {})
    session_attributes['routedToExpert'] = 'true'
    session_attributes['expertRequestTime'] = str(int(time.time()))
    
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'Close'
            },
            'intent': {
                'name': event['sessionState']['intent']['name'],
                'state': 'Fulfilled'
            },
            'sessionAttributes': session_attributes
        },
        'messages': [
            {
                'contentType': 'PlainText',
                'content': 'I understand you need specialized assistance. Let me connect you with an expert who can help you better.'
            }
        ]
    }


def handle_bot_response(event):
    """
    Handle standard bot responses
    """
    intent_name = event['sessionState']['intent']['name']
    
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'Close'
            },
            'intent': {
                'name': intent_name,
                'state': 'Fulfilled'
            }
        },
        'messages': [
            {
                'contentType': 'PlainText',
                'content': 'I can help you with that request.'
            }
        ]
    }



def elicit_slot_response(event, slot_to_elicit, message):
    """
    Return Lex response to elicit a specific slot
    """
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'ElicitSlot',
                'slotToElicit': slot_to_elicit
            },
            'intent': {
                'name': event['sessionState']['intent']['name'],
                'slots': event['sessionState']['intent']['slots'],
                'state': 'InProgress'
            }
        },
        'messages': [
            {
                'contentType': 'PlainText',
                'content': message
            }
        ]
    }


def delegate_response(event):
    """
    Delegate back to Lex to continue the conversation
    """
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'Delegate'
            },
            'intent': event['sessionState']['intent']
        }
    }


def confirm_intent_response(event, message):
    """
    Ask user to confirm the intent
    """
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'ConfirmIntent'
            },
            'intent': {
                'name': event['sessionState']['intent']['name'],
                'slots': event['sessionState']['intent']['slots'],
                'state': 'InProgress'
            }
        },
        'messages': [
            {
                'contentType': 'PlainText',
                'content': message
            }
        ]
    }


def close_with_fulfillment(event, message, session_attributes=None):
    """
    Close the conversation with fulfillment
    """
    if session_attributes is None:
        session_attributes = event.get('sessionState', {}).get('sessionAttributes', {})
    
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'Close'
            },
            'intent': {
                'name': event['sessionState']['intent']['name'],
                'slots': event['sessionState']['intent']['slots'],
                'state': 'Fulfilled'
            },
            'sessionAttributes': session_attributes
        },
        'messages': [
            {
                'contentType': 'PlainText',
                'content': message
            }
        ]
    }
