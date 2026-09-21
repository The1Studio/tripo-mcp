"""
MIT License

Copyright (c) 2025 Siddharth Ahuja
Copyright (c) 2025 for additions

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This file is based on work by Siddharth Ahuja, with additional contributions
for Tripo MCP functionality.
"""

from mcp.server.fastmcp import FastMCP
import sys
from pathlib import Path
import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TripoMCPServer")

sys.path.insert(0, str(Path(__file__).parent.parent))

from tripo3d import TripoClient, TaskStatus


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle.

    This server owns no external runtime: it talks only to the Tripo HTTP API, so
    there is nothing to connect to at startup. The lifespan hook is kept so the
    server keeps a standard lifecycle and has a place for future setup.
    """
    logger.info("Tripo MCP server starting up")
    try:
        yield {}
    finally:
        logger.info("Tripo MCP server shut down")


mcp = FastMCP(
    name="Tripo MCP",
    instructions=(
        "MCP server for Tripo 3D model generation. Creates 3D models from text or "
        "images and reports task status; the generated GLB is imported downstream by "
        "the Blender MCP server (blender-mcp)."
    ),
    lifespan=server_lifespan,
)


def _get_tripo_api_key() -> str:
    """Return the Tripo API key from the TRIPO_API_KEY environment variable.

    Raises:
        ValueError: if TRIPO_API_KEY is unset or empty. There is deliberately no
            fallback source: a missing key must fail loudly rather than be
            silently substituted.
    """
    api_key = os.environ.get("TRIPO_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "TRIPO_API_KEY is not set. Export it in the environment of the MCP server "
            "(for example TRIPO_API_KEY=tsk_xxx), then restart the server."
        )
    return api_key


@mcp.tool()
async def create_3d_model_from_text(
    describe_the_look_of_object: str, face_limit: int = -1
) -> Dict[str, Any]:
    """
    Create a 3D model from a text description using the Tripo API.

    IMPORTANT: This tool initiates a 3D model generation task but does NOT wait for completion.
    After calling this tool, you MUST repeatedly call the get_task_status tool with the returned
    task_id until the task status is SUCCESS or a terminal error state.

    Typical workflow:
    1. Call create_3d_model_from_text to start the task
    2. Get the task_id from the response
    3. Call get_task_status with the task_id
    4. If status is not SUCCESS, wait a moment and call get_task_status again
    5. Repeat until status is SUCCESS or a terminal error state
    6. When status is SUCCESS, use the pbr_model_url from the response

    Args:
        describe_the_look_of_object: A detailed description of the object to generate.
        face_limit: The maximum number of faces in the model.
        auto_size: Whether to automatically size the model.

    Returns:
        A dictionary containing the task ID and instructions for checking the status.
    """
    api_key = _get_tripo_api_key()

    # Create the Tripo client
    async with TripoClient(api_key=api_key) as client:
        # Create a text-to-model task
        task_id = await client.text_to_model(
            prompt=describe_the_look_of_object,
            face_limit=face_limit,
        )

        # Get initial task status
        task = await client.get_task(task_id)

        # Return immediately with task ID and status
        return {
            "task_id": task_id,
            "status": str(task.status),
            "progress": task.progress,
            "message": "Task created successfully. The 3D model generation is in progress.",
            "next_step": "You MUST now call get_task_status with this task_id to check progress.",
            "important_note": "3D model generation takes 3-5 minutes. You need to repeatedly call get_task_status until completion.",
            "workflow": [
                "1. You've completed this step by calling create_3d_model_from_text",
                "2. Now call get_task_status with task_id: " + task_id,
                "3. If status is not SUCCESS, wait and call get_task_status again",
                "4. When status is SUCCESS, use the pbr_model_url from the response",
            ],
        }


@mcp.tool()
async def create_3d_model_from_image(
    image: str, face_limit: int = -1
) -> Dict[str, Any]:
    """
    Create a 3D model from an image using the Tripo API.

    IMPORTANT: This tool initiates a 3D model generation task but does NOT wait for completion.
    After calling this tool, you MUST repeatedly call the get_task_status tool with the returned
    task_id until the task status is SUCCESS or a terminal error state.

    Typical workflow:
    1. Call create_3d_model_from_image to start the task
    2. Get the task_id from the response
    3. Call get_task_status with the task_id
    4. If status is not SUCCESS, wait a moment and call get_task_status again
    5. Repeat until status is SUCCESS or a terminal error state
    6. When status is SUCCESS, use the pbr_model_url from the response

    Args:
        image: The local path or url to the image file.
        face_limit: The maximum number of faces in the model.
        auto_size: Whether to automatically size the model.

    Returns:
        A dictionary containing the task ID and instructions for checking the status.
    """
    api_key = _get_tripo_api_key()

    # Create the Tripo client
    async with TripoClient(api_key=api_key) as client:
        # Create a text-to-model task
        task_id = await client.image_to_model(
            image=image,
            face_limit=face_limit,
        )

        # Get initial task status
        task = await client.get_task(task_id)

        # Return immediately with task ID and status
        return {
            "task_id": task_id,
            "status": str(task.status),
            "progress": task.progress,
            "message": "Task created successfully. The 3D model generation is in progress.",
            "next_step": "You MUST now call get_task_status with this task_id to check progress.",
            "important_note": "3D model generation takes 3-5 minutes. You need to repeatedly call get_task_status until completion.",
            "workflow": [
                "1. You've completed this step by calling create_3d_model_from_image",
                "2. Now call get_task_status with task_id: " + task_id,
                "3. If status is not SUCCESS, wait and call get_task_status again",
                "4. When status is SUCCESS, use the pbr_model_url from the response",
            ],
        }


@mcp.tool()
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get the status of a 3D model generation task.

    IMPORTANT: This tool checks the status of a task started by create_3d_model_from_text.
    You may need to call this tool MULTIPLE TIMES until the task completes.

    Typical workflow:
    1. Call this tool with the task_id from create_3d_model_from_text
    2. Check the status in the response:
       - If status is SUCCESS, the task is complete and you can use the pbr_model_url
       - If status is FAILED, CANCELLED, BANNED, or EXPIRED, the task failed
       - If status is anything else, the task is still in progress
    3. If the task is still in progress, wait a moment and call this tool again

    Args:
        task_id: The ID of the task to check (obtained from create_3d_model_from_text).

    Returns:
        A dictionary containing the task status and other information.
    """
    api_key = _get_tripo_api_key()

    # Create the Tripo client
    async with TripoClient(api_key=api_key) as client:
        # Get task status
        task = await client.get_task(task_id)

        # Ensure task is not None
        if task is None:
            raise ValueError(
                f"Failed to retrieve task information for task ID: {task_id}"
            )

        # Create result dictionary
        result = {
            "task_id": task_id,
            "status": str(task.status),
            "progress": task.progress,
        }

        # Add output fields if task is successful and output is available
        if task.status == TaskStatus.SUCCESS and task.output:
            result.update(
                {
                    "base_model_url": task.output.base_model,
                    "model_url": task.output.model,
                    "pbr_model_url": task.output.pbr_model,
                    "rendered_image_url": task.output.rendered_image,
                    "message": "Task completed successfully! You can now use the pbr_model_url.",
                    "next_step": "Use the pbr_model_url to access the 3D model. Downloading and importing the GLB is handled downstream by the Blender MCP server (blender-mcp).",
                }
            )

            if not task.output.pbr_model:
                result["warning"] = (
                    "Model generated but PBR model URL is not available."
                )
        elif task.status == TaskStatus.SUCCESS:
            result["message"] = (
                "Task completed successfully but no output data is available."
            )
            result["next_step"] = (
                "Try creating a new model with a different description."
            )
        elif task.status in (
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
            TaskStatus.BANNED,
            TaskStatus.EXPIRED,
        ):
            result["message"] = f"Task failed with status: {task.status}"
            result["next_step"] = (
                "Try creating a new model with a different description."
            )
        else:
            result["message"] = (
                f"Task is still in progress. Current status: {task.status}, Progress: {task.progress}%"
            )
            result["next_step"] = (
                "IMPORTANT: You must call get_task_status again with this task_id to continue checking progress."
            )
            result["wait_message"] = (
                "3D model generation typically takes 3-5 minutes. Please be patient and keep checking."
            )

        return result


def main():
    # mcp.run("sse")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
