# flake8: noqa
"""Load tools."""
import warnings
from typing import Any, Dict, List, Optional, Callable, Tuple
from mypy_extensions import KwArg

from langchain.agents.tools import Tool
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains.api import news_docs, open_meteo_docs, podcast_docs, tmdb_docs
from langchain.chains.api.base import APIChain
from langchain.chains.llm_math.base import LLMMathChain
from langchain.chains.pal.base import PALChain
from langchain.llms.base import BaseLLM
from langchain.requests import TextRequestsWrapper
from langchain.tools.arxiv.tool import ArxivQueryRun
from langchain.tools.base import BaseTool
from langchain.tools.bing_search.tool import BingSearchRun
from langchain.tools.ddg_search.tool import DuckDuckGoSearchTool
from langchain.tools.google_search.tool import GoogleSearchResults, GoogleSearchRun
from langchain.tools.human.tool import HumanInputRun
from langchain.tools.python.tool import PythonREPLTool
from langchain.tools.requests.tool import (
    RequestsDeleteTool,
    RequestsGetTool,
    RequestsPatchTool,
    RequestsPostTool,
    RequestsPutTool,
)
from langchain.tools.searx_search.tool import SearxSearchResults, SearxSearchRun
from langchain.tools.wikipedia.tool import WikipediaQueryRun
from langchain.tools.wolfram_alpha.tool import WolframAlphaQueryRun
from langchain.utilities import ArxivAPIWrapper
from langchain.utilities.apify import ApifyWrapper
from langchain.utilities.bash import BashProcess
from langchain.utilities.bing_search import BingSearchAPIWrapper
from langchain.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from langchain.utilities.google_search import GoogleSearchAPIWrapper
from langchain.utilities.google_serper import GoogleSerperAPIWrapper
from langchain.utilities.searx_search import SearxSearchWrapper
from langchain.utilities.serpapi import SerpAPIWrapper
from langchain.utilities.wikipedia import WikipediaAPIWrapper
from langchain.utilities.wolfram_alpha import WolframAlphaAPIWrapper


def _get_python_repl() -> BaseTool:
    return PythonREPLTool()


def _get_tools_requests_get() -> BaseTool:
    return RequestsGetTool(requests_wrapper=TextRequestsWrapper())


def _get_tools_requests_post() -> BaseTool:
    return RequestsPostTool(requests_wrapper=TextRequestsWrapper())


def _get_tools_requests_patch() -> BaseTool:
    return RequestsPatchTool(requests_wrapper=TextRequestsWrapper())


def _get_tools_requests_put() -> BaseTool:
    return RequestsPutTool(requests_wrapper=TextRequestsWrapper())


def _get_tools_requests_delete() -> BaseTool:
    return RequestsDeleteTool(requests_wrapper=TextRequestsWrapper())


def _get_terminal() -> BaseTool:
    return Tool(
        name="Terminal",
        description="Executes commands in a terminal. Input should be valid commands, and the output will be any output from running that command.",
        func=BashProcess().run,
    )


_BASE_TOOLS = {
    "python_repl": _get_python_repl,
    "requests": _get_tools_requests_get,  # preserved for backwards compatability
    "requests_get": _get_tools_requests_get,
    "requests_post": _get_tools_requests_post,
    "requests_patch": _get_tools_requests_patch,
    "requests_put": _get_tools_requests_put,
    "requests_delete": _get_tools_requests_delete,
    "terminal": _get_terminal,
}


def _get_pal_math(llm: BaseLLM) -> BaseTool:
    return Tool(
        name="PAL-MATH",
        description="A language model that is really good at solving complex word math problems. Input should be a fully worded hard word math problem.",
        func=PALChain.from_math_prompt(llm).run,
    )


def _get_pal_colored_objects(llm: BaseLLM) -> BaseTool:
    return Tool(
        name="PAL-COLOR-OBJ",
        description="A language model that is really good at reasoning about position and the color attributes of objects. Input should be a fully worded hard reasoning problem. Make sure to include all information about the objects AND the final question you want to answer.",
        func=PALChain.from_colored_object_prompt(llm).run,
    )


def _get_llm_math(llm: BaseLLM) -> BaseTool:
    return Tool(
        name="Calculator",
        description="Useful for when you need to answer questions about math.",
        func=LLMMathChain(llm=llm, callback_manager=llm.callback_manager).run,
        coroutine=LLMMathChain(llm=llm, callback_manager=llm.callback_manager).arun,
    )


