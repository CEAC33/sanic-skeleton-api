# External dependencies
from sanic.response import text, json
from sanic import Blueprint
from sanic.log import logger
from sanic_openapi import doc
from sanic_jwt.decorators import protected

import logging
logging.basicConfig(filename='logs.txt',level=logging.WARNING)

blueprint = Blueprint('app_name')

# ENDPOINTS

@doc.summary("This is the description shown in Swagger")
@doc.produces("This is a test text")
@blueprint.get('/')
async def root_endpoint(request):
    logger.info('GET to ROOT')
    return text("This is a test text")

@doc.summary("This is the description shown in Swagger")
@doc.produces("This is a test text")
@blueprint.get('/protected')
@protected()
async def protected_endpoint(request):
    logger.info('GET to ROOT')
    return text("This is a test text protected by JWT Token")

