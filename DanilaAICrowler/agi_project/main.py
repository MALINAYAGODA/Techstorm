import base64
import requests
import json
import uuid
import urllib3
from utils import OutputParser, WebPage
import time
import sys
import aiohttp
sys.path.append("../KAZAN")

from pydantic import TypeAdapter
import asyncio
from render_utils import PageRenderer


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

client_id = "20f43d1e-1f45-43cc-8f90-d6aa84116206"
secret = "5f56c358-271e-475b-aabf-9f50b98d1c72"
_API_ENDPOINT = "http://195.242.16.26:8080/performSearch"


auth = base64.b64encode(f"{client_id}:{secret}".encode('utf-8')).decode('utf-8')

SEARCH_TOPIC_PROMPT = """Please provide up to 2 necessary key phrases related to your research topic for Google search. Write in the language of the user's request. \
Your response must be in JSON format, for example: ["key phrase 1", "key phrase 2"]."""

RESEARCH_TOPIC_SYSTEM = "You are an AI researcher assistant, and your research topic is:\n#TOPIC#\n{topic}"

SUMMARIZE_SEARCH_PROMPT = """### Requirements
1. The keywords related to your research topic and the search results are shown in the "Search Result Information" section.
2. Provide up to only {decomposition_nums} queries related to your research topic base on the search results.
3. Respond in the following JSON format: ["query1", "query2", "query3", ...].

### Search Result Information
{search_results}
###
Provide up to only {decomposition_nums} queries.
Respond in the following JSON format: ["query1", "query2", "query3", ...]
Important: ask questions that will definitely be able to find answers on google to "{topic}"
Today is August 24th, 2024.
"""
RESEARCH_BASE_SYSTEM = """You are an AI critical thinker research assistant. Your sole purpose is to write well \
written, critically acclaimed, objective and structured reports on the given text."""

LANG_PROMPT = "Please respond in {language}."

WEB_BROWSE_AND_SUMMARIZE_PROMPT = """### Requirements
1. Utilize the text in the "Reference Information" section to respond to the question "{query}".
2. If the question cannot be directly answered using the text, but the text is related to the research topic, please provide \
a comprehensive summary of the text.
3. If the text is entirely unrelated to the research topic, please reply with a simple text "Not relevant."
4. Include all relevant factual information, numbers, statistics, etc., if available.

### Reference Information
{content}
"""

CONDUCT_RESEARCH_PROMPT = """### Reference Information
{content}

### Requirements
If there are many answers, choose the most relevant and frequent answer.
Please provide a message report in response to the following topic: "{topic}", using the information provided \
above. The report must meet the following requirements:

- Focus on directly addressing the chosen topic.
- Incorporating relevant facts and figures where available.
- Present data and findings in an intuitive manner, utilizing feature comparative tables, if applicable.
- The report should have a minimum word count of 100 and be formatted with Markdown syntax following APA style guidelines.

Important: at the end of your message, output only those link text from Reference Information where there is relevant information. Answer and display the links!
"""


def get_research_system_text(topic: str, language: str):
    """Get the system text for conducting research.

    Args:
        topic: The research topic.
        language: The language for the system text.

    Returns:
        The system text for conducting research.
    """
    return " ".join((RESEARCH_TOPIC_SYSTEM.format(topic=topic), LANG_PROMPT.format(language=language)))

def get_token(auth_token, scope='GIGACHAT_API_PERS'):
    try:
        response = requests.post(
            "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': str(uuid.uuid4()),
                'Authorization': f'Basic {auth_token}'
            },
            data={'scope': scope},
            verify=False
        )
        return response if response.status_code == 200 else None
    except requests.RequestException as e:
        print(f"Ошибка: {str(e)}")
        return None

