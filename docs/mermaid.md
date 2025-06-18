erDiagram

CUSTOMER {
  INT customer_id PK
  VARCHAR email
  VARCHAR phone
}

BRAND {
  INT brand_id PK
  VARCHAR name
}

LUXURY_LEVEL {
  INT luxury_level_id PK
  VARCHAR name
  DECIMAL price_per_day
}

MODEL {
  INT model_id PK
  INT brand_id FK
  INT luxury_level_id FK
  VARCHAR name
}

PICKUP_LOCATION {
  INT location_id PK
  VARCHAR country
  VARCHAR town
  VARCHAR postal_code
  VARCHAR address_line_1
  VARCHAR address_line_2
}

CAR {
  INT car_id PK
  INT model_id FK
  INT location_id FK
  VARCHAR registration_number
  INT production_year
  BOOLEAN is_visible
}

RENTAL {
  INT rental_id PK
  INT customer_id FK
  INT car_id FK
  DATE created_at
  DATE updated_at
  BOOLEAN is_email_confirmed
  DATE start_date
  DATE end_date
  DATE returned_date
  DECIMAL price_per_day_at_time_of_rental
}

PAYMENT_STATUS {
  INT payment_status_id PK
  VARCHAR name
}

PAYMENT_METHOD {
  INT payment_method_id PK
  VARCHAR name
  DECIMAL commission
}

PAYMENT {
  INT payment_id PK
  INT rental_id FK
  INT payment_method_id FK
  INT payment_status_id FK
  DATE payment_date
  DECIMAL commission_at_time_of_payment
}

RENTAL_CACHE {
  INT rental_cache_id PK
  INT car_id FK
  INT rental_id FK
  DATE occupied_day_date
}

CUSTOMER ||--o{ RENTAL : "makes"
BRAND ||--o{ MODEL : "produces"
LUXURY_LEVEL ||--o{ MODEL : "defines"
MODEL ||--o{ CAR : "includes"
PICKUP_LOCATION ||--o{ CAR : "hosts"
CAR ||--o{ RENTAL : "rented in"
RENTAL ||--o{ PAYMENT : "is paid by"
PAYMENT_METHOD ||--o{ PAYMENT : "used in"
PAYMENT_STATUS ||--o{ PAYMENT : "results in"
CAR ||--o{ RENTAL_CACHE : "tracked by"
RENTAL ||--o{ RENTAL_CACHE : "generates"


## Most popular read scenerio

Checking ready to book car: (sprawdzanie dostepnosci samochodu w danym terminie)

* sprawdzenie dostepnosci pierwszych 30 samochodów w podanym terminie i miejscem przez klienta w kolejności rosnącej ceny

(order by i limit, offset do paginacji)

```sql
SELECT 
    MODEL.name AS model_name, 
    BRAND.name AS brand_name, 
    LUXURY_LEVEL.price_per_day, 
    LUXURY_LEVEL.name AS luxury_level_name, 
    CAR.production_year,
    PICKUP_LOCATION.country,
    PICKUP_LOCATION.town
FROM CAR
JOIN MODEL ON CAR.model_id = MODEL.model_id
JOIN BRAND ON MODEL.brand_id = BRAND.brand_id
JOIN LUXURY_LEVEL ON MODEL.luxury_level_id = LUXURY_LEVEL.luxury_level_id
JOIN PICKUP_LOCATION ON CAR.location_id = PICKUP_LOCATION.location_id
WHERE 
    PICKUP_LOCATION.country = :country
    AND PICKUP_LOCATION.town = :town
    AND CAR.is_visible = TRUE
    AND CAR.car_id NOT IN (
        SELECT RENTAL_CACHE.car_id 
        FROM RENTAL_CACHE
        WHERE RENTAL_CACHE.occupied_day_date BETWEEN :start_date AND :end_date
    )
ORDER BY LUXURY_LEVEL.price_per_day ASC
LIMIT :limit OFFSET :offset;```
