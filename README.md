# Tripo MCP Server

**The1Studio's fork of [Tripo MCP](https://github.com/VAST-AI-Research/tripo-mcp)** — a **Tripo-generation-only** MCP server.

This fork does one thing: it drives the [Tripo AI](https://www.tripo3d.ai) API to generate 3D models via [Model Context Protocol (MCP)](https://modelcontextprotocol.io), and hands back the resulting GLB URL. It holds **no Blender tools and no Blender addon dependency**.

> **Blender is owned elsewhere.** Scene manipulation, asset import, and everything else inside Blender are provided by **[blender-mcp](https://github.com/ahujasid/blender-mcp)** (mcp-for-blender) **2.0.0** — the single Blender authority in our pipeline. This server is one generation backend alongside Rodin and Hunyuan3D, which blender-mcp already hosts.
>
> The handoff is the URL: when a generation task succeeds, this server returns `pbr_model_url`; blender-mcp downloads and imports that GLB downstream.

## Current Features

- Generate a 3D model from a natural-language prompt (`create_3d_model_from_text`)
- Generate a 3D model from an image, local path or URL (`create_3d_model_from_image`)
- Poll generation progress and retrieve the model URLs (`get_task_status`)
- Compatible with Claude and other MCP-enabled AI assistants

## Quick Start

### Prerequisites

- Python 3.10+
- A Tripo AI API key
- Claude for Desktop or Cursor IDE
- [blender-mcp](https://github.com/ahujasid/blender-mcp) 2.0.0, if you want the generated model imported into Blender

### Installation

The API key is read from the **`TRIPO_API_KEY` environment variable**. There is no Blender addon to install and no other source for the key.

1. Configure the MCP server in Claude Desktop or Cursor, passing `TRIPO_API_KEY` through `env`.

    * `pip install uv`
    * set mcp in cursor
    ```json
    {
      "mcpServers": {
        "tripo-mcp": {
          "command": "uvx",
          "args": [
            "tripo-mcp"
          ],
          "env": {
            "TRIPO_API_KEY": "tsk_xxxxxxxxxxxxxxxx"
          }
        }
      }
    }
    ```

    If `TRIPO_API_KEY` is missing or empty the server raises an error naming the variable, rather than falling back to another source.

    * Then you will get a green dot like this:
      ![img](succeed.jpg)

### Usage

1. Chat using Cursor or Claude. E.g., "Generate a 3D model of a futuristic chair".

2. Call `create_3d_model_from_text` or `create_3d_model_from_image` to start a task, then call `get_task_status` until the status is `SUCCESS` or a terminal error state.

3. Take the `pbr_model_url` from the success response and hand it to blender-mcp to import the model into your Blender scene.

## Acknowledgements

- **[Tripo AI](https://www.tripo3d.ai)**
- **[blender-mcp](https://github.com/ahujasid/blender-mcp)** by [Siddharth Ahuja](https://github.com/ahujasid)

**Special Thanks**  
Special thanks to Siddharth Ahuja for the blender-mcp project, which provided inspiring ideas for MCP + 3D.
