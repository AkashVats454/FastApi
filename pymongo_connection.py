from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = (
    "mongodb+srv://akashvats454:OWyel4DiuKqHNlUI@cluster0.p0kbxyp.mongodb.net/?retryWrites=true&w=majority&appName="
    "Cluster0"
)


class ServiceDB:
    def __init__(self, collection):
        self.uri = uri
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db_name = self.client["fastapi"]
        self.collection_name = self.db_name[collection]

    def check_conection(self):
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

    def insert_many(self, list_data: list):
        self.collection_name.insert_many(list_data)
        print("Data inserted Successfully!")

    def insert_one(self, data: dict):
        self.collection_name.insert_one(data)
        print("Data inserted Successfully!")

    def get_from_db(self, query: dict):
        rec = self.collection_name.find_one(query)
        print("Data fetched Successfully!")
        return rec

    def update_db(self, query: dict, data: dict):
        self.collection_name.update_one(query, {"$set": data})
        print("Data updated Successfully!")

    def delete_one(self, query: dict):
        self.collection_name.delete_one(query)
        print("Data deleted Successfully!")

# item_1 = {
#     "username": "johndoe",
#     "full_name": "John Doe",
#     "email": "johndoe@example.com",
#     "hashed_password": "fakehashedsecret",
#     "disabled": False,
# }
#
# item_2 = {
#     "username": "alice",
#     "full_name": "Alice Wonderson",
#     "email": "alice@example.com",
#     "hashed_password": "fakehashedsecret2",
#     "disabled": True,
# }
