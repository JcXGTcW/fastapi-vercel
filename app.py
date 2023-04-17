from datetime import datetime
from typing import Optional
import httpx
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import stripe
import os

app = FastAPI()


@app.get("/")
def main():
    return 'Hello'

if os.getenv("STRIPE_SECRET_KEY") is not None:
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
else:
    stripe.api_key = open('stripe_secret_key_test','r').read()


@app.post("/checkout")
async def checkout(price_id: str = Form(...),
                   type: str = Form(...),
                   success_url: str = Form(...),
                   cancel_url: str = Form(...),
                   token: str = Form(...)):
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': f'{price_id}',
                    'quantity': 1,
                },
            ],
            mode=type,
            success_url=success_url , # + f'?token={token}'
            cancel_url=cancel_url # + f'?token={token}'
        )
    except Exception as e:
        return str(e)

    return RedirectResponse(url=checkout_session.url, status_code=302)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)