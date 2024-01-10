import copyreg
import io

from lxml import etree


def element_unpickler(data):
    return etree.fromstring(data)


def element_pickler(element):
    data = etree.tostring(element)
    return element_unpickler, (data,)


copyreg.pickle(etree._Element, element_pickler, element_unpickler)


def elementtree_unpickler(data):
    data = io.StringIO(data)
    return etree.parse(data)


def elementtree_pickler(tree):
    data = io.StringIO()
    tree.write(data)
    return elementtree_unpickler, (data.getvalue(),)


copyreg.pickle(etree._ElementTree, elementtree_pickler, elementtree_unpickler)
