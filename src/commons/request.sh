#!/usr/bin/env bash

curl -X POST \
-H 'Accept: */*' \
-H 'Accept-Encoding: gzip, deflate' \
-H 'Connection: keep-alive' \
-H 'Content-Length: 1965' \
-H 'User-Agent: python-requests/2.24.0' \
-H 'content-type: application/json' \
-d 'result=0&insurance=insurance_start&insurance=insurance_mature&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&inspection_complete=2020-11-23+16%3A41%3A45' https://micare.mibank.xyz/insurance/3834064d-9a72-4898-913e-6587c16a4b32/complete/
