# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the desired logging level

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    #READ test case
    def test_read_a_product(self):
        """It should create a product, assign it an ID, save it to the system, retrieve it back using the ID,
        and verify that the retrieved product has the same properties as the original product."""

        product = ProductFactory()
        logger.debug(str(product))
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(Decimal(found_product.price), product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)

    #UPDATE test case 
    def test_update_a_product(self):
        """It should create a product, save it to the system, update its properties, verify the updated properties,
        fetch the product back from the system, and confirm that the fetched product has the updated properties."""

        product = ProductFactory()
        logger.debug(str(product))
        product.id = None
        product.create()
        logger.debug(str(product))
        self.assertIsNotNone(product.id)
        product.description = "update a product description work fine"
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "update a product description work fine")
        list_product = Product.all()
        self.assertEqual(len(list_product), 1)
        found_product = list_product[0]
        self.assertEqual(found_product.id, original_id)
        self.assertEqual(found_product.description, "update a product description work fine")

    #UPDATE EMPTY ID test case
    def test_update_a_product_empty_id(self):
        """It should test raises error when the ID is empty"""
        product = ProductFactory()
        logger.debug(str(product))
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    #DELETE test case
    def test_delete_a_product(self):
        """It should create a product, save it to the database, delete it,
        and verify that the product is no longer present in the database."""
        product = ProductFactory()
        logger.debug(str(product))
        product.id = None
        product.create()
        self.assertEqual(len(Product.all()), 1)
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    #LIST ALL test case
    def test_list_all_products(self):
        """It should check that initially there are no products, create five products,
        and confirm that the count of the retrieved products matches the expected count of 5."""

        products = Product.all()
        self.assertEqual(len(products), 0)
        for _ in range(5):
            product = ProductFactory()
            logger.debug(str(product))
            product.create()
        products = Product.all()
        self.assertEqual(len(products), 5)

    #FIND BY NAME test case 
    def test_find_a_product_by_name(self):
        """this test case should verify if the Product.find_by_name() method correctly retrieves
        products from the database based on their name,by creating a batch of products,
        saving them to the database,finding products by name, and verifying that the count and names
        of the found products match the expected values."""

        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        name = products[0].name
        count = len([product for product in products if product.name == name])
        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, name)

    #FIND BY AVAILABILITY test 
    def test_find_a_product_by_availability(self):
        """this test case should verify if the Product.find_by_availability() method correctly retrieves
        products from the database based on their availability,by creating a batch of products,
        saving them to the database, finding products by availability,and verifying that the count
        and availability of the found products match the expected values."""

        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        available = products[0].available
        count = len([product for product in products if product.available == available])
        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, available)

    #FIND BY CATEGORY test 
    def test_find_a_product_by_category(self):
        """this test case should verify if the Product.find_by_category() method correctly retrieves products
        from the database based on their category, by creating a batch of products, saving them to the database,
        finding products by category, and verifying that the count and categories of the found products match
        the expected values."""

        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        category = products[0].category
        count = len([product for product in products if product.category == category])
        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, category)
