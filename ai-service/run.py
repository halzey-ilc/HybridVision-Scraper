import asyncio
import sys
import uvicorn
def main():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    uvicorn.run(
        "app.main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True,
        workers=1  # В Windows для Proactor лучше использовать 1 воркер при reload
    )

if __name__ == "__main__":
    main()