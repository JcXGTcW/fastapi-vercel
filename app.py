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


@app.get("/", response_class=HTMLResponse)
def index(request: Request, username: str = None):
    if not username:
        return templates.TemplateResponse("index.html", context={"request": request})
    user = get_github_profile(request, username)
    context = {"request": request, "user": user}
    return templates.TemplateResponse("index.html", context=context)
@app.get("/{username}", response_model=models.GithubUserModel)
def get_github_profile(request: Request, username: str) -> Optional[models.GithubUserModel]:
    headers = {"accept": "application/vnd.github.v3+json"}
    response = httpx.get(f"https://api.github.com/users/{username}", headers=headers)
    if response.status_code == 404:
        return False
    user = models.GithubUserModel(**response.json())
    # Sobreescribir la fecha con el formato que necesitamos
    user.created_at = datetime.strptime(user.created_at, "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%y")
    return user


if os.getenv("STRIPE_SECRET_KEY") != '':
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