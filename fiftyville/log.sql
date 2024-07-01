-- Keep a log of any SQL queries you execute as you solve the mystery.

--1. Pull the crime scene report for the date and location of the theft
SELECT id, description FROM crime_scene_reports
    WHERE street = "Humphrey Street" AND day = 28 AND month = 07 AND year = 2021;
--theft at 10:15 am/at Humphrey Street bakery/3 witnesses/ALL mentions the bakery
--littering at 16:36, no known witnesses. (Irrelevant?)


--2. Pull interview reports of (3 witnesses) from TABLE interviews, to get witnesses name and transcript
SELECT name, transcript FROM interviews
    WHERE day = 28 AND month = 07 AND year = 2021;
--there were 7 people in the output. and 3 has mentioned the theft, which are Ruth, Eugene and Raymond
--we also learned that Emma is the bakery owner
--**Ruth: within 10 mins of the theft,, the thief got into a car in the bakery parking lot
--**Eugene: it's someone he recognized but don't know the name. saw the thief using ATM on Leggett St
--**Raymon: overheard that they were planning to take the earliest flight out of Fiftyville tomorrow
    --The thief then asked the person on the other end of the phone to purchase the flight ticket.
--##Emma: someone suspiciously whispering into a phone for about half an hour. Never bought anything.


--3. get license_plate# and owner name (on July 28, 2021, bakery parking lot, between 10:15 and 10:25am)
SELECT name, phone_number, passport_number, license_plate FROM people
    WHERE license_plate IN (SELECT license_plate FROM bakery_security_logs
            WHERE day = 28 AND month = 07 AND year = 2021 AND hour = 10 AND minute >=15 AND minute <=25
            AND activity = "exit");
--+---------+----------------+-----------------+---------------+
--|  name   |  phone_number  | passport_number | license_plate |
--+---------+----------------+-----------------+---------------+
--| Vanessa | (725) 555-4692 | 2963008352      | 5P2BI95       |
--| Barry   | (301) 555-4174 | 7526138472      | 6P58WS2       |
--| Iman    | (829) 555-5269 | 7049073643      | L93JTIZ       |
--| Sofia   | (130) 555-0289 | 1695452385      | G412CB7       |
--| Luca    | (389) 555-5198 | 8496433585      | 4328GD8       |
--| Diana   | (770) 555-1861 | 3592750733      | 322W7JE       |
--| Kelsey  | (499) 555-9472 | 8294398571      | 0NTHK55       |
--| Bruce   | (367) 555-5533 | 5773159633      | 94KL13X       |
--+---------+----------------+-----------------+---------------+


--4. find bank_accounts details from atm_transactions (possiable caller)
    --before noon; on Leggett Street; withdraw
SELECT name, passport_number, bank_accounts.account_number FROM people, atm_transactions, bank_accounts
    WHERE people.id = bank_accounts.person_id
    AND atm_transactions.account_number = bank_accounts.account_number
    AND day = 28 AND month = 07 AND year = 2021
    AND atm_location = "Leggett Street" AND transaction_type = "withdraw";
--8 outputs. Bruce, Iman and Luca are account holders who also showed up in previous query (3)


--5. find caller and receiver of the call Raymon mentioned
    --lasted less than 1 min
    --caller asked the receiver to purchase flight ticket
    --i tried SELECT caller, receiver, duration FROM phone_calls to first see what the data looks like
SELECT caller, name FROM phone_calls, people
    WHERE people.phone_number = caller
    AND day = 28 AND month = 07 AND year = 2021 AND duration < 60
    ORDER BY phone_calls.id;
    --9 matching calls total, Bruce was the only caller who used the ATM from the previous query

SELECT receiver, name FROM phone_calls, people
    WHERE people.phone_number = receiver
    AND day = 28 AND month = 07 AND year = 2021 AND duration < 60
    ORDER BY phone_calls.id;
    --Robin was the person on the phone with Bruce, which is the person who bought the ticket


--6. check the flight departing Fiftyville next morning (July 29, 2021)
    --find out destination
    --passengers details
SELECT airports.city, airports.full_name, people.name, people.passport_number FROM airports, flights, passengers, people
    WHERE airports.id = flights.destination_airport_id
    AND flights.id = passengers.flight_id AND passengers.passport_number = people.passport_number
    AND flights.origin_airport_id = (SELECT airports.id FROM airports WHERE city = "Fiftyville")
    AND day = 29 AND month = 07 AND year = 2021 ORDER BY flights.hour;
    --Bruce is on the passenger list, destination airport is New York City
    --it's the same Bruce from step 3 because it's the same passport number
