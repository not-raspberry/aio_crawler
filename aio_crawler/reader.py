"""Extracting resources from the bodies."""
import re
from urllib.parse import urlsplit, urlunsplit, urljoin


tag_contents = r'[^<>]'
attr = r'(src|href)'
attr_value = r'''["']?(?P<addr>[^"'>]+)["']?'''
tag_name = r'(a|img|script|link)'
resource = r'<{tag_name}{tag_contents}+{attr}={attr_value}{tag_contents}*>'.format(**globals())
resource_re = re.compile(resource)


def resources_from_tag_soup(soup: str, base_url: str) -> tuple:
    """
    Extract all resources using regular expressions.

    Why regular expressions rather than BeautifulSoup/lxml or combination thereof?
    Because we don't really need to understand the document structure, tag soup parsing is a mess,
    and a proper parser is orders of magnitude slower than findall with a regular expression.

    :param soup: proper HTML or a tag soup
    :return: a set of links and a set of resource URLs
    """
    resources = set()
    links = set()
    for match in resource_re.finditer(soup):
        tag, attr, attr_value = match.groups()
        if attr_value.startswith('javascript:'):
            continue

        url = normalize_url(attr_value, base_url)
        resources.add(url)
        if is_subpage(tag, attr, url, base_url):
            links.add(url)

    return links, resources


def normalize_url(url: str, base_url: str) -> str:
    """Make the url absolute, with no trailing slash and no fragment part."""
    absolute = urljoin(base_url, url)
    split = urlsplit(absolute)
    return urlunsplit(
        (split.scheme, split.netloc, split.path, split.query, '')
    ).rstrip('/')


def is_subpage(tag: str, attr: str, url: str, base_url: str) -> bool:
    """Check if the resource is a sub-page (a page within this site)."""
    return (tag == 'a' and
            attr == 'href' and
            urlsplit(url).netloc == urlsplit(base_url).netloc)
