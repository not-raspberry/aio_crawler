"""Testing extracting resources from a tag soup."""
import pytest
from aio_crawler.reader import resources_from_tag_soup, normalize_url, is_subpage


@pytest.mark.parametrize('soup, links, resources', [
    ('', set(), set()),
    ('<a href="">', set(), set()),
    ('<a href="#">', {'http://a.qq'}, {'http://a.qq'}),
    ('<a href="/link">', {'http://a.qq/link'}, {'http://a.qq/link'}),
    ('<a href="http://a.qq/link?asa=12#2112">',
     {'http://a.qq/link?asa=12'}, {'http://a.qq/link?asa=12'}),
    ('<img src="res.png">', set(), {'http://a.qq/res.png'}),
    ("<img src='res.png'>", set(), {'http://a.qq/res.png'}),
    ('<img alt="" src="res.png">', set(), {'http://a.qq/res.png'}),
    ('<link rel="stylesheet" href="res.css">', set(), {'http://a.qq/res.css'}),
    ('<script type="application/javascript" src="res.js">', set(), {'http://a.qq/res.js'}),
    ('   <a     \n\t  href="/link"   >\t\n', {'http://a.qq/link'}, {'http://a.qq/link'}),
    ('<a href="/link"><img src="res.png">',
     {'http://a.qq/link'}, {'http://a.qq/link', 'http://a.qq/res.png'})
])
def test_resources_from_tag_soup_valid(soup, links, resources):
    """Test extracting valid resources from a tag soup."""
    assert resources_from_tag_soup(soup, 'http://a.qq') == (links, resources)


@pytest.mark.parametrize('soup', [
    '<a href=res.html>',
    '''<a href='res.html">''',
    '''<a href="res.html'>''',
    '''<a href="res.html" />''',
])
def test_resources_from_tag_soup_invalid(soup):
    """Testing tolerating syntax errors."""
    assert resources_from_tag_soup(soup, 'https://c.ca/') == (
        {'https://c.ca/res.html'}, {'https://c.ca/res.html'}
    )


@pytest.mark.parametrize('soup', [
    'href="/abc"',
    '<img src="/abc"<',
    'a href="/abc"',
])
def test_resources_from_tag_soup_omisions(soup):
    """Test not extracting things so broken that they are definitely not resource links."""
    assert resources_from_tag_soup(soup, base_url='http://a.cc') == (set(), set())


@pytest.mark.parametrize('url, base_url, result', [
    ('http://a.com/', 'http://b.com/', 'http://a.com'),
    ('https://a.com/', 'http://a.com/', 'https://a.com'),
    ('/a/b', 'http://b.com/', 'http://b.com/a/b'),
    ('../../../aa', 'http://b.com/path/path/path', 'http://b.com/aa'),
    ('/a/b?q=1#asda', 'http://b.com/', 'http://b.com/a/b?q=1'),
])
def test_normalize_url(url, base_url, result):
    """Test normalizing urls."""
    assert normalize_url(url, base_url) == result


@pytest.mark.parametrize('tag, attr, normalized_url, result', [
    ('a', 'href', 'http://aaa.com', True),
    ('a', 'href', 'http://aaa.com/a/b', True),
    ('a', 'href', '//aaa.com', True),
    ('a', 'href', 'https://aaa.com', True),
    ('a', 'href', 'http://bbb.com', False),
    ('img', 'src', 'http://aaa.com/a/b', False),
    ('link', 'href', 'http://aaa.com/a/b', False),
    ('a', 'src', 'http://aaa.com/a/b', False),
])
def test_is_subpage(tag, attr, normalized_url, result):
    """Check detecting whether a resource is a document belonging to this page."""
    assert is_subpage(tag, attr, normalized_url, 'http://aaa.com') == result
