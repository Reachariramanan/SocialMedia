import socket
import asyncio
from core.config.settings import settings
from core.utils.common import setup_logging

logger = setup_logging("TorControl")

async def renew_tor_identity():
    """Signal Tor to get a new identity (IP address)."""
    try:
        # Use a simple socket connection to send the NEWNYM signal to Tor control port
        reader, writer = await asyncio.open_connection('localhost', settings.TOR_CONTROL_PORT)
        
        # Authenticate (assuming default empty password or matching the one in docker-compose)
        writer.write(b'AUTHENTICATE "mypassword"\r\n')
        await writer.drain()
        
        response = await reader.read(1024)
        if b'250 OK' not in response:
            logger.error(f"Tor authentication failed: {response.decode().strip()}")
            return False
            
        # Send NEWNYM signal
        writer.write(b'SIGNAL NEWNYM\r\n')
        await writer.drain()
        
        response = await reader.read(1024)
        if b'250 OK' in response:
            logger.info("Successfully requested new Tor identity.")
            return True
        else:
            logger.error(f"Failed to request new Tor identity: {response.decode().strip()}")
            return False
            
    except Exception as e:
        logger.error(f"Error communicating with Tor control port: {e}")
        return False
    finally:
        if 'writer' in locals():
            writer.close()
            await writer.wait_closed()