def get_chat_completion(auth_token, user_message, system_prompt):
    try:
        response = requests.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {auth_token}'
            },
            data=json.dumps({
                "model": "GigaChat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 1,
                "top_p": 0.1,
                "n": 1,
                "stream": False,
                "max_tokens": 512,
                "repetition_penalty": 1,
                "update_interval": 0
            }),
            verify=False
        )
        return response.json().get('choices')[0].get('message').get('content')
    except requests.RequestException as e:
        print(f"Произошла ошибка: {str(e)}")
        return None
    
async def web_browser_engine(urls: list):
    _API_ENDPOINT_2 = "http://195.242.16.26:8080/renderPages"
    if urls:
        urls_combined = urls
        data = {"urls": urls_combined, "maxTimeoutMs": 15000}
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic YXRvbTpoZWxwbWVoZWxwbWVoZWxwbWU="
        }

        # try:
        async with aiohttp.ClientSession() as session:
                async with session.post(_API_ENDPOINT_2, json=data, headers=headers, timeout=25) as response:
                    if response.status == 200:
                        print(response)
                        response_data = await response.json()
                        items = response_data["result"]["completeTasks"]
                        result = [
                            WebPage(
                                inner_text=item["pageText"],
                                url=item["url"]
                            )
                            for item in items
                        ]
                        return result
                    else:
                        return None
        # except asyncio.TimeoutError:
        #     print("Request timed out")
        #     return None
    
