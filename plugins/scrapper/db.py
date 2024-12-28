import datetime
import motor.motor_asyncio
from config import Config

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users = self.db.UsersData
        self.black = self.db.TamilMV_List
        self.tb = self.db.TamilBlaster_List
        self.tr = self.db.TamilRockers_List
        self.domains = self.db.Domains

    def tamilmv(self, Name, link, url):
        return dict(
            FileName = Name,
            magnet_link = link,
            magnet_url = url,
            upload_date=datetime.date.today().isoformat()
        )

    async def add_tamilmv(self, Name, link, url):
        user = self.tamilmv(Name, link, url)
        await self.black.insert_one(user)

    async def is_tamilmv_exist(self, Name, link, url):
        user = await self.black.find_one({'magnet_url': url})
        return True if user else False

    def tbx(self, Name, link, url):
        return dict(
            FileName = Name,
            magnet_link = link,
            magnet_url = url,
            upload_date=datetime.date.today().isoformat()
        )

    async def add_tb(self, Name, link, url):
        user = self.tbx(Name, link, url)
        await self.tb.insert_one(user)

    async def is_tb_exist(self, Name, link, url):
        user = await self.tb.find_one({'magnet_url': url})
        return True if user else False

    # TamilRockers DB Functions

    def tr(self, Name, link, url):
        return dict(
            FileName = Name,
            magnet_link = link,
            magnet_url = url,
            upload_date=datetime.date.today().isoformat()
        )

    async def add_tr(self, Name, link, url):
        user = self.tr(Name, link, url)
        await self.tr.insert_one(user)

    async def is_tr_exist(self, Name, link, url):
        user = await self.tr.find_one({'magnet_url': url})
        return True if user else False

    # Domain Management Functions
    async def add_or_update_domain(self, key, url):
        """
        Add a new domain or update an existing one with the provided key and URL.
        """
        existing_domain = await self.domains.find_one({"key": key})
        if existing_domain:
            # Update existing domain
            await self.domains.update_one({"key": key}, {"$set": {"url": url}})
        else:
            # Insert new domain
            await self.domains.insert_one({"key": key, "url": url})
    
    async def get_all_domains(self):
        """
        Retrieve all domains from the database.
        """
        domains = {}
        async for domain in self.domains.find():
            domains[domain["key"]] = domain["url"]
        return domains

    async def get_domain(self, key):
        """
        Retrieve a specific domain URL by its key.
        """
        domain = await self.domains.find_one({"key": key})
        return domain["url"] if domain else None

    async def delete_domain(self, key):
        """
        Delete a domain by its key.
        """
        result = await self.domains.delete_one({"key": key})
        return result.deleted_count > 0

u_db = Database(Config.DB_URL, Config.DB_NAME)
