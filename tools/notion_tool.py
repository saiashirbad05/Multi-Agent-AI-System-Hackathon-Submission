"""Notion MCP integration tool for notes management."""
import os
from notion_client import Client


def get_notion_client():
    token = os.environ.get("NOTION_API_TOKEN")
    if not token:
        raise ValueError("NOTION_API_TOKEN not set in environment")
    return Client(auth=token)


def create_notion_page(title: str, content: str) -> dict:
    """Create a new page in Notion under the configured parent page."""
    try:
        client = get_notion_client()
        parent_id = os.environ.get("NOTION_PAGE_ID")
        if not parent_id:
            return {"success": False, "message": "NOTION_PAGE_ID not configured"}
        
        response = client.pages.create(
            parent={"type": "page_id", "page_id": parent_id},
            properties={"title": {"title": [{"text": {"content": title}}]}},
            children=[{
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]}
            }]
        )
        return {
            "success": True,
            "page_id": response["id"],
            "url": response.get("url", ""),
            "message": f"Notion page '{title}' created"
        }
    except Exception as e:
        return {"success": False, "message": f"Notion error: {str(e)}"}


def list_notion_pages() -> dict:
    """List pages in the Notion workspace."""
    try:
        client = get_notion_client()
        parent_id = os.environ.get("NOTION_PAGE_ID")
        response = client.blocks.children.list(block_id=parent_id)
        pages = []
        for block in response.get("results", []):
            if block.get("type") == "child_page":
                pages.append({
                    "id": block["id"],
                    "title": block["child_page"].get("title", "Untitled")
                })
        return {"success": True, "pages": pages, "count": len(pages)}
    except Exception as e:
        return {"success": False, "message": f"Notion error: {str(e)}"}


def append_to_notion_page(page_id: str, content: str) -> dict:
    """Append content block to an existing Notion page."""
    try:
        client = get_notion_client()
        client.blocks.children.append(
            block_id=page_id,
            children=[{
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]}
            }]
        )
        return {"success": True, "message": "Content appended to Notion page"}
    except Exception as e:
        return {"success": False, "message": f"Notion error: {str(e)}"}
