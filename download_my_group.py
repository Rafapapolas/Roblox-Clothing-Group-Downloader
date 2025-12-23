import asyncio
from module.roblox import AsyncRobloxDownloader

downloader = AsyncRobloxDownloader(
    template="./runtime/template.png",
    runtime_dir="./runtime/",
    max_concurrent=10  
)

async def main():
    group_id = YOUR_ID_HERE  

    
    await downloader.download_group_items(group_id, limit=10)

    print("Download batch complete!")

if __name__ == "__main__":
    asyncio.run(main())