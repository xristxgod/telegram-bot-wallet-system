import asyncio
import random
import typing

import aiohttp
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from tronpy.async_tron import AsyncTron, AsyncHTTPProvider

from src.utils import Utils
from src.types import TAddress
from config import Config, logger

class NodeStatus:
    """ Tron node status """
    PROVIDER = AsyncHTTPProvider(Config.NODE_URL)
    PUBLIC_NODE = ["http://3.225.171.164:8090", "http://52.53.189.99:8090", "http://18.196.99.16:8090"]

    @staticmethod
    async def _get_node_info(our_node: AsyncTron) -> typing.Optional:
        if int(await our_node.get_node_info()["activeConnectCount"]) == 0:
            # If there are no active connections to the node, then the node is dead!
            raise Exception("Problems with the node. There are no active connections")

    @staticmethod
    async def _is_block_ex(our_node: AsyncTron, public_node: AsyncTron) -> typing.Optional:
        if not Utils.is_valid(
                val_one=(await our_node.get_latest_block_number()),
                val_two=(await public_node.get_latest_block_number())
        ):
            # If the blocks are moving with a large gap, then something is wrong with the node
            raise Exception("The blocks in the node are moving too slowly")

    @staticmethod
    async def _is_acc_valid(our_node: AsyncTron, address: TAddress = "TPvxLpLeC1Rd13CymBVWnXJiURjWk3SfRx"):
        if not (await our_node.get_account(address)):
            # If you call out the method through the node, then something is also wrong
            raise Exception("The node is not working correctly")

    @staticmethod
    async def get_node_status(accept: int = 0) -> bool:
        if accept > 1:
            return False
        our_node = None
        public_node = None
        try:
            our_node = AsyncTron(provider=NodeStatus.PROVIDER)
            public_node = AsyncTron(provider=AsyncHTTPProvider(NodeStatus.PUBLIC_NODE[random.randint(0, 2)]))
            await NodeStatus._get_node_info(our_node=our_node)
            await NodeStatus._is_block_ex(our_node=our_node, public_node=public_node)
            await NodeStatus._is_acc_valid(our_node=our_node)
            return True
        except Exception as error:
            logger.error(f"ERROR: {error}")
            await asyncio.sleep(2)
            await NodeStatus.get_node_status(accept=accept+1)
        finally:
            if our_node is not None:
                await our_node.close()
            if public_node is not None:
                await public_node.close()

class DemonStatus:
    """ Tron demon status """
    PROVIDER = AsyncHTTPProvider(Config.NODE_URL)
    NETWORK: str = "shasta" if Config.NETWORK == "TESTNET" else "mainnet"
    TRON_DEMON_BLOCK_URL = "/tron/demon-block"

    @staticmethod
    async def get_demon_block() -> int:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                Config.CHECKER_NODE_BLOCK + DemonStatus.TRON_DEMON_BLOCK_URL
            ) as response:
                if not response.ok:
                    logger.error(f'GET RESPONSE ERROR: {response.status}')
                    raise Exception("Block is not found")
                return int(await response.text())

    @staticmethod
    async def get_demon_status(accept: int = 0):
        if accept > 1:
            raise Exception("Demon is dead")
        try:
            async with AsyncTron(
                provider=DemonStatus.PROVIDER if DemonStatus.NETWORK == "mainnet" else None,
                network=DemonStatus.NETWORK
            ) as node:
                if Utils.is_valid(
                    val_one=node.get_latest_block_number(),
                    val_two=(await DemonStatus.get_demon_block())
                ):
                    return True
                return False
        except Exception as error:
            logger.error(f"ERROR: {error}")
            await asyncio.sleep(2)
            await DemonStatus.get_demon_status(accept=accept+1)

router = APIRouter()

# <<<======================================>>> Api status <<<========================================================>>>

@router.get("/", description="Find out the status of the API", response_class=JSONResponse, tags=["System"])
async def get_api_status():
    return JSONResponse(content={"message": True})

# <<<======================================>>> Node status <<<=======================================================>>>

@router.get("/is-node-alive", description="Find out the status of the Tron Node", response_class=JSONResponse, tags=["System"])
async def get_node_status():
    try:
        if Config.NETWORK == "MAINNET":
            return JSONResponse(content={"message": await NodeStatus.get_node_status()})
        return JSONResponse(content={"message": True})
    except Exception as error:
        return JSONResponse(content={"message": False})

# <<<======================================>>> Demon status <<<======================================================>>>

@router.get("/is-demon-alive", description="Find out the status of the Tron Demon", response_class=JSONResponse, tags=["System"])
async def get_demon_status():
    try:
        return JSONResponse(content={"message": await DemonStatus.get_demon_status()})
    except Exception as error:
        return JSONResponse(content={"message": False})