async def search_engine(query, max_results: int = 4):
    url = "https://google.serper.dev/search"
    payload = json.dumps({
      "q": query,
      "gl": "ru"
    })
    headers = {
      'X-API-KEY': '9bfd930bbc25fa413f6d5c308a8487e307ae6a24',
      'Content-Type': 'application/json'
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        data = json.loads(response.text)
        organic_results = data.get("organic", [])
        ret_data = [{"title": item["title"], "snippet": item["snippet"], "link": item["link"]} for item in
                            organic_results[:max_results]]
        return ret_data
    except:
        return None
    
async def get_links(topic, giga_token):
    system_text = RESEARCH_TOPIC_SYSTEM.format(topic=topic)
    keywords = get_chat_completion(giga_token, SEARCH_TOPIC_PROMPT, system_text)
    print(keywords)
    try:
        keywords = OutputParser.extract_struct(keywords, list)
        keywords = TypeAdapter(list[str]).validate_python(keywords)
    except Exception as e:
        print('Problem_1')
        keywords = [topic]
    results = await asyncio.gather(*(search_engine(i) for i in keywords))

    def gen_msg(keywords, results, topic):
            search_results = "\n".join(
                f"#### Keyword: {i}\n Search Result: {j}\n" for (i, j) in zip(keywords, results)
            )
            prompt = SUMMARIZE_SEARCH_PROMPT.format(
                decomposition_nums=4, search_results=search_results, topic=topic
            )
            return prompt

    prompt = gen_msg(keywords, results, topic)
    queries = get_chat_completion(giga_token, prompt, system_text)
    print(queries)
    try:
        queries = OutputParser.extract_struct(queries, list)
        queries = TypeAdapter(list[str]).validate_python(queries)
    except Exception as e:
        print("Problem_2")
        queries = keywords
    ret = {}
    main_links = await asyncio.gather(*(search_engine(query) for query in queries))
    for i in range(len(main_links)):
        ret[queries[i]] = [j['link'] for j in main_links[i]]
    # all_links = []
    # for k, v in ret.items():
    #     all_links += v
    return ret

# async def summarize(urls: list, query: str, system_text: str = RESEARCH_BASE_SYSTEM):
#     contents = await web_browser_engine(urls)
#     if not urls:
#         contents = [contents]
#     try:
#         print("+", len(contents))
#     except:
#         print("+", 0)
#     return contents
#     # summaries = {}
#     # prompt_template = WEB_BROWSE_AND_SUMMARIZE_PROMPT.format(query=query, content="{}")
#     # async def summarizing_links(u, content):
#     #     content = content.inner_text
#     #     prompt = prompt_template.format(content=content)
#     #     summary = get_chat_completion(giga_token, prompt, system_text)
#     #     if summary == "Not relevant.":
#     #         summaries[u] = None
#     #         return 
#     #     else:
#     #         summaries[u] = summary
#     #         return
#     # print(zip([url, *urls], contents))
#     # parallel_summarization = (
#     #        summarizing_links(u, content) for u, content in zip([url, *urls], contents)
#     # )
#     # await asyncio.gather(*parallel_summarization)
#     # print('Есть +1')
#     # return summaries

async def get_render_text(sd, urls: list, query: str):  # список из 4 content
    start = time.time()
    contents = await sd.run(urls)
    print("* ", time.time()-start)
    return (contents, query, urls)
    

async def summarize(contents, giga_token, urls: list, query: str, system_text: str = RESEARCH_BASE_SYSTEM):
    summaries = {}
    async def summarizing_links(u, content):
        content = content.inner_text
        prompt = WEB_BROWSE_AND_SUMMARIZE_PROMPT.format(query=query, content=content)
        summary = get_chat_completion(giga_token, prompt, system_text)
        print("Ответ: " + summary)
        if summary == "Not relevant." or summary == 'Не актуально':
            summaries[u] = None
            return 
        else:
            summaries[u] = summary
            return
    # url_res = ''
    # content_res = ''
    # for i in range(len(contents)):
    #     if len(contents[i].inner_text) != 0:
    #         content_res = contents[i]
    #         url_res = urls[i]
    #         break

    start = time.time()
    try:
       for i in range(len(urls)):
           await summarizing_links(urls[i], contents[i])
    except:
        return summaries
    print("- ", time.time()-start)
    # parallel_summarization = (
    #        summarizing_links(u, content) for u, content in zip(urls, contents)
    # )
    # await asyncio.gather(*parallel_summarization)
    return summaries

async def get_summarize(sd, giga_token, links, topic):
    research_system_text = get_research_system_text(topic, "ru")  # "en-us"
    start = time.time()
    
    todo = [
        get_render_text(sd, urls, query=query) 
        for query, urls in links.items()
    ]
    render_texts = await asyncio.gather(*todo)
    render_texts = [i for i in render_texts if i[0] is not None]
    # for summary in render_texts:
    #     if summary is not None:
    #         for i in summary[0]:
    #             print("- ", i.inner_text)
    #     else:
    #         print("None")

    todo = [
        summarize(content, giga_token, urls, query=query, system_text=research_system_text) 
        for content, query, urls  in render_texts
    ]
    summaries = await asyncio.gather(*todo)
    
    print("Total time:", time.time() - start)
    return summaries
    
    # summaries = [
    #     (url, summary) for i in summaries for url, summary in i.items() if summary
    # ]
    # return summaries

async def conduct(giga_token, topic, content):
    system_text = get_research_system_text(topic, "ru")
    prompt = CONDUCT_RESEARCH_PROMPT.format(topic=topic, content=content)
    return get_chat_completion(giga_token, prompt, system_text)


async def crawler(topic):
    
    response = get_token(auth)
    giga_token = response.json().get('access_token')

    # topic = input("Ваш вопрос: ")
    start = time.time()
    links = await get_links(topic, giga_token)
    print("First phase: ", time.time() - start)

    sd = PageRenderer()
    summaries = await get_summarize(sd, giga_token, links, topic)
    new_summaries = {}
    for summa in summaries:
        for k, v in summa.items():
            if v is not None:
                new_summaries[k] = v
    summary_text = "\n---\n".join(f"url: {k}\nsummary: {v}" for k, v in new_summaries.items())
    print(summary_text)
    
    content = await conduct(giga_token, topic, summary_text)
    return content
    # for summary in res:
    #     if summary is not None:
    #         print(len(summary))
    #         for i in summary:
    #             print("- ", len(i.inner_text))
    #     else:
    #         print("None")
    
    
# Run the async main function
# asyncio.run(crawler(input("Ваш вопрос: ")))
    
