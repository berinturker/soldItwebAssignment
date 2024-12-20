from flask import Flask, render_template, request, g # type: ignore
import sqlite3 as sql

app = Flask(__name__)

DATABASE = 'database.db'  

def get_db():
    if 'db' not in g:
        g.db = sql.connect(DATABASE)
        g.db.row_factory = sql.Row  
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def initDB():
    with app.app_context(): 
        conn = get_db()
        print("Opened database successfully")
        
        conn.execute('''CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            ad_number TEXT,
            description TEXT,
            price REAL,
            city TEXT,
            image TEXT,
            category TEXT,
            sub_category TEXT
        );''')
        print("Table created successfully")

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ads")
        if cursor.fetchone()[0] == 0:
            ads = [
                ('Renault Clio 4', 'AD-1', '1.2 Petrol Automatic Transmission', 62500, 'Istanbul', 'static/images/clio4.jpg', 'Vehicle', 'Car'),
                ('Office Workplace', 'AD-2', 'Suitable office for large companies.', 11000000, 'Tekirdağ', 'static/images/office.jpg', 'Estate', 'Workplace'),
                ('Peugeot 2008', 'AD-3', '1.2 Puretech Hybrid car', 73900, 'Ankara', 'static/images/Peugeot2008.jpg', 'Vehicle', 'Off Road & SUV & Pickup'),
                ('Standart Apartment', 'AD-4', 'Very high quality middle floor apartment at an affordable price.', 200000, 'Afyonkarahisar', 'static/images/apartmen1.jpeg', 'Estate', 'Residence'),
                ('Toyota Corolla', 'AD-5', '1.8 L Dream Hybrid e-CVT Sedan car', 68700, 'Bursa', 'static/images/toyota-corolla-on.jpg', 'Vehicle', 'Car'),
                ('RKS BITTER 125', 'AD-6', 'Biker 50/125, 1760 km, 125cc ', 15670, 'Konya', 'static/images/rks-bitter-50-125.jpeg', 'Vehicle', 'Motorcycle'),
                ('Acre Land', 'AD-7', 'Acres of land are suitable for planting and harvesting.', 5000000, 'Urfa', 'static/images/istanbulda-satilik-arsa-kaldi-mi-3.jpg', 'Estate', 'Land'),
                ('Yamaha Tracer 700', 'AD-8', 'Super Sport, 18960 km, 35kW , 700cc', 43000, 'Aydın', 'static/images/2023-Yamaha-MT07TR.jpg', 'Vehicle', 'Motorcycle'),
                ('NIU NQi GTS 2020', 'AD-9', 'Scooter, 110 km , 3kW Bosch ', 18500, 'Antalya', 'static/images/nqi-gts-4.jpg', 'Vehicle', 'Motorcycle'),
                ('Volkswagen Golf', 'AD-10', '2024, 1.5 lt 85 kW, Hybrid car', 85000, 'Zonguldak', 'static/images/volkswagen-golf-2024.jpg', 'Vehicle', 'Car'),
                ('Izmir Villa', 'AD-11', '140 m2, Two-Storey, 5+1', 550000, 'Izmir', 'static/images/villa1.jpg', 'Estate', 'Residence'),
                ('Istanbul Residence', 'AD-12', '175 m2, 4+1', 400000, 'Istanbul', 'static/images/residence.jpg', 'Estate', 'Residence'),
                ('Tesla Model 3', 'AD-13', 'A brand new model electric Tesla car that provides a driverless car experience.', 130000, 'Istanbul', 'static/images/tesla-model3.jpg', 'Vehicle', 'Electric Car')
            ]
            
            conn.executemany('INSERT INTO ads (name, ad_number, description, price, city, image, category, sub_category) VALUES (?, ?, ?, ?, ?, ?, ?, ?);', ads)
            print("Initial records inserted successfully")
        else:
            print("Database already contains data, skipping initial insert.")
        
        conn.commit()
@app.route('/')
def home():
    conn = get_db()
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM ads LIMIT 13")
    ads = cursor.fetchall()

    cursor.execute("SELECT * FROM ads")
    all_ads = cursor.fetchall()

    category_counts = {}
    for ad in all_ads:
        main_category = ad["category"]
        sub_category = ad["sub_category"]

        if main_category not in category_counts:
            category_counts[main_category] = {"count": 0, "sub_categories": {}}

        category_counts[main_category]["count"] += 1

        if sub_category:
            if sub_category not in category_counts[main_category]["sub_categories"]:
                category_counts[main_category]["sub_categories"][sub_category] = 0
            category_counts[main_category]["sub_categories"][sub_category] += 1

    return render_template('home.html', ads=ads, category_counts=category_counts)




@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')  
    conn = get_db()
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ads WHERE name LIKE ? OR description LIKE ? OR city LIKE ? OR category LIKE ? OR sub_category LIKE ? OR price LIKE ?", 
                   (f"%{query}%", f"%{query}%",f"%{query}%",f"%{query}%",f"%{query}%",f"%{query}%"))
    ads = cursor.fetchall()
    return render_template('search.html', ads=ads, query=query)
@app.route('/category/<category>/<sub_category>')
def category_filter(category, sub_category):
    conn = get_db()
    conn.row_factory = sql.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM ads WHERE category = ? AND sub_category = ?", 
        (category, sub_category)
    )
    ads = cursor.fetchall()

    cursor.execute("SELECT * FROM ads")
    all_ads = cursor.fetchall()

    category_counts = {}
    for ad in all_ads:
        main_category = ad["category"]
        sub_category = ad["sub_category"]

        if main_category not in category_counts:
            category_counts[main_category] = {"count": 0, "sub_categories": {}}

        category_counts[main_category]["count"] += 1

        if sub_category:
            if sub_category not in category_counts[main_category]["sub_categories"]:
                category_counts[main_category]["sub_categories"][sub_category] = 0
            category_counts[main_category]["sub_categories"][sub_category] += 1

    return render_template('home.html', ads=ads, category_counts=category_counts)



@app.route('/item/<int:item_id>')
def item_detail(item_id):
    conn = get_db()
    conn.row_factory = sql.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ads WHERE id = ?", (item_id,))
    ad = cursor.fetchone()

    if not ad:
        return "Item not found", 404

    return render_template('detail.html', ad=ad)


if __name__ == '__main__':
    initDB()  
    app.run(debug=True)
