"""Testing extracting resources from a tag soup."""
import pytest
from aio_crawler.reader import resources_from_tag_soup


@pytest.mark.parametrize('soup, links', [
    ('', []),
    ('<a href="">', []),
    ('<a href="#">', [('a', 'href', '#')]),
    ('<a href="/link">', [('a', 'href', '/link')]),
    ('<a href="http://a.qq/link?asa=12#2112">', [('a', 'href', 'http://a.qq/link?asa=12#2112')]),
    ('<img src="res.png">', [('img', 'src', 'res.png')]),
    ("<img src='res.png'>", [('img', 'src', 'res.png')]),
    ('<img alt="" src="res.png">', [('img', 'src', 'res.png')]),
    ('<link rel="stylesheet" href="res.css">', [('link', 'href', 'res.css')]),
    ('<script type="application/javascript" src="res.js">', [('script', 'src', 'res.js')]),

    ('   <a     \n\t  href="/link"   >\t\n', [('a', 'href', '/link')]),
    ('<a href="/link"><img src="res.png">', [('a', 'href', '/link'), ('img', 'src', 'res.png')]),
])
def test_resources_from_tag_soup_valid(soup, links):
    """Test extracting valid resources from a tag soup."""
    assert resources_from_tag_soup(soup) == links


@pytest.mark.parametrize('soup', [
    '<img src=res.png>',
    '''<img src='res.png">''',
    '''<img src="res.png'>''',
    '''<img src="res.png" />''',
])
def test_resources_from_tag_soup_invalid(soup):
    """Testing tolerating syntax errors."""
    assert resources_from_tag_soup(soup) == [('img', 'src', 'res.png')]


@pytest.mark.parametrize('soup', [
    'href="/abc"',
    '<img src="/abc"<',
    'a href="/abc"',
])
def test_resources_from_tag_soup_omisions(soup):
    """Test not extracting things that definitely are not resource links."""
    assert resources_from_tag_soup(soup) == []
