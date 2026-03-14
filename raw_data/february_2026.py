raw_input_json = """
{
    "cashback": 3043,
    "transactions": [
        {
            "date": "24 Jan 26",
            "merchant": "AMAZONIN GURGAON IN",
            "amount": 106.0,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "24 Jan 26",
            "merchant": "MEESHO BANGALORE IN",
            "amount": 160.0,
            "type": "C",
            "mode": null,
            "done_by": null
        },
        {
            "date": "25 Jan 26",
            "merchant": "PAYMENT RECEIVED 000DP016025232708XrvERg",
            "amount": 24953.0,
            "type": "C",
            "mode": null,
            "done_by": null
        },
        {
            "date": "25 Jan 26",
            "merchant": "CAS*REDBUS INDIA PRIVA BANGALORE NOR IN (Pay in EMIs)",
            "amount": 3570.0,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "25 Jan 26",
            "merchant": "TRAVELOGY ONLINE PRIVA KAMRUP IN (Pay in EMIs)",
            "amount": 6192.0,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "26 Jan 26",
            "merchant": "AMAZON PAY INDIA PRIVA WWW.AMAZON.IN IN",
            "amount": 449.0,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "26 Jan 26",
            "merchant": "RAZ*GULLAK TECHNOLOGIE Bengaluru KA IN",
            "amount": 194.4,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "26 Jan 26",
            "merchant": "RAZ*GULLAK TECHNOLOGIE Bengaluru KA IN",
            "amount": 193.5,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "26 Jan 26",
            "merchant": "RAZ*GULLAK TECHNOLOGIE Bengaluru KA IN",
            "amount": 193.5,
            "type": "C",
            "mode": null,
            "done_by": null
        },
        {
            "date": "28 Jan 26",
            "merchant": "RAZ*GULLAK TECHNOLOGIE Bengaluru KA IN",
            "amount": 254.7,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "28 Jan 26",
            "merchant": "AMAZON PAY INDIA PRIVA WWW.AMAZON.IN IN",
            "amount": 399.0,
            "type": "C",
            "mode": null,
            "done_by": null
        },
        {
            "date": "29 Jan 26",
            "merchant": "SWIGGY LIMITED BANGALORE IN",
            "amount": 341.0,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "29 Jan 26",
            "merchant": "AMAZON PAY INDIA PRIVA WWW.AMAZON.IN IN",
            "amount": 479.32,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "29 Jan 26",
            "merchant": "RAZ*GULLAK TECHNOLOGIE Bengaluru KA IN",
            "amount": 238.5,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "31 Jan 26",
            "merchant": "MEESHO TECHNOLOGIES PR Bangalore IN",
            "amount": 1052.0,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "31 Jan 26",
            "merchant": "ZOMATO LIMITED Gurugram IN",
            "amount": 166.9,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "01 Feb 26",
            "merchant": "AMAZON PAY INDIA PRIVA WWW.AMAZON.IN IN",
            "amount": 311.0,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "03 Feb 26",
            "merchant": "AMAZON PAY INDIA PRIVA WWW.AMAZON.IN IN (Pay in EMIs)",
            "amount": 10000.0,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "03 Feb 26",
            "merchant": "AMAZON PAY INDIA PRIVA WWW.AMAZON.IN IN (Pay in EMIs)",
            "amount": 10000.0,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "03 Feb 26",
            "merchant": "RAZ*GULLAK TECHNOLOGIE Bengaluru KA IN (Pay in EMIs)",
            "amount": 6000.0,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "03 Feb 26",
            "merchant": "AMAZON PAY INDIA PRIVA Bangalore IN (Pay in EMIs)",
            "amount": 10000.0,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "03 Feb 26",
            "merchant": "AMAZON PAY INDIA PRIVA Bangalore IN (Pay in EMIs)",
            "amount": 10000.0,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "05 Feb 26",
            "merchant": "RAZ*GULLAK TECHNOLOGIE Bengaluru KA IN",
            "amount": 210.0,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "05 Feb 26",
            "merchant": "RAZ*GULLAK TECHNOLOGIE Bengaluru KA IN",
            "amount": 210.0,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "05 Feb 26",
            "merchant": "RAZ*GULLAK TECHNOLOGIE Bengaluru KA IN",
            "amount": 210.0,
            "type": "C",
            "mode": null,
            "done_by": null
        },
        {
            "date": "06 Feb 26",
            "merchant": "AMAZON PAY INDIA PRIVA Bangalore IN",
            "amount": 350.0,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "07 Feb 26",
            "merchant": "ZOMATO NEW DELHI IN",
            "amount": 328.5,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "07 Feb 26",
            "merchant": "MEESHO TECHNOLOGIES PR Bangalore IN",
            "amount": 72.0,
            "type": "C",
            "mode": null,
            "done_by": null
        },
        {
            "date": "07 Feb 26",
            "merchant": "MEESHO TECHNOLOGIES PR Bangalore IN",
            "amount": 84.0,
            "type": "C",
            "mode": null,
            "done_by": null
        },
        {
            "date": "07 Feb 26",
            "merchant": "MEESHO TECHNOLOGIES PR Bangalore IN",
            "amount": 84.0,
            "type": "C",
            "mode": null,
            "done_by": null
        },
        {
            "date": "07 Feb 26",
            "merchant": "MEESHO TECHNOLOGIES PR Bangalore IN",
            "amount": 148.0,
            "type": "C",
            "mode": null,
            "done_by": null
        },
        {
            "date": "08 Feb 26",
            "merchant": "DISTRICT MOVIE TICKET GURUGRAM IN",
            "amount": 389.96,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "09 Feb 26",
            "merchant": "RAZ*GULLAK TECHNOLOGIE Bengaluru KA IN",
            "amount": 1000.0,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "10 Feb 26",
            "merchant": "RAZ*GULLAK TECHNOLOGIE Bengaluru KA IN",
            "amount": 210.0,
            "type": "D",
            "mode": null,
            "done_by": null
        },
        {
            "date": "22 Feb 26",
            "merchant": "22 Jan 26 CARD CASHBACK CREDIT",
            "amount": 1009.0,
            "type": "C",
            "mode": null,
            "done_by": null
        },
        {
            "date": "22 Feb 26",
            "merchant": "07 Feb 26 MEESHO TECHNOLOGIES PR Bangalore IN",
            "amount": 125.0,
            "type": "C",
            "mode": null,
            "done_by": null
        }
    ]
}
"""