"""Automated verification test suite for the local MongoDB setup (`test_commerce_db`)."""

from __future__ import annotations

import unittest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from mongodb_setup.seed_and_verify_mongodb import DB_NAME, MONGO_URI, setup_database


class TestMongoDBSetup(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.db = setup_database(MONGO_URI, DB_NAME)
        cls.client: MongoClient = cls.db.client

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.close()

    def test_01_server_ping(self) -> None:
        res = self.client.admin.command("ping")
        self.assertEqual(res.get("ok"), 1.0)

    def test_02_collections_and_counts(self) -> None:
        collections = set(self.db.list_collection_names())
        self.assertTrue({"products", "customers", "orders"}.issubset(collections))
        self.assertEqual(self.db.products.count_documents({}), 20)
        self.assertEqual(self.db.customers.count_documents({}), 15)
        self.assertEqual(self.db.orders.count_documents({}), 30)

    def test_03_unique_index_enforcement(self) -> None:
        existing_customer = self.db.customers.find_one({"customer_code": "CUST-001"})
        self.assertIsNotNone(existing_customer)
        with self.assertRaises(DuplicateKeyError):
            self.db.customers.insert_one(
                {
                    "customer_code": "CUST-999",
                    "name": "Duplicate Email User",
                    "email": existing_customer["email"],
                }
            )

    def test_04_text_search_index(self) -> None:
        results = list(
            self.db.products.find({"$text": {"$search": "ergonomic monitor"}})
        )
        self.assertGreaterEqual(len(results), 2)

    def test_05_aggregation_pipeline(self) -> None:
        pipeline = [
            {"$match": {"status": {"$ne": "CANCELLED"}}},
            {"$group": {"_id": None, "grand_total": {"$sum": "$total_amount"}}},
        ]
        agg_res = list(self.db.orders.aggregate(pipeline))
        self.assertEqual(len(agg_res), 1)
        self.assertGreater(agg_res[0]["grand_total"], 10000.0)


if __name__ == "__main__":
    unittest.main()
