"""
Custom exception handler pour uniformiser les réponses d'erreur de l'API.

Format uniforme :
{
    "message": "Message d'erreur principal",
    "errors": {"field": "erreur"} ou null,
    "code": "error_code"
}
"""

from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Uniformise le format des erreurs API"""
    response = exception_handler(exc, context)

    if response is None:
        return None

    error_data = response.data
    custom_response = {
        'message': None,
        'errors': None,
        'code': getattr(exc, 'default_code', 'error')
    }

    # Erreur avec "detail" (401, 403, 404, etc.)
    if isinstance(error_data, dict) and 'detail' in error_data:
        custom_response['message'] = str(error_data['detail'])

    # Erreur de validation avec champs (400)
    elif isinstance(error_data, dict):
        errors = {}
        for field, messages in error_data.items():
            if isinstance(messages, list):
                errors[field] = str(messages[0]) if messages else "Erreur de validation"
            else:
                errors[field] = str(messages)

        custom_response['message'] = "Les données sont invalides"
        custom_response['errors'] = errors
        custom_response['code'] = 'validation_error'

    # Autres cas
    else:
        custom_response['message'] = str(error_data)

    response.data = custom_response
    return response
