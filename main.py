import random
from bs4 import BeautifulSoup
import asyncio
import tempfile
import shutil
import nodriver as uc


async def random_delay(min_delay: float = 1.0, max_delay: float = 3.0):
    delay = random.uniform(min_delay, max_delay)
    await asyncio.sleep(delay)


async def run_browser():
    """
    Input your path for temporary profiles
    """
    profile_dir = tempfile.mkdtemp(dir=r"Your path for temporary profiles")
    url = "https://booking.com"
    browser = await uc.start(user_data_dir=profile_dir, browser_args=[
        "--lang=en-US",
    ],
                             )

    location = input('Input location')
    user_checkin_date = input('Input check-in date in format "year-mm-dd"')
    user_checkout_date = input('Input check-out date in format "year-mm-dd"')

    try:
        page = await browser.get(url)
        await asyncio.sleep(5)
        place = await page.query_selector('[placeholder="Where are you going?"]')
        if not place:
            print(f'Destination button was not found')

        date_field = await page.query_selector('button[data-testid="date-display-field-start"]')
        if not date_field:
            print(f'date field was not found')

        search_btn = await page.query_selector('button[type="submit"]')
        if not search_btn:
            print(f'Search button was not found')

        if place and date_field and search_btn:
            print("Elements has been found")
            await place.send_keys(location)
            await random_delay()
            await date_field.click()
            checkin_field = await page.query_selector(f'[data-date="{user_checkin_date}"]')
            if not checkin_field:
                print('check-in field was not found')
            await checkin_field.click()
            await random_delay()
            checkout_field = await page.query_selector(f'[data-date="{user_checkout_date}"]')
            if not checkout_field:
                print('check-out field was not found')
            await checkout_field.click()
            await random_delay()
            await search_btn.click()
            await asyncio.sleep(5)
            await page.scroll_down(5000)
            await asyncio.sleep(2)
            html = await page.get_content()
            soup = BeautifulSoup(html, 'lxml')
            cards = soup.find_all(attrs={"data-testid": "property-card-container"})
            with open('hotels.txt', 'w', encoding='utf-8') as file:
                for card in cards:
                    hotel_card = BeautifulSoup(str(card), 'lxml')
                    hotel_name = hotel_card.find(attrs={"data-testid": "title"}).text
                    hotel_price = hotel_card.find(attrs={"data-testid": "price-and-discounted-price"}).text
                    hotel_score = hotel_card.find(attrs={"data-testid": "review-score"}).text.split()[1]
                    file.write(f"{hotel_name}\t{hotel_price}\t{hotel_score}\n")
            print('Work is done!')
    except Exception as e:
        print(f"Browser error, {e}")
    finally:
        if browser:
            browser.stop()
        await asyncio.sleep(2)
        shutil.rmtree(profile_dir)


uc.loop().run_until_complete(run_browser())
