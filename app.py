from datetime import datetime
from typing import Optional
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import models
import stripe
import os

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/")
def main():
    return 'Hello'

if os.getenv("STRIPE_SECRET_KEY") is not None:
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
else:
    stripe.api_key = open('stripe_secret_key_test','r').read()

YOUR_DOMAIN = 'https://falra.net/buy/'
@app.get("/checkout")
def checkout(price_id:str):
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': f'{price_id}',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success.html',
            cancel_url=YOUR_DOMAIN + '/cancel.html',
        )
    except Exception as e:
        return str(e)

    return RedirectResponse(url = checkout_session.url, code=303)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)