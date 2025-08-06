import os
from prisma import Prisma
import asyncio

async def main() :
    db = Prisma(auto_register=True)
    return db

if __name__ == '__main__':
    asyncio.run(main())                 

        
