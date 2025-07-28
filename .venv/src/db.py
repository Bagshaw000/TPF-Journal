import os
from prisma import Prisma
from prisma.models import  user
import asyncio

async def main() :
    db = Prisma(auto_register=True)
    return db

if __name__ == '__main__':
    asyncio.run(main())                 

        




# data={
#                         'first_name': 'Robert',
#                         'email': 'robert@craigie.dev',
#                         'last_name': 'Robert',
#                         'plan': 'free'
#                     },