import aiohttp
import functools
import asyncio  
from sanic.log import logger

async def get(url, json):
    async with aiohttp.ClientSession(headers={"Connection": "close"}) as session:
        try:    
            async with session.get(url, json=json) as resp:
                return await resp.json()
        except Exception as e:
            logger.error(e)
            logger.info('RETRYING')
            await get(url, json)

