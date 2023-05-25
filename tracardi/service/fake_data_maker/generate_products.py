from random import randint

from faker import Faker

import faker_commerce

fake = Faker()
fake.add_provider(faker_commerce.Provider)


def ecommerce_price(as_int: bool = True):
    n = randint(10, 100000)
    return round(n, 2) if as_int else n / 100


def make_fake_company():
    return {
        "company": fake.company(),
        "address": fake.address()
    }


def make_fake_product():
    return {
        "name": fake.ecommerce_name(),
        "category": fake.ecommerce_category(),
        "price": ecommerce_price(False),
        "id": fake.bothify(text='????-########', letters='ABCDE')
    }


def add_to_basket():
    return {
        "name": fake.ecommerce_name(),
        "category": fake.ecommerce_category(),
        "price": ecommerce_price(False),
        "quantity": randint(1, 3),
        "id": fake.bothify(text='????-########', letters='ABCDE'),
        "sku": fake.bothify(text='????-########', letters='ABCDE')
    }


fake_products = [make_fake_product() for _ in range(0, 1000)]


def make_fake_product_purchase():
    product = fake_products[randint(0, 999)]
    product["card"] = fake.credit_card_number()
    return product


def checkout_data():
    return {
        "id": randint(0, 999123),
        "order_id": randint(0, 999123),
        "value": randint(0, 923),
        "currency": "USD",
        "coupon": "10% OFF"

    }
