from tr_climate.bing_news_fetch import unwrap_news_redirect_url


def test_unwrap_bing_apiclick_extracts_publisher_url() -> None:
    href = (
        "http://www.bing.com/news/apiclick.aspx?ref=FexRss&aid=&tid=x"
        "&url=https%3a%2f%2fwww.ntv.com.tr%2fgundem%2farticle-1"
        "&c=1&mkt=tr-tr"
    )
    assert unwrap_news_redirect_url(href) == "https://www.ntv.com.tr/gundem/article-1"


def test_unwrap_passes_through_direct_url() -> None:
    u = "https://www.haberturk.com/haber/abc"
    assert unwrap_news_redirect_url(u) == u
