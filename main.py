from typing import Optional
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from website_validation import WebsiteValidator
from constants import (
    PASSED, FAILED, INNER_NOT_TRANSLATED, DROP_DOWN_NOT_WORKING,
    PAGE_NOT_TRANSLATED, NOT_HIGH_RESOLUTION, WRONG_PAGE
)

app = FastAPI()
templates = Jinja2Templates(directory='templates/')


@app.get("/")
async def root():
    return {"message": "Welcome to Michael's Trial Task"}


@app.get("/check_urls", response_class=HTMLResponse)
async def check_urls(request: Request):
    context = {"request": request, "urls": "", "result": ""}
    return templates.TemplateResponse("index.html", context=context)


def add_failed(val: str, error: str):
    if FAILED in val:
        return f"{val}; {error}"

    return f"{FAILED}: {error}"


@app.post("/check_urls", response_class=HTMLResponse)
async def check_urls(request: Request, urls: Optional[str] = Form(...)):
    result = {}
    with WebsiteValidator() as check:
        for url in urls.split("\n"):
            url = url.strip()
            if not url:
                continue
            result[url] = PASSED
            try:
                translated = check.page_translated(url)
                if not translated:
                    result[url] = add_failed(result[url], PAGE_NOT_TRANSLATED)

                img_high_quality = check.images_high_resolution()
                if not img_high_quality:
                    result[url] = add_failed(result[url], NOT_HIGH_RESOLUTION)

                dropdown = check.js_drop_downs()
                if not dropdown:
                    result[url] = add_failed(result[url], DROP_DOWN_NOT_WORKING)

                inner_translated = check.inner_page_translated()
                if not inner_translated:
                    result[url] = add_failed(result[url], INNER_NOT_TRANSLATED)

            except Exception as e:
                print(e)
                result[url] = add_failed(result[url], WRONG_PAGE)
                continue

    # Result dictionary to list of strings
    result_list = []
    for k, v in result.items():
        result_list.append(f"{k}:   {v}")
    context = {"request": request, "urls": "", "results": result_list}

    return templates.TemplateResponse("index.html", context=context)
