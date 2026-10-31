"""
End-to-End MongoDB Database Setup & Seeding Script (`test_commerce_db`).

Creates and populates three collections:
1. `products`  (20 items across Electronics, Books, Home Office, Accessories)
2. `customers` (15 customer profiles with nested address objects and loyalty tiers)
3. `orders`    (30 orders linking customers and product line items with dates and statuses)

Also builds single-field, unique, compound, and text indexes, and executes
sample CRUD + aggregation pipelines, displaying formatted output with `rich`.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import ASCENDING, DESCENDING, TEXT, MongoClient
from pymongo.database import Database
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

try:
    from mongodb_setup.manage_server import start_server
except ModuleNotFoundError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from mongodb_setup.manage_server import start_server

MONGO_URI = "mongodb://127.0.0.1:27017/"
DB_NAME = "test_commerce_db"

console = Console()


def get_seed_products() -> list[dict[str, Any]]:
    now = datetime(2026, 10, 1, 10, 0, 0, tzinfo=timezone.utc)
    return [
        {
            "sku": "ELEC-001",
            "name": "UltraWide 34-inch Curved Monitor",
            "category": "Electronics",
            "price": 549.99,
            "stock": 42,
            "rating": 4.8,
            "tags": ["monitor", "ultrawide", "display", "4k"],
            "description": "34-inch WQHD curved IPS monitor with 144Hz refresh rate and USB-C power delivery.",
            "created_at": now,
        },
        {
            "sku": "ELEC-002",
            "name": "Mechanical Wireless Keyboard Pro",
            "category": "Electronics",
            "price": 149.50,
            "stock": 115,
            "rating": 4.7,
            "tags": ["keyboard", "mechanical", "wireless", "hot-swap"],
            "description": "75% compact aluminum wireless mechanical keyboard with tactile switches and RGB.",
            "created_at": now,
        },
        {
            "sku": "ELEC-003",
            "name": "Active Noise Cancelling Headphones X5",
            "category": "Electronics",
            "price": 299.00,
            "stock": 68,
            "rating": 4.9,
            "tags": ["audio", "headphones", "anc", "bluetooth"],
            "description": "Studio-grade over-ear wireless headphones with 40-hour battery life and spatial audio.",
            "created_at": now,
        },
        {
            "sku": "ELEC-004",
            "name": "Thunderbolt 4 Docking Station",
            "category": "Electronics",
            "price": 219.99,
            "stock": 54,
            "rating": 4.6,
            "tags": ["dock", "thunderbolt", "usb-c", "networking"],
            "description": "15-in-1 Thunderbolt 4 dock supporting dual 4K 60Hz displays and 96W host charging.",
            "created_at": now,
        },
        {
            "sku": "ELEC-005",
            "name": "NVMe Gen4 Portable SSD 2TB",
            "category": "Electronics",
            "price": 179.95,
            "stock": 90,
            "rating": 4.8,
            "tags": ["storage", "ssd", "nvme", "portable"],
            "description": "Rugged IP65 water-resistant external NVMe SSD with 2000MB/s read/write speeds.",
            "created_at": now,
        },
        {
            "sku": "BOOK-001",
            "name": "Designing Data-Intensive Applications",
            "category": "Books",
            "price": 49.99,
            "stock": 200,
            "rating": 4.9,
            "tags": ["distributed-systems", "databases", "architecture", "engineering"],
            "description": "Comprehensive guide to reliable, scalable, and maintainable distributed data systems.",
            "created_at": now,
        },
        {
            "sku": "BOOK-002",
            "name": "MongoDB: The Definitive Guide",
            "category": "Books",
            "price": 44.50,
            "stock": 150,
            "rating": 4.7,
            "tags": ["mongodb", "nosql", "databases", "aggregation"],
            "description": "Powerful and scalable document database administration, indexing, and schema design.",
            "created_at": now,
        },
        {
            "sku": "BOOK-003",
            "name": "Fluent Python (3rd Edition)",
            "category": "Books",
            "price": 54.00,
            "stock": 130,
            "rating": 4.9,
            "tags": ["python", "programming", "asyncio", "typing"],
            "description": "Clear, concise, and effective programming in modern Python with type hints and concurrency.",
            "created_at": now,
        },
        {
            "sku": "BOOK-004",
            "name": "Building AI Agents in Production",
            "category": "Books",
            "price": 59.95,
            "stock": 85,
            "rating": 4.8,
            "tags": ["ai", "llm", "agents", "tool-use"],
            "description": "Practical patterns for orchestrating multi-agent workflows, tool calling, and evaluation.",
            "created_at": now,
        },
        {
            "sku": "BOOK-005",
            "name": "Database Internals: Deep Dive into Storage Engines",
            "category": "Books",
            "price": 52.00,
            "stock": 95,
            "rating": 4.8,
            "tags": ["databases", "b-tree", "lsm", "consensus"],
            "description": "How distributed data systems and B-Tree/LSM storage engines work under the hood.",
            "created_at": now,
        },
        {
            "sku": "HOME-001",
            "name": "Ergonomic Mesh Office Chair Elite",
            "category": "Home Office",
            "price": 429.00,
            "stock": 30,
            "rating": 4.7,
            "tags": ["chair", "ergonomic", "furniture", "lumbar"],
            "description": "Breathable mesh ergonomic chair with 4D armrests and dynamic lumbar support.",
            "created_at": now,
        },
        {
            "sku": "HOME-002",
            "name": "Dual-Motor Electric Standing Desk 60-inch",
            "category": "Home Office",
            "price": 499.00,
            "stock": 25,
            "rating": 4.8,
            "tags": ["desk", "standing-desk", "motorized", "walnut"],
            "description": "Solid walnut top sit-stand desk with programmable height presets and cable tray.",
            "created_at": now,
        },
        {
            "sku": "HOME-003",
            "name": "LED Monitor Light Bar Pro",
            "category": "Home Office",
            "price": 69.99,
            "stock": 140,
            "rating": 4.6,
            "tags": ["lighting", "desk-lamp", "monitor", "eye-care"],
            "description": "Asymmetric optical desk light bar with wireless rotary dimmer and auto-dimming sensor.",
            "created_at": now,
        },
        {
            "sku": "HOME-004",
            "name": "Heavy-Duty Gas Spring Monitor Arm",
            "category": "Home Office",
            "price": 89.50,
            "stock": 75,
            "rating": 4.7,
            "tags": ["monitor-arm", "vesa", "ergonomic", "desk"],
            "description": "Full-motion aluminum monitor mount supporting ultrawide screens up to 40 inches.",
            "created_at": now,
        },
        {
            "sku": "HOME-005",
            "name": "Acoustic Studio Foam Wall Panels (12-Pack)",
            "category": "Home Office",
            "price": 79.00,
            "stock": 60,
            "rating": 4.5,
            "tags": ["acoustic", "studio", "office", "soundproofing"],
            "description": "High-density hexagonal acoustic panels for reducing room echo during calls and recording.",
            "created_at": now,
        },
        {
            "sku": "ACCS-001",
            "name": "Ergonomic Vertical Wireless Mouse",
            "category": "Accessories",
            "price": 79.99,
            "stock": 110,
            "rating": 4.6,
            "tags": ["mouse", "ergonomic", "wireless", "bluetooth"],
            "description": "57-degree vertical posture mouse with electromagnetic scroll wheel and multi-host switch.",
            "created_at": now,
        },
        {
            "sku": "ACCS-002",
            "name": "Wool Felt Extended Desk Mat",
            "category": "Accessories",
            "price": 34.99,
            "stock": 180,
            "rating": 4.5,
            "tags": ["desk-mat", "wool", "minimalist", "accessory"],
            "description": "Merino wool blend desk pad with anti-slip natural rubber base (900x400mm).",
            "created_at": now,
        },
        {
            "sku": "ACCS-003",
            "name": "GaN 140W 4-Port Fast Charger",
            "category": "Accessories",
            "price": 84.99,
            "stock": 95,
            "rating": 4.8,
            "tags": ["charger", "gan", "usb-c", "travel"],
            "description": "Compact Gallium Nitride PD 3.1 wall charger with 3 USB-C ports and 1 USB-A port.",
            "created_at": now,
        },
        {
            "sku": "ACCS-004",
            "name": "4K UltraHD AI Auto-Framing Webcam",
            "category": "Accessories",
            "price": 139.00,
            "stock": 64,
            "rating": 4.7,
            "tags": ["webcam", "4k", "video", "streaming"],
            "description": "Sony Starvis CMOS sensor 4K webcam with dual beamforming mics and privacy shutter.",
            "created_at": now,
        },
        {
            "sku": "ACCS-005",
            "name": "Aluminum Laptop Vertical Stand",
            "category": "Accessories",
            "price": 39.50,
            "stock": 125,
            "rating": 4.6,
            "tags": ["stand", "laptop", "aluminum", "clamshell"],
            "description": "CNC-machined anodized aluminum dual-slot vertical stand for laptops and tablets.",
            "created_at": now,
        },
    ]


def get_seed_customers() -> list[dict[str, Any]]:
    base_date = datetime(2026, 1, 15, 9, 30, 0, tzinfo=timezone.utc)
    return [
        {
            "customer_code": f"CUST-{i:03d}",
            "name": name,
            "email": email,
            "loyalty_tier": tier,
            "address": {
                "city": city,
                "country": country,
                "postal_code": postal,
            },
            "joined_at": base_date,
            "is_active": True,
        }
        for i, (name, email, tier, city, country, postal) in enumerate(
            [
                ("Aarav Sharma", "aarav.sharma@example.com", "Platinum", "Bengaluru", "India", "560001"),
                ("Maya Lin", "maya.lin@example.com", "Gold", "San Francisco", "USA", "94105"),
                ("Liam O'Connor", "liam.oconnor@example.com", "Silver", "Dublin", "Ireland", "D02"),
                ("Sofia Rossi", "sofia.rossi@example.com", "Platinum", "Milan", "Italy", "20121"),
                ("Kenji Takahashi", "kenji.t@example.com", "Gold", "Tokyo", "Japan", "100-0001"),
                ("Priya Nair", "priya.nair@example.com", "Platinum", "Mumbai", "India", "400001"),
                ("Lucas Silva", "lucas.silva@example.com", "Bronze", "Sao Paulo", "Brazil", "01000"),
                ("Elena Rostova", "elena.r@example.com", "Silver", "Berlin", "Germany", "10115"),
                ("Noah Williams", "noah.w@example.com", "Gold", "Austin", "USA", "78701"),
                ("Chloe Dubois", "chloe.dubois@example.com", "Silver", "Paris", "France", "75001"),
                ("Rohan Verma", "rohan.verma@example.com", "Gold", "Hyderabad", "India", "500081"),
                ("Hannah Kim", "hannah.kim@example.com", "Platinum", "Seoul", "South Korea", "04524"),
                ("Mateo Gomez", "mateo.gomez@example.com", "Bronze", "Madrid", "Spain", "28001"),
                ("Olivia Chen", "olivia.chen@example.com", "Gold", "Toronto", "Canada", "M5V"),
                ("Zara Al-Mansoor", "zara.m@example.com", "Platinum", "Dubai", "UAE", "00000"),
            ],
            start=1,
        )
    ]


def build_seed_orders(
    products_by_sku: dict[str, dict[str, Any]],
    customers_by_code: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    order_specs = [
        ("ORD-1001", "CUST-001", [("ELEC-001", 1), ("ELEC-002", 1), ("BOOK-001", 1)], "DELIVERED", 1),
        ("ORD-1002", "CUST-002", [("HOME-001", 1), ("HOME-002", 1)], "DELIVERED", 2),
        ("ORD-1003", "CUST-003", [("BOOK-002", 2), ("BOOK-003", 1)], "DELIVERED", 3),
        ("ORD-1004", "CUST-004", [("ELEC-003", 1), ("ACCS-003", 2)], "SHIPPED", 4),
        ("ORD-1005", "CUST-005", [("ELEC-004", 1), ("ELEC-005", 1)], "DELIVERED", 5),
        ("ORD-1006", "CUST-006", [("HOME-002", 1), ("HOME-004", 1), ("ACCS-002", 1)], "DELIVERED", 6),
        ("ORD-1007", "CUST-007", [("BOOK-004", 1), ("BOOK-005", 1)], "PROCESSING", 7),
        ("ORD-1008", "CUST-008", [("ACCS-001", 1), ("ACCS-005", 1)], "DELIVERED", 8),
        ("ORD-1009", "CUST-009", [("ELEC-001", 2), ("HOME-004", 2)], "DELIVERED", 9),
        ("ORD-1010", "CUST-010", [("HOME-003", 2), ("ACCS-002", 2)], "SHIPPED", 10),
        ("ORD-1011", "CUST-011", [("ELEC-002", 1), ("ACCS-001", 1), ("BOOK-002", 1)], "DELIVERED", 11),
        ("ORD-1012", "CUST-012", [("ELEC-003", 2), ("ACCS-004", 1)], "DELIVERED", 12),
        ("ORD-1013", "CUST-013", [("BOOK-001", 1)], "CANCELLED", 13),
        ("ORD-1014", "CUST-014", [("HOME-001", 1), ("HOME-003", 1)], "DELIVERED", 14),
        ("ORD-1015", "CUST-015", [("ELEC-001", 1), ("ELEC-004", 1), ("ACCS-004", 1)], "DELIVERED", 15),
        ("ORD-1016", "CUST-001", [("BOOK-004", 2), ("BOOK-005", 1)], "DELIVERED", 16),
        ("ORD-1017", "CUST-004", [("HOME-005", 2), ("ACCS-004", 1)], "DELIVERED", 17),
        ("ORD-1018", "CUST-006", [("ELEC-005", 2), ("ACCS-003", 1)], "SHIPPED", 18),
        ("ORD-1019", "CUST-002", [("BOOK-001", 1), ("BOOK-002", 1), ("BOOK-003", 1)], "DELIVERED", 19),
        ("ORD-1020", "CUST-012", [("HOME-002", 1), ("ELEC-001", 1)], "DELIVERED", 20),
        ("ORD-1021", "CUST-009", [("ACCS-003", 2), ("ACCS-005", 2)], "PROCESSING", 21),
        ("ORD-1022", "CUST-015", [("HOME-001", 2)], "DELIVERED", 22),
        ("ORD-1023", "CUST-005", [("BOOK-004", 1), ("ELEC-002", 1)], "DELIVERED", 23),
        ("ORD-1024", "CUST-011", [("ELEC-003", 1), ("HOME-003", 1)], "SHIPPED", 24),
        ("ORD-1025", "CUST-014", [("ELEC-005", 1), ("BOOK-005", 1)], "DELIVERED", 25),
        ("ORD-1026", "CUST-001", [("HOME-001", 1), ("ACCS-001", 1)], "DELIVERED", 26),
        ("ORD-1027", "CUST-003", [("ACCS-004", 1), ("HOME-005", 1)], "DELIVERED", 27),
        ("ORD-1028", "CUST-008", [("ELEC-004", 1), ("BOOK-002", 1)], "DELIVERED", 28),
        ("ORD-1029", "CUST-010", [("BOOK-003", 1), ("BOOK-004", 1)], "PROCESSING", 29),
        ("ORD-1030", "CUST-006", [("ELEC-001", 1), ("ELEC-003", 1)], "DELIVERED", 30),
    ]

    orders: list[dict[str, Any]] = []
    for order_no, cust_code, line_specs, status, day in order_specs:
        cust = customers_by_code[cust_code]
        items = []
        total_amount = 0.0
        for sku, qty in line_specs:
            prod = products_by_sku[sku]
            line_total = round(prod["price"] * qty, 2)
            total_amount = round(total_amount + line_total, 2)
            items.append(
                {
                    "product_id": prod["_id"],
                    "sku": prod["sku"],
                    "name": prod["name"],
                    "category": prod["category"],
                    "quantity": qty,
                    "unit_price": prod["price"],
                    "line_total": line_total,
                }
            )
        orders.append(
            {
                "order_number": order_no,
                "customer_id": cust["_id"],
                "customer_code": cust_code,
                "items": items,
                "total_amount": total_amount,
                "status": status,
                "ordered_at": datetime(2026, 10, min(day, 28), 14, 0, 0, tzinfo=timezone.utc),
            }
        )
    return orders


def setup_database(uri: str = MONGO_URI, db_name: str = DB_NAME) -> Database[dict[str, Any]]:
    start_server()
    client: MongoClient[dict[str, Any]] = MongoClient(uri, serverSelectionTimeoutMS=5000)
    ping_res = client.admin.command("ping")
    if ping_res.get("ok") != 1.0:
        raise RuntimeError(f"MongoDB ping failed: {ping_res}")

    # Drop and recreate cleanly for idempotent end-to-end runs
    client.drop_database(db_name)
    db = client[db_name]

    # 1. Insert Products
    products = get_seed_products()
    db.products.insert_many(products)
    products_by_sku = {p["sku"]: p for p in db.products.find()}

    # 2. Insert Customers
    customers = get_seed_customers()
    db.customers.insert_many(customers)
    customers_by_code = {c["customer_code"]: c for c in db.customers.find()}

    # 3. Insert Orders
    orders = build_seed_orders(products_by_sku, customers_by_code)
    db.orders.insert_many(orders)

    # 4. Create Indexes
    db.products.create_index([("sku", ASCENDING)], unique=True, name="idx_sku_unique")
    db.products.create_index(
        [("category", ASCENDING), ("price", ASCENDING)],
        name="idx_category_price",
    )
    db.products.create_index(
        [("name", TEXT), ("description", TEXT)],
        name="idx_product_text_search",
    )

    db.customers.create_index([("email", ASCENDING)], unique=True, name="idx_email_unique")
    db.customers.create_index([("customer_code", ASCENDING)], unique=True, name="idx_cust_code_unique")

    db.orders.create_index([("order_number", ASCENDING)], unique=True, name="idx_order_no_unique")
    db.orders.create_index([("customer_id", ASCENDING), ("ordered_at", DESCENDING)], name="idx_customer_orders")
    db.orders.create_index([("status", ASCENDING)], name="idx_order_status")

    return db


def print_verification_report(db: Database[dict[str, Any]]) -> None:
    server_info = db.client.server_info()
    console.print(
        Panel.fit(
            f"[bold green]Connected to MongoDB v{server_info.get('version')}[/bold green]\n"
            f"Database: [bold cyan]{db.name}[/bold cyan] | "
            f"Collections: [yellow]{', '.join(sorted(db.list_collection_names()))}[/yellow]",
            title="MongoDB End-to-End Setup Summary",
        )
    )

    # Collection counts table
    counts_table = Table(title="Collection Document & Index Counts")
    counts_table.add_column("Collection", style="cyan", no_wrap=True)
    counts_table.add_column("Documents", justify="right", style="green")
    counts_table.add_column("Indexes", style="magenta")

    for coll_name in ["products", "customers", "orders"]:
        coll = db[coll_name]
        doc_count = coll.count_documents({})
        idx_names = ", ".join(coll.index_information().keys())
        counts_table.add_row(coll_name, str(doc_count), idx_names)

    console.print(counts_table)

    # Aggregation 1: Revenue by Category (excluding CANCELLED orders)
    category_pipeline: list[dict[str, Any]] = [
        {"$match": {"status": {"$ne": "CANCELLED"}}},
        {"$unwind": "$items"},
        {
            "$group": {
                "_id": "$items.category",
                "units_sold": {"$sum": "$items.quantity"},
                "total_revenue": {"$sum": "$items.line_total"},
                "distinct_orders": {"$addToSet": "$order_number"},
            }
        },
        {
            "$project": {
                "category": "$_id",
                "units_sold": 1,
                "total_revenue": {"$round": ["$total_revenue", 2]},
                "order_count": {"$size": "$distinct_orders"},
            }
        },
        {"$sort": {"total_revenue": -1}},
    ]

    cat_table = Table(title="Aggregation 1: Revenue by Product Category (Active Orders)")
    cat_table.add_column("Category", style="cyan")
    cat_table.add_column("Orders", justify="right")
    cat_table.add_column("Units Sold", justify="right")
    cat_table.add_column("Total Revenue ($)", justify="right", style="bold green")

    for row in db.orders.aggregate(category_pipeline):
        cat_table.add_row(
            str(row["category"]),
            str(row["order_count"]),
            str(row["units_sold"]),
            f"${row['total_revenue']:,.2f}",
        )
    console.print(cat_table)

    # Aggregation 2: Top 5 Customers by Total Spend via $lookup
    top_customers_pipeline: list[dict[str, Any]] = [
        {"$match": {"status": {"$ne": "CANCELLED"}}},
        {
            "$group": {
                "_id": "$customer_id",
                "order_count": {"$sum": 1},
                "total_spent": {"$sum": "$total_amount"},
            }
        },
        {
            "$lookup": {
                "from": "customers",
                "localField": "_id",
                "foreignField": "_id",
                "as": "customer",
            }
        },
        {"$unwind": "$customer"},
        {"$sort": {"total_spent": -1}},
        {"$limit": 5},
    ]

    cust_table = Table(title="Aggregation 2: Top 5 Customers by Total Spend ($lookup)")
    cust_table.add_column("Customer", style="cyan")
    cust_table.add_column("Tier", style="yellow")
    cust_table.add_column("City / Country")
    cust_table.add_column("Orders", justify="right")
    cust_table.add_column("Total Spend ($)", justify="right", style="bold green")

    for row in db.orders.aggregate(top_customers_pipeline):
        c = row["customer"]
        cust_table.add_row(
            f"{c['name']} ({c['customer_code']})",
            c["loyalty_tier"],
            f"{c['address']['city']}, {c['address']['country']}",
            str(row["order_count"]),
            f"${row['total_spent']:,.2f}",
        )
    console.print(cust_table)

    # Text Search Verification
    text_results = list(
        db.products.find(
            {"$text": {"$search": "distributed databases mongodb"}},
            {"score": {"$meta": "textScore"}, "sku": 1, "name": 1, "price": 1},
        ).sort([("score", {"$meta": "textScore"})])
    )
    search_table = Table(title="Full-Text Index Search: 'distributed databases mongodb'")
    search_table.add_column("SKU", style="cyan")
    search_table.add_column("Name", style="white")
    search_table.add_column("Price", justify="right", style="green")
    search_table.add_column("Relevance Score", justify="right", style="magenta")
    for item in text_results:
        search_table.add_row(
            item["sku"],
            item["name"],
            f"${item['price']:.2f}",
            f"{item['score']:.2f}",
        )
    console.print(search_table)


if __name__ == "__main__":
    database = setup_database()
    print_verification_report(database)
