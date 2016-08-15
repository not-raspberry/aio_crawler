"""Extracting resources from the bodies."""
import re
from urllib.parse import urlsplit


tag_contents = r'[^<>]'
attr = r'(src|href)'
attr_value = r'''["']?(?P<addr>[^"'>]+)["']?'''
tag_name = r'(a|img|script|link)'
resource = r'<{tag_name}{tag_contents}+{attr}={attr_value}{tag_contents}*>'.format(**globals())
resource_re = re.compile(resource)


def resources_from_tag_soup(soup: str) -> list:
    """
    Extract all resources using regular expressions.

    Why regular expressions rather than BeautifulSoup/lxml or combination thereof?
    Because we don't really need to understand the document structure, tag soup parsing is a mess,
    and a proper parser is orders of magnitude slower than findall with a regular expression.

    Findall is used, rather than finditer, to allow for quick garbage collection of the input
    string.

    :param soup: proper HTML or a tag soup
    :return: a list of resource tuples - (tag_name, attr_name, url),
        e.g. ('a', 'href', '/password')
    """
    return resource_re.findall(soup)


def is_subpage(resource: tuple, site_netloc: str) -> bool:
    """Check if the resource is a sub-page (a page within this site)."""
    tag, attr, url = resource

    if tag != 'a' or attr != 'href':
        return False

    split = urlsplit(url)
    return split.netloc == '' or split.netloc == site_netloc
