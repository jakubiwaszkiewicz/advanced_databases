import asyncio
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from datetime import date, timedelta
import databases
import sqlalchemy
from fastapi import Query
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+aiomysql://user:password@mysql:3306/db"
)

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

print(sys.platform)

if sys.platform == 'win32':
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

class RentalRequest(BaseModel):
    customer_id: int
    car_id: int
    start_date: date
    end_date: date

@app.post("/api/rent-car")
async def rent_car(data: RentalRequest):
    try:
        async with database.transaction():

            conflict_query = """
                SELECT 1
                FROM RENTAL_CACHE
                WHERE car_id = :car_id
                AND occupied_day_date BETWEEN :start_date AND :end_date
                LIMIT 1
            """
            conflict = await database.fetch_one(conflict_query, {
                "car_id": data.car_id,
                "start_date": data.start_date,
                "end_date": data.end_date
            })

            if conflict:
                raise HTTPException(
                    status_code=400,
                    detail="The car is already reserved during the selected period."
                )

            price_query = """
                SELECT LUXURY_LEVEL.price_per_day
                FROM CAR
                JOIN MODEL ON CAR.model_id = MODEL.model_id
                JOIN LUXURY_LEVEL ON MODEL.luxury_level_id = LUXURY_LEVEL.luxury_level_id
                WHERE CAR.car_id = :car_id
            """
            row = await database.fetch_one(price_query, {"car_id": data.car_id})
            if not row:
                raise HTTPException(status_code=404, detail="Car not found")
            price_per_day = row["price_per_day"]

            insert_rental_query = """
                INSERT INTO RENTAL (
                    customer_id, car_id, created_at, updated_at,
                    is_email_confirmed, start_date, end_date,
                    returned_date, price_per_day_at_time_of_rental
                )
                VALUES (
                    :customer_id, :car_id, CURDATE(), CURDATE(),
                    FALSE, :start_date, :end_date,
                    NULL, :price_per_day
                )
            """
            await database.execute(
                insert_rental_query,
                {
                    "customer_id": data.customer_id,
                    "car_id": data.car_id,
                    "start_date": data.start_date,
                    "end_date": data.end_date,
                    "price_per_day": price_per_day
                }
            )

            rental_id_row = await database.fetch_one("SELECT LAST_INSERT_ID() AS rental_id")
            rental_id = rental_id_row["rental_id"]

            rental_days = []
            current_date = data.start_date
            while current_date <= data.end_date:
                rental_days.append({
                    "car_id": data.car_id,
                    "rental_id": rental_id,
                    "occupied_day_date": current_date
                })
                current_date += timedelta(days=1)

            insert_cache_query = """
                INSERT INTO RENTAL_CACHE (car_id, rental_id, occupied_day_date)
                VALUES (:car_id, :rental_id, :occupied_day_date)
            """
            await database.execute_many(insert_cache_query, rental_days)

            return {"message": "Car reserved successfully", "rental_id": rental_id}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")




@app.get("/api/available-cars")
async def get_available_cars(
    location_id: int = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    limit: int = Query(30),
    offset: int = Query(0)
):
    query = """
        SELECT 
            MODEL.name AS model_name, 
            BRAND.name AS brand_name, 
            LUXURY_LEVEL.price_per_day, 
            LUXURY_LEVEL.name AS luxury_level_name,
            CAR.car_id, 
            CAR.production_year,
            PICKUP_LOCATION.country,
            PICKUP_LOCATION.town
        FROM CAR
        JOIN MODEL ON CAR.model_id = MODEL.model_id
        JOIN BRAND ON MODEL.brand_id = BRAND.brand_id
        JOIN LUXURY_LEVEL ON MODEL.luxury_level_id = LUXURY_LEVEL.luxury_level_id
        JOIN PICKUP_LOCATION ON CAR.location_id = PICKUP_LOCATION.location_id
        WHERE 
            CAR.location_id = :location_id
            AND CAR.is_visible = TRUE
            AND CAR.car_id NOT IN (
                SELECT RENTAL_CACHE.car_id 
                FROM RENTAL_CACHE
                WHERE RENTAL_CACHE.occupied_day_date BETWEEN :start_date AND :end_date
            )
        ORDER BY LUXURY_LEVEL.price_per_day ASC
        LIMIT :limit OFFSET :offset
    """

    rows = await database.fetch_all(query, {
        "location_id": location_id,
        "start_date": start_date,
        "end_date": end_date,
        "limit": limit,
        "offset": offset
    })

    return rows
