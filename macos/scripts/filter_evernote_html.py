#!/usr/bin/python

"""Filter Evernote exported HTML."""

__author__ = "Tom Goetz"
__copyright__ = "Copyright Tom Goetz"
__license__ = "GPL"


import sys
from bs4 import BeautifulSoup
import string


class EvernoteHtmlFilter(object):
    """A class that implements filtering of Evernote exported note HTML."""

    printable = set(string.printable)

    remove_style_attribute_elements_base = [
        'font-family', '-webkit-text-stroke-width', 'letter-spacing', 'font-variant-ligatures', 'flex-basis', 'font-variant-caps',
        'text-indent', 'font-style', 'word-spacing', 'text-align', 'white-space', 'text-transform', 'font-weight'
    ]

    def __init__(self, html):
        """Return a new EvernoteHtmlFilter instance."""
        self.html = filter(lambda x: x in self.printable, html)
        # parse and extract the note body
        self.soup = BeautifulSoup(self.html).find('div', id='en-note')

    def style_element_name(self, style_selement):
        """Return the name of the style element."""
        return style_selement.split(':')[0].lstrip(' ')

    def filter_style_elements(self, style, remove_element_list=[], append_element_dict={}):
        """Filter elements from style attributes."""
        style_list = style.split(';')
        filtered_style = [item for item in style_list if not self.style_element_name(item) in remove_element_list and len(item) > 0]
        for key, value in append_element_dict.iteritems():
            filtered_style.append(' %s: %s'  % (key, value))
        return ';'.join(filtered_style)

    def modify_styles(self, remove_attribute_elements):
        """Modify all style attributes."""
        for tag in self.soup.recursiveChildGenerator():
            if getattr(tag, 'attrs', None) is not None:
                for key, value in tag.attrs.iteritems():
                    if key == 'style':
                        tag.attrs[key] = self.filter_style_elements(value, remove_attribute_elements)

    def modify_tag(self, tag_name, modify_dict={}, add_style_dict={}):
        """Modify tags named tagname with values from a dict."""
        for tag in self.soup.find_all(tag_name):
            for key, value in modify_dict.iteritems():
                tag[key] = value
            tag['style'] = self.filter_style_elements(tag['style'], append_element_dict=add_style_dict)

    def remove_tag(self, tag_name, tag_id):
        """Remove tags named tagname."""
        for tag in self.soup.find_all(tag_name, id=tag_id):
            parent = tag.parent
            subtags = tag.extract().contents
            for subtag in subtags:
                parent.append(subtag)

    def filter(self, table_border=False, table_style_border=False, font_size=False, font_weight=False, table_border_color='black'):
        """Filter the HTML based on settings."""
        border_style = '1px solid %s' % table_border_color
        remove_style_attribute_elements = self.remove_style_attribute_elements_base
        if font_size:
            remove_style_attribute_elements.append('font-size')
        if font_weight:
            remove_style_attribute_elements.append('font-weight')
        if table_border or table_style_border:
            remove_style_attribute_elements.append('border')
        self.modify_styles(remove_style_attribute_elements)
        if table_border:
            self.modify_tag('table', modify_dict={'border': border_style})
        if table_style_border:
            self.modify_tag('table', add_style_dict={'border': border_style})
            self.modify_tag('td', add_style_dict={'border': border_style})

    def __str__(self):
        """Return a string representatin of the filtered output."""
        return str(self.soup)


html_content = ""
for line in sys.stdin:
    html_content = html_content + line

filter = EvernoteHtmlFilter(html_content)
filter.filter(table_style_border=True, table_border_color='gray')

sys.stdout.write(str(filter))