def _get_open_meteo_api(llm: BaseLLM) -> BaseTool:
    chain = APIChain.from_llm_and_api_docs(llm, open_meteo_docs.OPEN_METEO_DOCS)
    return Tool(
        name="Open Meteo API",
        description="Useful for when you want to get weather information from the OpenMeteo API. The input should be a question in natural language that this API can answer.",
        func=chain.run,
    )


_LLM_TOOLS = {
    "pal-math": _get_pal_math,
    "pal-colored-objects": _get_pal_colored_objects,
    "llm-math": _get_llm_math,
    "open-meteo-api": _get_open_meteo_api,
}


def _get_news_api(llm: BaseLLM, **kwargs: Any) -> BaseTool:
    news_api_key = kwargs["news_api_key"]
    chain = APIChain.from_llm_and_api_docs(
        llm, news_docs.NEWS_DOCS, headers={"X-Api-Key": news_api_key}
    )
    return Tool(
        name="News API",
        description="Use this when you want to get information about the top headlines of current news stories. The input should be a question in natural language that this API can answer.",
        func=chain.run,
    )


def _get_tmdb_api(llm: BaseLLM, **kwargs: Any) -> BaseTool:
    tmdb_bearer_token = kwargs["tmdb_bearer_token"]
    chain = APIChain.from_llm_and_api_docs(
        llm,
        tmdb_docs.TMDB_DOCS,
        headers={"Authorization": f"Bearer {tmdb_bearer_token}"},
    )
    return Tool(
        name="TMDB API",
        description="Useful for when you want to get information from The Movie Database. The input should be a question in natural language that this API can answer.",
        func=chain.run,
    )


def _get_podcast_api(llm: BaseLLM, **kwargs: Any) -> BaseTool:
    listen_api_key = kwargs["listen_api_key"]
    chain = APIChain.from_llm_and_api_docs(
        llm,
        podcast_docs.PODCAST_DOCS,
        headers={"X-ListenAPI-Key": listen_api_key},
    )
    return Tool(
        name="Podcast API",
        description="Use the Listen Notes Podcast API to search all podcasts or episodes. The input should be a question in natural language that this API can answer.",
        func=chain.run,
    )


def _get_wolfram_alpha(**kwargs: Any) -> BaseTool:
    return WolframAlphaQueryRun(api_wrapper=WolframAlphaAPIWrapper(**kwargs))


def _get_google_search(**kwargs: Any) -> BaseTool:
    return GoogleSearchRun(api_wrapper=GoogleSearchAPIWrapper(**kwargs))


def _get_wikipedia(**kwargs: Any) -> BaseTool:
    return WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(**kwargs))


def _get_arxiv(**kwargs: Any) -> BaseTool:
    return ArxivQueryRun(api_wrapper=ArxivAPIWrapper(**kwargs))


def _get_google_serper(**kwargs: Any) -> BaseTool:
    return Tool(
        name="Serper Search",
        func=GoogleSerperAPIWrapper(**kwargs).run,
        description="A low-cost Google Search API. Useful for when you need to answer questions about current events. Input should be a search query.",
    )


def _get_google_search_results_json(**kwargs: Any) -> BaseTool:
    return GoogleSearchResults(api_wrapper=GoogleSearchAPIWrapper(**kwargs))


def _get_serpapi(**kwargs: Any) -> BaseTool:
    return Tool(
        name="Search",
        description="A search engine. Useful for when you need to answer questions about current events. Input should be a search query.",
        func=SerpAPIWrapper(**kwargs).run,
        coroutine=SerpAPIWrapper(**kwargs).arun,
    )


def _get_searx_search(**kwargs: Any) -> BaseTool:
    return SearxSearchRun(wrapper=SearxSearchWrapper(**kwargs))


def _get_searx_search_results_json(**kwargs: Any) -> BaseTool:
    wrapper_kwargs = {k: v for k, v in kwargs.items() if k != "num_results"}
    return SearxSearchResults(wrapper=SearxSearchWrapper(**wrapper_kwargs), **kwargs)


def _get_bing_search(**kwargs: Any) -> BaseTool:
    return BingSearchRun(api_wrapper=BingSearchAPIWrapper(**kwargs))


def _get_ddg_search(**kwargs: Any) -> BaseTool:
    return DuckDuckGoSearchTool(api_wrapper=DuckDuckGoSearchAPIWrapper(**kwargs))


