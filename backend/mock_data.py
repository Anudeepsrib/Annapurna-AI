# Mock Data migrated from Frontend

mock_week_plan = [
    {
        "day": "Monday",
        "date": "Feb 12",
        "meals": {
            "breakfast": { "title": "Pesarattu served with Allam Pachadi", "description": "Green moong dal dosa rich in protein.", "time": "20m", "ingredients": ["Moong Dal", "Ginger", "Green Chillies"] },
            "lunch": { "title": "Rice, Tomato Pappu, and Dondakaya Vepudu", "description": "Comforting dal with tangy tomatoes and crispy ivy gourd fry.", "time": "45m", "ingredients": ["Toor Dal", "Tomato", "Dondakaya (Ivy Gourd)", "Rice"] },
            "dinner": { "title": "Phulka with Bottle Gourd (Sorakaya) Stew", "description": "Light and digestible stew with soft rotis.", "time": "30m", "ingredients": ["Wheat Flour", "Bottle Gourd", "Moong Dal"] },
        }
    },
    {
        "day": "Tuesday",
        "date": "Feb 13",
        "meals": {
            "breakfast": { "title": "Upma with Groundnut Chutney", "description": "Classic semolina breakfast with crunchy veggies.", "time": "15m", "ingredients": ["Rava (Semolina)", "Peanuts", "Green Chillies"] },
            "lunch": { "title": "Rice, Palakura Pappu, and Aloo Fry", "description": "Iron-rich spinach dal with favourite potato fry.", "time": "40m", "ingredients": ["Toor Dal", "Spinach", "Potato", "Rice"] },
            "dinner": { "title": "Lemon Rice with Curd", "description": "Zesty lemon rice with cooling yogurt.", "time": "20m", "ingredients": ["Rice", "Lemon", "Peanuts", "Curd"] },
        }
    },
    {
        "day": "Wednesday",
        "date": "Feb 14",
        "meals": {
            "breakfast": { "title": "Idli with Sambar", "description": "Steamed fermented rice cakes with lentil soup.", "time": "15m", "ingredients": ["Idli Batter", "Toor Dal", "Drumstick"] },
            "lunch": { "title": "Rice, Dosakaya Pappu, and Bendakaya Fry", "description": "Cucumber lentil stew with crispy okra.", "time": "45m", "ingredients": ["Toor Dal", "Yellow Cucumber", "Okra", "Rice"] },
            "dinner": { "title": "Jowar Roti with Brinjal Curry", "description": "Gluten-free sorghum flatbread with spicy eggplant.", "time": "40m", "ingredients": ["Jowar Flour", "Brinjal", "Tamarind"] },
        }
    },
    {
        "day": "Thursday",
        "date": "Feb 15",
        "meals": {
            "breakfast": { "title": "Pongal with Coconut Chutney", "description": "Savory rice and lentil porridge spiced with pepper.", "time": "25m", "ingredients": ["Rice", "Moong Dal", "Peppercorns", "Coconut"] },
            "lunch": { "title": "Rice, Majjiga Pulusu, and Aratikaya Bajji", "description": "Spiced buttermilk stew with raw banana fritters.", "time": "45m", "ingredients": ["Curd", "Besan", "Raw Banana", "Rice"] },
            "dinner": { "title": "Vegetable Pulao with Raita", "description": "One-pot spiced rice dish with mixed veggies.", "time": "35m", "ingredients": ["Basmati Rice", "Carrot", "Beans", "Curd"] },
        }
    },
    {
        "day": "Friday",
        "date": "Feb 16",
        "meals": {
            "breakfast": { "title": "Dosa with Tomato Chutney", "description": "Crispy fermented crepe with tangy chutney.", "time": "20m", "ingredients": ["Dosa Batter", "Tomato", "Red Chillies"] },
            "lunch": { "title": "Rice, Beerakaya Pappu, and Vankaya Vepudu", "description": "Ridge gourd dal with brinjal fry.", "time": "45m", "ingredients": ["Toor Dal", "Ridge Gourd", "Brinjal", "Rice"] },
            "dinner": { "title": "Rasam Rice with Papad", "description": "Light aromatic soup offering digestive goodness.", "time": "25m", "ingredients": ["Rice", "Tamarind", "Tomato", "Garlic"] },
        }
    },
    {
        "day": "Saturday",
        "date": "Feb 17",
        "meals": {
            "breakfast": { "title": "Semiya Upma", "description": "Vermicelli spiced with curry leaves and mustard.", "time": "15m", "ingredients": ["Vermicelli", "Onion", "Carrot"] },
            "lunch": { "title": "Pulihora (Tamarind Rice) and Payasam", "description": "Traditional tangy rice with sweet milky dessert.", "time": "50m", "ingredients": ["Rice", "Tamarind", "Jaggery", "Vermicelli"] },
            "dinner": { "title": "Chapati with Mixed Veg Curry", "description": "Whole wheat flatbread with seasonal vegetables.", "time": "35m", "ingredients": ["Wheat Flour", "Potatoes", "Cauliflower"] },
        }
    },
    {
        "day": "Sunday",
        "date": "Feb 18",
        "meals": {
            "breakfast": { "title": "Punugulu (Rice fitters)", "description": "Crispy snack-like breakfast made from dosa batter.", "time": "25m", "ingredients": ["Dosa Batter", "Oil", "Onion"] },
            "lunch": { "title": "Veg Biryani with Mirchi Ka Salan", "description": "Aromatic layered rice with spicy chili gravy.", "time": "60m", "ingredients": ["Basmati Rice", "Spices", "Green Chillies", "Peanuts"] },
            "dinner": { "title": "Light Kichdi with Kadhi", "description": "Comfort food to end the week.", "time": "30m", "ingredients": ["Rice", "Moong Dal", "Curd", "Besan"] },
        }
    },
]

