"""Testing extracting resources from a tag soup."""
import pytest
from aio_crawler.reader import resources_from_tag_soup, is_subpage


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


@pytest.mark.parametrize('resource, result', [
    (('a', 'href', 'http://aaa.com'), True),
    (('a', 'href', ''), True),
    (('a', 'href', '/a/b'), True),
    (('a', 'href', '//aaa.com'), True),
    (('a', 'href', 'https://aaa.com'), True),
    (('a', 'href', 'http://bbb.com'), False),
    (('img', 'src', '/a/b'), False),
    (('link', 'href', '/a/b'), False),
    (('a', 'src', '/a/b'), False),
])
def test_is_subpage(resource, result):
    """Check detecting whether a resource is a document belonging to this page."""
    assert is_subpage(resource, 'aaa.com') == result
