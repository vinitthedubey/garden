from pymongo import MongoClient
# MongoDB connection
client = MongoClient("mongodb+srv://vinit_dubey:1860Amul@cluster0.zjwfiov.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['Garden']
user_collection = db['normal_plant_search']
print("MongoClient imported successfully!")

data = {
    "_id": "Neem",
    "Neem": [
        "./static/data/image/Neem/Neem-Full.jpg",
        "./static/data/image/Neem/Neem-Leaf.png",
        "Azadirachta indica",
        ["neem", "nim tree", "Indian lilac", "margosa tree"],
        {
            "habitat": {
                "Regions": "Dry, arid, and semi-arid areas with low rainfall.",
                "Soil Type": "Well-drained, sandy, or rocky soils; it tolerates poor and degraded soils.",
                "Climate": "Hot climates with temperatures ranging from 25°C to 40°C; resistant to drought and thrives in areas with annual rainfall between 450 mm and 1200 mm.",
                "Altitude": "Grows up to elevations of 1500 meters above sea level.",
                "Common Locations": "Roadsides, farmland boundaries, and urban areas as shade trees due to their resilience and adaptability."
            }
        },
        {
            "medicinal uses": {
                "Skin Health": "Neem is widely used in treating acne, eczema, and other skin conditions due to its antibacterial and anti-inflammatory properties.",
                "Oral Hygiene": "Neem twigs and extracts are used in toothpaste and mouthwash for preventing gum diseases and maintaining oral health.",
                "Blood Purification": "Neem helps detoxify the blood, improving overall health and combating various infections.",
                "Immune Booster": "Regular use of neem can strengthen the immune system due to its antimicrobial and antioxidant properties.",
                "Digestive Aid": "Neem helps alleviate ulcers, intestinal worms, and other digestive issues."
            }
        },
        {
            "methods of cultivation": {
                "Climate and Soil Requirements": "Neem thrives in tropical and subtropical regions with temperatures between 25°C to 40°C",
                "Propagation": "Neem is propagated primarily through seeds.",
                "Sowing": "Seeds can be sown directly in the field or in nursery beds for transplantation.",
                "Irrigation": "Neem trees are drought-tolerant and require minimal watering after establishment.",
                "Fertilization": "Apply organic manure or compost during the planting stage to promote growth.",
                "Harvesting": "Neem trees begin to produce seeds after 3-5 years.",
                "Additional Care": "Mulching around the base can retain soil moisture and prevent weed growth.",
                "vedio link": "https://www.youtube.com/embed/QZY_j0b15BU?si=Z8_Lbh0lcepPKgtT"
            }
        }
    ]
}

user_collection.insert_one(data)