grocery_categories = [
    {
        "name": "Produce",
        "items": [
            { "id": "p1", "name": "Tomatoes", "quantity": "1 kg", "meals": ["Tomato Pappu", "Rasam"] },
            { "id": "p2", "name": "Onions", "quantity": "1 kg", "meals": ["Upma", "Sambar", "Pesarattu"] },
            { "id": "p3", "name": "Green Chillies", "quantity": "200g", "meals": ["All"] },
            { "id": "p4", "name": "Curry Leaves", "quantity": "2 bunches", "meals": ["Tempering"] },
            { "id": "p5", "name": "Bottle Gourd", "quantity": "1 medium", "meals": ["Stew"] },
            { "id": "p6", "name": "Brinjal", "quantity": "500g", "meals": ["Vankaya Vepudu", "Curry"] },
        ]
    },
    {
        "name": "Grains & Dals",
        "items": [
            { "id": "g1", "name": "Toor Dal", "quantity": "500g", "meals": ["Pappu", "Sambar"] },
            { "id": "g2", "name": "Moong Dal", "quantity": "250g", "meals": ["Pesarattu", "Pongal"] },
            { "id": "g3", "name": "Sona Masoori Rice", "quantity": "5 kg", "meals": ["Staple"] },
        ]
    },
    {
        "name": "Dairy",
        "items": [
            { "id": "d1", "name": "Curd / Yogurt", "quantity": "1 kg", "meals": ["Majjiga Pulusu", "Rice side"] },
            { "id": "d2", "name": "Ghee", "quantity": "200g", "meals": ["Pongal", "Seasoning"] },
        ]
    },
    {
        "name": "Spices & Pantry",
        "items": [
            { "id": "s1", "name": "Tamarind", "quantity": "200g", "meals": ["Pulihora", "Rasam"] },
            { "id": "s2", "name": "Mustard Seeds", "quantity": "100g", "meals": ["Tempering"] },
        ]
    },
]
