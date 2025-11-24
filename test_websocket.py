#!/usr/bin/env python3
"""
Simple WebSocket test script to test stop_auto_attendance functionality
"""
import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket():
    uri = "ws://127.0.0.1:8001/api/ws/lesson/1?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc2NDA0OTUxOX0.CEiY38ulus2-vxXFHxUkBgjgr-S-7QlwfiiUKGLkMj8"

    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connected to WebSocket")

            # Wait for initial message
            response = await websocket.recv()
            logger.info(f"Received: {response}")

            # Send start_attendance command
            start_message = {"type": "start_attendance"}
            await websocket.send(json.dumps(start_message))
            logger.info(f"Sent: {start_message}")

            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                logger.info(f"Received start response: {response}")
            except asyncio.TimeoutError:
                logger.warning("No start response received")

            # Wait a moment for attendance to start
            await asyncio.sleep(2)

            # Send stop_auto_attendance command
            stop_message = {"type": "stop_auto_attendance"}
            await websocket.send(json.dumps(stop_message))
            logger.info(f"Sent: {stop_message}")

            # Wait for multiple responses (stop confirmation might come after count updates)
            responses_received = 0
            while responses_received < 3:  # Wait for up to 3 responses
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    logger.info(f"Received response {responses_received + 1}: {response}")
                    responses_received += 1
                    
                    # Check if we got the stop confirmation
                    response_data = json.loads(response)
                    if response_data.get("type") == "auto_attendance_stopped":
                        logger.info("✅ Successfully received auto_attendance_stopped confirmation!")
                        break
                        
                except asyncio.TimeoutError:
                    logger.warning("No more responses received")
                    break

    except Exception as e:
        logger.error(f"WebSocket test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
