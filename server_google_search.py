from mcp.server.fastmcp import FastMCP, Context
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("GOOGLE_CSE_API_KEY")
CX_ID = os.getenv("GOOGLE_CSE_ID")

mcp = FastMCP("google_search_server")

@mcp.tool()
async def google_search(query: str, ctx: Context) -> str:
    """
    指定されたクエリでGoogle検索を行い、最初の5件の結果を返します。
    日本からの検索として扱い、日本語の結果を優先します。

    Args:
        query (str): 検索クエリ
        ctx (Context): ロギング用のMCPコンテキスト
    """

    if not query or not query.strip():
        raise ValueError("クエリを入力してください")
    
    if len(query) > 100:
        raise ValueError("クエリは100文字以内で入力してください")

    if not API_KEY or not CX_ID:
        raise Exception("Google CSE APIキーまたはCSE IDが設定されていません。")
    
    await ctx.info(f"Google検索を実行: {query}")

    try:
        service = build("customsearch", "v1", developerKey=API_KEY)
        resp = (
            service.cse()
            .list(
                q=query,
                cx=CX_ID,
                num=5,
                gl="jp",
                lr="lang_ja",
            )
            .execute()
        )
    
    except HttpError as e:
        if e.resp.status == 403:
            await ctx.error("Google CSE APIの使用制限に達しました。")
            raise Exception("Google CSE APIの使用制限に達しました。１日１００回まで")
        else:
            await ctx.error(f"Google CSE APIエラー: {str(e)}")
            raise Exception(f"Google CSE APIエラー: {str(e)}")

    except Exception as e:
        await ctx.error(f"検索エラー: {str(e)}")
        raise Exception(f"検索中にエラーが発生。: {str(e)}")

    items = resp.get("items", [])
    if not items:
        return "検索結果が見つかりませんでした"

    cleaned = []
    for rank, it in enumerate(items, 1):
        meta = (it.get("pagemap", {}).get("metatags") or [{}])[0]
        published = meta.get("article:published_time") or meta.get("og:updated_time")

        cleaned.append(
            {
                "rank": rank,
                "title": it["title"],
                "snippet": it["snippet"],
                "url": it["link"],
                "domain": it["displayLink"],
                "published_at": published,       
            }
        )

    await ctx.info(f"検索結果を取得: {len(cleaned)}件")

    return str(cleaned)

if __name__ == "__main__":
    mcp.run(transport="stdio")
