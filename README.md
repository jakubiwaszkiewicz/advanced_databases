# advanced_databases

Mermaid code:
```mermaid
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
        BOOLEAN is_available
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

    CUSTOMER ||--o| RENTAL : ""
    RENTAL ||--|| CAR : ""
    CAR |o--|| MODEL : ""
    CAR |o--|| PICKUP_LOCATION : ""
    MODEL |o--|| BRAND : ""
    MODEL |o--|| LUXURY_LEVEL : ""
    PAYMENT |o--|| RENTAL : ""
    PAYMENT |o--|| PAYMENT_METHOD : ""
    PAYMENT |o--|| PAYMENT_STATUS : ""
    RENTAL_CACHE |o--|| CAR : ""
    RENTAL_CACHE |o--|| RENTAL : ""
```

## Most popular read scenerio

The code of it is included in the `/backend/main.py:/api/rent-car` endpoint.

## Most popular write scenerio

Creating a rental reservation
The code of it is included in the `/backend/main.py:/api/available-cars` endpoint.
