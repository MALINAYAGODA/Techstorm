import asyncio
import json
import aiohttp
import time

from agi_project.utils import WebPage




class PageRenderer:

    async def run(self, urls: list):
        if urls:
            return await self._scrape_multiple(urls)

    async def run_legacy(self, url: str, *urls: str):
        if urls:
            return await asyncio.gather(self._scrape_single(url), *(self._scrape_single(i) for i in urls))
        return await self._scrape_single(url)

    async def _scrape_single(self, url: str) -> WebPage:
        data = {
            "urls": [url],
        }
        headers = {"Content-Type": "application/json", "Authorization": "Basic YXRvbTpoZWxwbWVoZWxwbWVoZWxwbWU="}
        _API_ENDPOINT_R = "http://localhost:8070/renderPages" # "http://195.242.16.26:8080/renderPages"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(_API_ENDPOINT_R, json=data, headers=headers, timeout=25) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        item = response_data["result"]["completeTasks"][0]
                        web_page = WebPage(
                            inner_text=item["pageText"],
                            html="None",
                            url=url
                        )
                        return web_page
                return None
        except asyncio.TimeoutError:
            print("Request timed out")
            return None

    async def _scrape_multiple(self, urls: list[str]) -> list[WebPage]:
        _API_ENDPOINT_R = "http://195.242.16.26:8080/renderPages"
        data = {"urls": urls}
        headers = {"Content-Type": "application/json", "Authorization": "Basic YXRvbTpoZWxwbWVoZWxwbWVoZWxwbWU="}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(_API_ENDPOINT_R, json=data, headers=headers, timeout=20) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        items = response_data["result"]["completeTasks"]
                        result = [
                            WebPage(
                                inner_text=item["pageText"],
                                html="None",
                                url=item["url"]
                            )
                            for item in items
                        ]
                        return result
                return None
        except asyncio.TimeoutError:
            print("Request timed out")
            return None


# async def get_render(sd, urls):
#     contents = await sd.run(urls)
#     return contents


# async def main():
#     sd = AtomPageRenderer()
#     links = [
#         ["https://www.b2b-tatneft.ru/", "https://raexpert.ru/database/companies/1000012430/"],
#         ["https://rss.tatneft.ru/locator/list?region_id=2&region_name=г.Казань%2C++районы+прилегающие+к+городу.&dont_change_region=0&fuel_type_id=0&fuel_type_name=Выбрать+вид+топлива&address=&previous_region_id=48&previous_region_name=Татарстан&page=2", "https://raexpert.ru/database/companies/1000012430/"],
#         ["https://www.b2b-tatneft.ru/", "https://www.benzin-price.ru/price.php?region_id=16&brand_id=13?utm_referrer=https%3A%2F%2Fyandex.ru%2F"],
#         ["https://multigo.ru/autoTravel/poi/509e9a09907850664d1cbfdb", "https://raexpert.ru/database/companies/1000012430/"]
#     ]
#     start = time.time()
#     todo = [get_render(sd, i) for i in links]

#     summaries = await asyncio.gather(*todo)
#     print(f"Time taken: {time.time() - start} seconds")

#     for summary in summaries:
#         if summary is not None:
#             print(len(summary))
#             for i in summary:
#                 print("- ", len(i.inner_text))
#         else:
#             print("None")


# # Run the async main function
# asyncio.run(main())