def _get_human_tool(**kwargs: Any) -> BaseTool:
    return HumanInputRun(**kwargs)


_EXTRA_LLM_TOOLS = {
    "news-api": (_get_news_api, ["news_api_key"]),
    "tmdb-api": (_get_tmdb_api, ["tmdb_bearer_token"]),
    "podcast-api": (_get_podcast_api, ["listen_api_key"]),
}

_EXTRA_OPTIONAL_TOOLS: Dict[str, Tuple[Callable[[KwArg(Any)], BaseTool], List[str]]] = {
    "wolfram-alpha": (_get_wolfram_alpha, ["wolfram_alpha_appid"]),
    "google-search": (_get_google_search, ["google_api_key", "google_cse_id"]),
    "google-search-results-json": (
        _get_google_search_results_json,
        ["google_api_key", "google_cse_id", "num_results"],
    ),
    "searx-search-results-json": (
        _get_searx_search_results_json,
        ["searx_host", "engines", "num_results", "aiosession"],
    ),
    "bing-search": (_get_bing_search, ["bing_subscription_key", "bing_search_url"]),
    "ddg-search": (_get_ddg_search, []),
    "google-serper": (_get_google_serper, ["serper_api_key"]),
    "serpapi": (_get_serpapi, ["serpapi_api_key", "aiosession"]),
    "searx-search": (_get_searx_search, ["searx_host", "engines", "aiosession"]),
    "wikipedia": (_get_wikipedia, ["top_k_results", "lang"]),
    "human": (_get_human_tool, ["prompt_func", "input_func"]),
}


def load_tools(
    tool_names: List[str],
    llm: Optional[BaseLLM] = None,
    callback_manager: Optional[BaseCallbackManager] = None,
    **kwargs: Any,
) -> List[BaseTool]:
    """Load tools based on their name.

    Args:
        tool_names: name of tools to load.
        llm: Optional language model, may be needed to initialize certain tools.
        callback_manager: Optional callback manager. If not provided, default global callback manager will be used.

    Returns:
        List of tools.
    """
    tools = []

    for name in tool_names:
        if name == "requests":
            warnings.warn(
                "tool name `requests` is deprecated - "
                "please use `requests_all` or specify the requests method"
            )

        if name == "requests_all":
            # expand requests into various methods
            requests_method_tools = [
                _tool for _tool in _BASE_TOOLS if _tool.startswith("requests_")
            ]
            tool_names.extend(requests_method_tools)
        elif name in _BASE_TOOLS:
            tools.append(_BASE_TOOLS[name]())
        elif name in _LLM_TOOLS:
            if llm is None:
                raise ValueError(f"Tool {name} requires an LLM to be provided")
            tool = _LLM_TOOLS[name](llm)
            if callback_manager is not None:
                tool.callback_manager = callback_manager
            tools.append(tool)
        elif name in _EXTRA_LLM_TOOLS:
            if llm is None:
                raise ValueError(f"Tool {name} requires an LLM to be provided")
            _get_llm_tool_func, extra_keys = _EXTRA_LLM_TOOLS[name]
            missing_keys = set(extra_keys).difference(kwargs)
            if missing_keys:
                raise ValueError(
                    f"Tool {name} requires some parameters that were not "
                    f"provided: {missing_keys}"
                )
            sub_kwargs = {k: kwargs[k] for k in extra_keys}
            tool = _get_llm_tool_func(llm=llm, **sub_kwargs)
            if callback_manager is not None:
                tool.callback_manager = callback_manager
            tools.append(tool)
        elif name in _EXTRA_OPTIONAL_TOOLS:
            _get_tool_func, extra_keys = _EXTRA_OPTIONAL_TOOLS[name]
            sub_kwargs = {k: kwargs[k] for k in extra_keys if k in kwargs}
            tool = _get_tool_func(**sub_kwargs)
            if callback_manager is not None:
                tool.callback_manager = callback_manager
            tools.append(tool)
        else:
            raise ValueError(f"Got unknown tool {name}")
    return tools


def get_all_tool_names() -> List[str]:
    """Get a list of all possible tool names."""
    return (
        list(_BASE_TOOLS)
        + list(_EXTRA_OPTIONAL_TOOLS)
        + list(_EXTRA_LLM_TOOLS)
        + list(_LLM_TOOLS)
    )
