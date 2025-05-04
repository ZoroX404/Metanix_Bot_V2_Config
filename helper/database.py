import motor.motor_asyncio
from config import Config
from .utils import send_log

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.user

    def new_user(self, id):
        return dict(
            _id=int(id),
            file_id=None,
            caption=None,
            prefix=None,
            suffix=None,
            metadata=False,
            metadata_code=""" -map 0 -c:s copy -c:a copy -c:v copy -metadata title="Created By:- 𝘈𝘑" -metadata author="𝘈𝘑" -metadata:s:s title="Subtitled By :- @MetaNiXbot" -metadata:s:a title="By :- @MetaNiXbot" -metadata:s:v title="By:- 𝘈𝘑" """,
            remname=None,
            upload_type="document",  # Add a new field for upload type setting
            auto=True,
        )

    async def add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id)
            await self.col.insert_one(user)
            await send_log(b, u)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({'_id': int(user_id)})

    async def set_thumbnail(self, id, file_id):
        await self.col.update_one({'_id': int(id)}, {'$set': {'file_id': file_id}})

    async def get_thumbnail(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('file_id', None)

    async def set_caption(self, id, caption):
        await self.col.update_one({'_id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('caption', None)

    async def set_prefix(self, id, prefix):
        await self.col.update_one({'_id': int(id)}, {'$set': {'prefix': prefix}})

    async def get_prefix(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('prefix', None)

    async def set_suffix(self, id, suffix):
        await self.col.update_one({'_id': int(id)}, {'$set': {'suffix': suffix}})

    async def get_suffix(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('suffix', None)

    async def set_metadata(self, id, bool_meta):
        await self.col.update_one({'_id': int(id)}, {'$set': {'metadata': bool_meta}})

    async def get_metadata(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('metadata', None)

    async def set_metadata_code(self, id, metadata_code):
        await self.col.update_one({'_id': int(id)}, {'$set': {'metadata_code': metadata_code}})

    async def get_metadata_code(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('metadata_code', None)

    async def set_remname(self, id, remname_text):
        await self.col.update_one({'_id': int(id)}, {'$set': {'remname': remname_text}})

    async def get_remname(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('remname', None)

    async def delete_remname(self, id):
        await self.col.update_one({'_id': int(id)}, {'$unset': {'remname': ""}})
        
    async def set_upload_type(self, id, upload_type):
        await self.col.update_one({'_id': int(id)}, {'$set': {'upload_type': upload_type}})
        
    async def get_upload_type(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('upload_type', None)
        
    async def delete_upload_type(self, id):
        await self.col.update_one({'_id': int(id)}, {'$unset': {'upload_type': ""}})

    async def set_auto(self, id, upload_type):
        await self.col.update_one({'_id': int(id)}, {'$set': {'upload_type': upload_type}})
        
    async def get_auto(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('upload_type', None)
        
    async def delete_auto(self, id):
        await self.col.update_one({'_id': int(id)}, {'$unset': {'upload_type': ""}})

db = Database(Config.DB_URL, Config.DB_NAME)
