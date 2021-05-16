from pymongo import MongoClient
client = MongoClient("mongodb+srv://<Admin>:<Admin123>@farmfresh.ralj1.mongodb.net/FarmFreshDB?retryWrites=true&w=majority")
db = client.test