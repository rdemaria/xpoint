import re


class ProxyDict(dict):
    def __init__(self, *args, **kwargs):
        self._proxy = {}
        super().__init__(*args, **kwargs)

    def __missing__(self, key):
        return self._proxy[key]
 
    def __contains__(self, key):
        return key in self._proxy or super().__contains__(key)

    def __iter__(self):
        return iter(set(self._proxy.keys()) | set(super().keys()))

    def __len__(self):
        return len(set(self._proxy.keys()) | set(super().keys()))

    def set_proxy(self, proxy):
        self._proxy=proxy
        return self


def apply_style(primitive, style):
    """Apply style to primitive

    A style dictionary is a dict, where the keys are style properties or selectors and the values are dicts of style properties.

    A selector is a string that starts with a character that determines the type of selector, followed by a string that is used to match the selector. The following selectors are supported:

    * ``.``: Match the class name of the primitive
    * ``#``: Match the name of the primitive
    * ``~``: Match the name of the primitive using a regular expression

    The following style properties are supported:

    * ``color``: The color of the primitive
    * ``linewidth``: The width of the line
    * ``linestyle``: The style of the line
    * ``marker``: The marker of the primitive
    * ``markersize``: The size of the marker
    * ``alpha``: The transparency of the primitive
    * ``label``: The label of the primitive
    * ``visible``: Whether the primitive is visible
    * ``zorder``: The z-order of the primitive
    * ``facecolor``: The face color of the primitive
    * ``edgecolor``: The edge color of the primitive
    * ``facealpha``: The face transparency of the primitive
    * ``edgealpha``: The edge transparency of the primitive
    * ``hatch``: The hatch of the primitive
    * ``fill``: Whether the primitive is filled
    * ``capstyle``: The cap style of the primitive
    * ``joinstyle``: The join style of the primitive
    * ``antialiased``: Whether the primitive is antialiased
    * ``dash_capstyle``: The cap style of the dash
    * ``solid_capstyle``: The cap style of the solid
    * ``dash_joinstyle``: The join style of the dash
    * ``solid_joinstyle``: The join style of the solid
    """
    result={}
    if style is not None:
        for k, v in style.items():
            if isinstance(v, dict): # k is a selector
                kdata=k[1:]
                if k[0]=='.' and primitive.__class__.__name__==kdata:
                        result.update(apply_style(v))
                elif k[0]=='#' and primitive.name==kdata:
                        result.update(apply_style(v))
                elif k[0]=='~' and isinstance(primitive.name,str) and re.match(kdata,primitive.name):
                        result.update(apply_style(v))
            else:
                result[k]=v
    return result