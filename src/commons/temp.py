import json

import requests

body = {
    "result": 0,
    "insurance": {
        "insurance_start": "2020-11-24",
        "insurance_mature": "2021-11-23"
    },
    "checkout_schedule": [
        {
            "amount": 3800,
            "cancel_at": None,
            "is_cancel": False,
            "checkout_due_date": "2020-11-26",
            "settlement_datetime": "2020-11-23 04:29:22"
        },
        {
            "amount": 3800,
            "cancel_at": None,
            "is_cancel": False,
            "checkout_due_date": "2020-12-23",
            "settlement_datetime": None
        },
        {
            "amount": 3800,
            "cancel_at": None,
            "is_cancel": False,
            "checkout_due_date": "2021-01-23",
            "settlement_datetime": None
        },
        {
            "amount": 3800,
            "cancel_at": None,
            "is_cancel": False,
            "checkout_due_date": "2021-02-23",
            "settlement_datetime": None
        },
        {
            "amount": 3800,
            "cancel_at": None,
            "is_cancel": False,
            "checkout_due_date": "2021-03-23",
            "settlement_datetime": None
        },
        {
            "amount": 3800,
            "cancel_at": None,
            "is_cancel": False,
            "checkout_due_date": "2021-04-23",
            "settlement_datetime": None
        },
        {
            "amount": 3800,
            "cancel_at": None,
            "is_cancel": False,
            "checkout_due_date": "2021-05-23",
            "settlement_datetime": None
        },
        {
            "amount": 3800,
            "cancel_at": None,
            "is_cancel": False,
            "checkout_due_date": "2021-06-23",
            "settlement_datetime": None
        },
        {
            "amount": 3800,
            "cancel_at": None,
            "is_cancel": False,
            "checkout_due_date": "2021-07-23",
            "settlement_datetime": None
        },
        {
            "amount": 3800,
            "cancel_at": None,
            "is_cancel": False,
            "checkout_due_date": "2021-08-23",
            "settlement_datetime": None
        },
        {
            "amount": 3800,
            "cancel_at": None,
            "is_cancel": False,
            "checkout_due_date": "2021-09-23",
            "settlement_datetime": None
        },
        {
            "amount": 3800,
            "cancel_at": None,
            "is_cancel": False,
            "checkout_due_date": "2021-10-23",
            "settlement_datetime": None
        }
    ],
    "inspection_complete": "2020-11-23 16:41:45"
}

import json
response = requests.post(
    "https://micare.mibank.xyz/insurance/3834064d-9a72-4898-913e-6587c16a4b32/complete/",
    data=json.dumps(body),
    headers={
        "Content-Type": "application/json"
    }
)

import curlify

curl = curlify.to_curl(response.request)

"""
curl -X POST -H 'Accept: */*' -H 'Accept-Encoding: gzip, deflate' -H 'Connection: keep-alive' -H 'Content-Length: 1965' -H 'User-Agent: python-requests/2.24.0' -H 'content-type: application/json' -d 'result=0&insurance=insurance_start&insurance=insurance_mature&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&checkout_schedule=amount&checkout_schedule=cancel_at&checkout_schedule=is_cancel&checkout_schedule=checkout_due_date&checkout_schedule=settlement_datetime&inspection_complete=2020-11-23+16%3A41%3A45' https://micare.mibank.xyz/insurance/3834064d-9a72-4898-913e-6587c16a4b32/complete/
"""
