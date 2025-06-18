import random
import string
import uuid
from faker import Faker

fake = Faker()



# Konfiguracja liczby rekordow
NUM_CUSTOMERS = 10000
NUM_BRANDS = 500
NUM_MODELS = 1000
NUM_CARS = 50000
NUM_PICKUP_LOCATIONS = 100
NUM_RENTALS = 50000
NUM_PAYMENTS = 50000
NUM_RENTAL_CACHE = 20000

# ID tracking
customer_ids = list(range(1, NUM_CUSTOMERS + 1))
brand_ids = list(range(1, NUM_BRANDS + 1))
model_ids = list(range(1, NUM_MODELS + 1))
car_ids = list(range(1, NUM_CARS + 1))
pickup_ids = list(range(1, NUM_PICKUP_LOCATIONS + 1))
rental_ids = list(range(1, NUM_RENTALS + 1))

# Otworz plik do zapisu
with open("init.sql", "w", encoding="utf-8") as f:
    f.write("""
-- ====================================
-- DROP EXISTING TABLES (if any)
-- ====================================
DROP TABLE IF EXISTS RENTAL_CACHE;
DROP TABLE IF EXISTS PAYMENT;
DROP TABLE IF EXISTS PAYMENT_METHOD;
DROP TABLE IF EXISTS PAYMENT_STATUS;
DROP TABLE IF EXISTS RENTAL;
DROP TABLE IF EXISTS CAR;
DROP TABLE IF EXISTS MODEL;
DROP TABLE IF EXISTS LUXURY_LEVEL;
DROP TABLE IF EXISTS BRAND;
DROP TABLE IF EXISTS PICKUP_LOCATION;
DROP TABLE IF EXISTS CUSTOMER;

-- ====================================
-- CREATE TABLES
-- ====================================

CREATE TABLE CUSTOMER (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(255)
);

CREATE TABLE BRAND (
    brand_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE LUXURY_LEVEL (
    luxury_level_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price_per_day DECIMAL(10,2) NOT NULL
);

CREATE TABLE MODEL (
    model_id INT AUTO_INCREMENT PRIMARY KEY,
    brand_id INT NOT NULL,
    luxury_level_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    CONSTRAINT fk_model_brand FOREIGN KEY (brand_id) REFERENCES BRAND(brand_id),
    CONSTRAINT fk_model_luxury_level FOREIGN KEY (luxury_level_id) REFERENCES LUXURY_LEVEL(luxury_level_id)
);

CREATE TABLE PICKUP_LOCATION (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    country VARCHAR(100) NOT NULL,
    town VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    address_line_1 VARCHAR(255) NOT NULL,
    address_line_2 VARCHAR(255)
);

CREATE TABLE CAR (
    car_id INT AUTO_INCREMENT PRIMARY KEY,
    model_id INT NOT NULL,
    location_id INT NOT NULL,
    registration_number VARCHAR(50) UNIQUE NOT NULL,
    production_year INT NOT NULL,
    is_visible BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_car_model FOREIGN KEY (model_id) REFERENCES MODEL(model_id),
    CONSTRAINT fk_car_location FOREIGN KEY (location_id) REFERENCES PICKUP_LOCATION(location_id)
);

CREATE TABLE RENTAL (
    rental_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    car_id INT NOT NULL,
    created_at DATE NOT NULL,
    updated_at DATE NOT NULL,
    is_email_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    returned_date DATE,
    price_per_day_at_time_of_rental DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_rental_customer FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id),
    CONSTRAINT fk_rental_car FOREIGN KEY (car_id) REFERENCES CAR(car_id)
);

CREATE TABLE PAYMENT_STATUS (
    payment_status_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE PAYMENT_METHOD (
    payment_method_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    commission DECIMAL(10,2) NOT NULL
);

CREATE TABLE PAYMENT (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    rental_id INT NOT NULL,
    payment_method_id INT NOT NULL,
    payment_status_id INT NOT NULL,
    payment_date DATE,
    commission_at_time_of_payment DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_payment_rental FOREIGN KEY (rental_id) REFERENCES RENTAL(rental_id),
    CONSTRAINT fk_payment_method FOREIGN KEY (payment_method_id) REFERENCES PAYMENT_METHOD(payment_method_id),
    CONSTRAINT fk_payment_status FOREIGN KEY (payment_status_id) REFERENCES PAYMENT_STATUS(payment_status_id)
);

CREATE TABLE RENTAL_CACHE (
    rental_cache_id INT AUTO_INCREMENT PRIMARY KEY,
    car_id INT NOT NULL,
    rental_id INT NOT NULL,
    occupied_day_date DATE NOT NULL,
    CONSTRAINT fk_cache_car FOREIGN KEY (car_id) REFERENCES CAR(car_id),
    CONSTRAINT fk_cache_rental FOREIGN KEY (rental_id) REFERENCES RENTAL(rental_id)
);

""")
    def generate_random_email():
      username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(6, 12)))
      domain = fake.domain_name()
      return f"{username}@{domain}"
    
    # CUSTOMER
    f.write("INSERT INTO CUSTOMER (customer_id, email, phone) VALUES\n")
    for i in customer_ids:
        email = generate_random_email()
        phone = fake.phone_number().replace("\n", "")
        f.write(f"({i}, '{email}', '{phone}')" + ("," if i != NUM_CUSTOMERS else ";") + "\n")

    # BRAND
    f.write("\nINSERT INTO BRAND (brand_id, name) VALUES\n")
    for i in brand_ids:
        name = fake.company().replace("'", "")
        f.write(f"({i}, '{name}')" + ("," if i != NUM_BRANDS else ";") + "\n")

    # LUXURY_LEVEL
    f.write("\nINSERT INTO LUXURY_LEVEL (luxury_level_id, name, price_per_day) VALUES\n")
    luxury_levels = ['STANDARD', 'LUXURY', 'PREMIUM']
    luxury_level_ids = [1,2,3]
    for i, name in enumerate(luxury_levels, start=1):
        price_per_day = round(random.uniform(50.0, 500.0), 2)
        f.write(f"({i}, '{name}', {price_per_day})" + ("," if i != len(luxury_levels) else ";") + "\n")

    # MODEL
    f.write("\nINSERT INTO MODEL (model_id, brand_id, name, luxury_level_id) VALUES\n")
    for i in model_ids:
        brand_id = random.choice(brand_ids)
        name = fake.word().capitalize()
        luxury_level_id = random.choice(luxury_level_ids)
        f.write(f"({i}, {brand_id}, '{name}', '{luxury_level_id}')" + ("," if i != NUM_MODELS else ";") + "\n")

    # PICKUP_LOCATION
    f.write("\nINSERT INTO PICKUP_LOCATION (location_id, country, town, postal_code, address_line_1, address_line_2) VALUES\n")
    for i in pickup_ids:
        town = fake.city().replace("'", "")
        country = fake.country().replace("'", "")
        postal_code = fake.postcode().replace("'", "")
        address_line_1 = fake.street_address().replace("'", "")
        address_line_2 = fake.secondary_address().replace("'", "")
        
        f.write(
            f"({i}, '{country}', '{town}', '{postal_code}', '{address_line_1}', '{address_line_2}')"
            + (",\n" if i != pickup_ids[-1] else ";\n")
    )

    # CAR
    f.write("\nINSERT INTO CAR (car_id, model_id, location_id, registration_number, production_year, is_visible) VALUES\n")
    for i in car_ids:
        model_id = random.choice(model_ids)
        pickup_id = random.choice(pickup_ids)
        reg_num = fake.bothify(text='?????########')
        year = random.randint(2018, 2024)
        is_visible = random.choice([1, 0])
        f.write(
            f"({i}, {model_id}, {pickup_id}, '{reg_num}', {year}, {is_visible})"
            + (",\n" if i != car_ids[-1] else ";\n")
        )

        # rental_id INT AUTO_INCREMENT PRIMARY KEY,
        # customer_id INT NOT NULL,
        # car_id INT NOT NULL,
        # created_at DATE NOT NULL,
        # updated_at DATE NOT NULL,
        # is_email_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
        # start_date DATE NOT NULL,
        # end_date DATE NOT NULL,
        # returned_date DATE,
        # price_per_day_at_time_of_rental DECIMAL(10,2) NOT NULL,

    # RENTAL
    f.write("\nINSERT INTO RENTAL (rental_id, customer_id, car_id, created_at, updated_at, is_email_confirmed, start_date, end_date, returned_date, price_per_day_at_time_of_rental) VALUES\n")
    for i in rental_ids:
        customer_id = random.choice(customer_ids)
        car_id = random.choice(car_ids)
        created_at = fake.date_between(start_date='-2y', end_date='today')
        updated_at = fake.date_between(start_date=created_at, end_date='today')
        is_email_confirmed = random.choice([0, 1])
        start_date = fake.date_between(start_date='-2y', end_date='today')
        end_date = fake.date_between(start_date=start_date, end_date='+30d')
        returned_date = fake.date_between(start_date=start_date, end_date='+30d')
        price_per_day_at_time_of_rental = round(random.uniform(50.0, 500.0), 2)
        f.write(f"({i}, {customer_id}, {car_id},'{created_at}','{updated_at}', '{is_email_confirmed}' ,'{start_date}', '{end_date}', '{returned_date}', '{price_per_day_at_time_of_rental}')" + ("," if i != NUM_RENTALS else ";") + "\n")

    # RENTAL_CACHE
    f.write("\nINSERT INTO RENTAL_CACHE (rental_cache_id, car_id, rental_id, occupied_day_date) VALUES\n")
    for i in range(1, NUM_RENTAL_CACHE + 1):
        rental_id = random.choice(rental_ids)
        car_id = random.choice(car_ids)
        occupied_day_date = fake.date_between(start_date='-2y', end_date='today')
        f.write(f"({i}, {rental_id}, {car_id}, '{occupied_day_date}')" + ("," if i != NUM_RENTAL_CACHE else ";") + "\n")

print("Plik 'generated_data.sql' został wygenerowany.")
