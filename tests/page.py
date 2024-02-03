"""
pset subclass that works as a django template context.
"""
import pickle

from django.core.exceptions import ImproperlyConfigured

from urllib.parse import unquote, quote
import uuid
import weakref

from django.conf import settings


def get_context_processors():
    """Get context processors in a way that works for Django 1.7 and 1.8+
       (from https://programtalk.com/vs2/python/8755/django-session-csrf/session_csrf/tests.py/)
    """
    try:
        from django.template.engine import Engine
        engine = Engine.get_default()
    except ImproperlyConfigured:
        return []
    return engine.template_context_processors


class pset(dict):
    """This code is placed in the Public Domain, or released under the
       wtfpl (http://sam.zoy.org/wtfpl/COPYING) wherever PD is problematic.

       Property Set class.
       A property set is an object where values are attached to attributes,
       but can still be iterated over as key/value pairs.
       The order of assignment is maintained during iteration.
       Only one value allowed per key.

         >>> x = pset()
         >>> x.a = 42
         >>> x.b = 'foo'
         >>> x.a = 314
         >>> x
         pset(a=314, b='foo')

    """
    def __init__(self, items=(), **attrs):
        object.__setattr__(self, '_order', [])
        super().__init__()
        for k, v in self._get_iterator(items):
            self._add(k, v)
        for k, v in attrs.items():
            self._add(k, v)

    def __json__(self):
        return dict(self.items())

    def _add(self, key, value):
        "Add key->value to client vars."
        if type(key) in (int,):
            key = self._order[key]
        elif key not in self._order:
            self._order.append(key)
        dict.__setitem__(self, key, value)

    def apply(self, fn):
        "Apply function ``fn`` to all values in self."
        object.__setattr__(self, '_order', [])
        for k, v in self:
            self[k] = fn(v)

    def remove(self, key):
        "Remove key from client vars."
        if type(key) in (int,):
            key = self._order[key]
            del self._order[key]
        elif key in self._order:
            self._order.remove(key)
        dict.__delitem__(self, key)

    def __eq__(self, other):
        """Equal iff they have the same set of keys, and the values for
           each key is equal. Key order is not considered for equality.
        """
        if other is None:
            return False
        if set(self._order) == set(other._order):  # pylint: disable=W0212
            return all(self[key] == other[key] for key in self._order)
        return False

    def _get_iterator(self, val):
        if not val:
            return []
        if isinstance(val, pset) or not isinstance(val, dict):
            return val
        else:
            return val.items()

    def __iadd__(self, other):
        for k, v in self._get_iterator(other):
            self._add(k, v)
        return self

    def __add__(self, other):
        "self + other"
        tmp = self.__class__()
        tmp += self
        tmp += other
        return tmp

    def __radd__(self, other):
        "other + self"
        tmp = self.__class__()
        for k, v in other.items():
            tmp[k] = v
        tmp += self
        return tmp

    def __neg__(self):
        "Reverse keys and values."
        return self.__class__((v, k) for (k, v) in self.items())

    def _name(self):
        return self.name if 'name' in self else self.__class__.__name__

    def __str__(self):
        vals = []
        for k, v in self:
            if k != 'name':
                try:
                    vals.append(f'{k}={repr(v)}')
                except Exception:
                    vals.append(f'{k}=UNPRINTABLE')

        vals = ', '.join(vals)

        return f'{self._name()}({vals})'

    __repr__ = __str__

    def __getattr__(self, key):
        if not super().__contains__(key):
            raise AttributeError(key)
        return dict.get(self, key)

    def __getitem__(self, key):
        if type(key) in (int,):
            key = self._order[key]
        return dict.get(self, key)

    def __delattr__(self, key):
        if key in self:
            self.remove(key)

    def __delitem__(self, key):
        if key in self:
            self.remove(key)

    def __iter__(self):
        return ((k, dict.get(self, k)) for k in self._order)

    def items(self):
        return iter(self)

    def values(self):
        return [dict.get(self, k) for k in self._order]

    def keys(self):
        return self._order

    def __setattr__(self, key, val):
        # assert key not in self._reserved, key
        if key.startswith('_'):
            object.__setattr__(self, key, val)
        else:
            self._add(key, val)

    def __setitem__(self, key, val):
        self._add(key, val)

    def update(self, dct):
        """Update self from dct.
        """
        for k, v in dct.items():
            self._add(k, v)
        return self


class Forms(pset):
    """A descriptor that makes a page (below) and its forms, mutually
       'self'-aware.  Needed by the forms templates to manage the csrf
       token.
    """
    def __get__(self, pageclass, owner):
        if pageclass is None:
            raise AttributeError('forms is an instance...')
        self.page = pageclass  # pylint:disable=W0201
        return self

    def __iter__(self):
        return iter(self.values())


class _deferred:
    def __init__(self, fn, *args):
        self.fn = fn
        self.args = args

    def __call__(self):
        return self.fn(*self.args)
    

class pageproperty:
    """`@property`-like decorator for properties on sub-classes of page.
    """
    def __init__(self, get):
        self.get = get
        if hasattr(get, '__doc__'):
            self.__doc__ = get.__doc__

    def __get__(self, pageobj, pageclass=None):
        if pageobj is None:
            return self
        return self.get(pageobj)


class deferred:
    """Decorator that doesn't evaluate the property until template evaluation
       and in such a way that the property is only evaluated once for each
       mention in the template.
       Not suitable for use in view code.
    """
    def __init__(self, get):
        # print("DEFERRED::init", get.__name__, dir(get))
        self.get = get
        if hasattr(get, '__doc__'):
            self.__doc__ = get.__doc__

    def __get__(self, pageobj, pageclass=None):
        if pageobj is None:
            return self
        return _deferred(self.get, pageobj)


class cached:
    """Decorator that creates a property who's method is only evaluated
       once. Great for properties that would otherwise hit the database
       at declaration time.

       Obviously not suitable for dynamic properties (properties who's
       values change during the life time of a view).
    """
    def __init__(self, get):
        # print "CACHED", get.__name__, dir(get)
        # print("cached init", get.__name__, dir(get))
        self.get = get
        if hasattr(get, '__doc__'):
            self.__doc__ = get.__doc__

    def __get__(self, pageobj, pageclass=None):
        # print "CACHED/get", self.get.__name__
        if pageobj is None:
            return self
        if not hasattr(self, '_value'):
            self._value = self.get(pageobj)
        return self._value

    def __set__(self, obj, val):
        # print 'setting...'
        self._value = val
        return self


class Page(pset):
    """The ``page`` class is used as a container for variables a view
       function wants to pass on to the template.  Idiomatic usage::
           
           from dkdjango.page import Page
           def myview(request, ...):
               page = Page(request)
               ...
               return dkhttp.render_to_response('template.html', page)

       when django renders a template variable it first calls

           page.__contains__(variable)

       and if that returns true it calls

           page.__getitem__(variable)

       (if that doesn't suceed it will continue..)

       page must not be completely empty.

    """
    forms = Forms()  # all the forms on the page
    
    def __init__(self, request, username=None, grab=(), **kwargs):
        super().__init__(**kwargs)

        # If path is funky (i.e. it contains GET parameters that aren't
        # ascii), then we ought to redirect to self.full_path.
        # Otherwise the GET variables will contain \ufffd characters.
        # FF and IE do this in subtly different ways, so test thoroughly
        # if changing any of this :-)
        # Note: normally we would never have GET parameters that we don't
        #       control, so this is hardly ever a real problem...
        rmqs = request.META.get('QUERY_STRING')
        querystring = unquote(rmqs or '')
        qquery = quote(querystring, '=&')

        fullpath = request.path
        funky = False
        if querystring:
            funky = querystring != querystring
            if not isinstance(qquery, bytes):
                qquery = qquery.encode('u8')
            fullpath += b'?' + qquery
        
        for v in grab:
            self[v] = request.GET.get(v)

        # set a number of common variables in the environment.
        # use dictionary syntax to prevent infinite recursion in
        # __setattr__
        # self['user'] = getattr(request, 'user', None)
        self['path'] = request.path   # XXX: hmm.. u8?
        self['full_path'] = fullpath
        self['funky_path'] = funky
        self['session'] = request.session if hasattr(request, 'session') else {}
        self['method'] = request.method
        self['COOKIES'] = request.COOKIES
        self['LANGUAGE_CODE'] = getattr(request, 'LANGUAGE_CODE', None)
        self['DEBUG'] = settings.DEBUG
        self['debug'] = settings.DEBUG
        
        self['is_post'] = self['method'] == 'POST'
        self['is_get'] = self['method'] == 'GET'
        self['request'] = request
        self['page_secret_selfref'] = weakref.proxy(self)  # don't create cycle
        self['uuid'] = str(uuid.uuid1())
        self._predefined = []

        for processor in get_context_processors():
            self.update(processor(request))

        # in addition to the manual mark operation, we also need to know
        # the initial state (e.g. for to_dict())
        object.__setattr__(self, '_initial_page_state', self._order[:])
        self.mark()
        # self._predefined = self._order[:]  # shallow copy of known names

    # @cached
    def user(self):
        "Hits the User table."
        # print "USER:"
        return getattr(self.request, 'user', None)

    def god_mode(self):
        try:
            return self.user().username in settings.GODS
        except:  # noqa
            return False

    def demigod_mode(self):
        try:
            return self.user().username in settings.DEMIGODS
        except:  # noqa
            return False

    def __getattr__(self, key):
        return super().__getattr__(key)

    def __setattr__(self, key, val):
        if key.startswith('_'):
            object.__setattr__(self, key, val)
        else:
            if self._ownsattr(key):
                object.__setattr__(self, key, val)

            if hasattr(val, 'is_form') and getattr(val, 'is_form', False):
                self.forms[key] = val

            self._add(key, val)

    def _ownsattr(self, attr):
        """When called from a subclass, this returns true iff the `attr` is
           defined on the subclass (ie. is not a method defined on
           :class:`dkdjango.page.Page`.
        """
        return hasattr(self, attr) and not hasattr(super(), attr)

    def __contains__(self, key):
        return super().__contains__(key) or self._ownsattr(key)

    def __getitem__(self, key):
        if self._ownsattr(key):
            return getattr(self, key)
        elif super().__contains__(key):
            return super().__getitem__(key)
        else:
            raise KeyError("Unknown key: %r" % key)

    def mark(self, persist=False):
        "Mark currently known item keys."
        if persist:
            self._predefined = self._order[:]  # shallow copy of known names
        return self._order[:]

    def to_dict(self, include_page_state=False):
        """Return a dict of the variables set on the page.
        """
        res = {}
        for var in self._order:
            if include_page_state or var not in self._initial_page_state:
                res[var] = self[var]
        return res

    def viewstate(self, mark=None):
        """Return viewstate from ``mark``.
           Viewstate ::= variables/values that have been defined on page.
        """
        state = {}
        skiplist = set(mark or self._predefined)

        def can_pickle(var, val):
            "Is the variable/value picleable?"
            
            if var in ('request', 'session', 'page_secret_selfref', 'dkhttp', 'cms_menu_renderer', 'debug', 'cms_settings'):
                return False

            if var == 'messages' and 'FallbackStorage' in str(type(val)):
                return False
            
            if not hasattr(val, '__dict__'):
                # all basic types (int, str, etc.) are pickleable
                return True

            if hasattr(val, '__getstate__'):
                print('{} [{}] has __getstate__'.format(var, type(val)))
                return True

            # pylint:disable=W0212
            if hasattr(val, '_can_pickle'):
                print('{}._can_pickle = {!r}'.format(var, val._can_pickle))
                return val._can_pickle
            
            try:
                pickleable = val == pickle.loads(pickle.dumps(val))
                print(
                    'checking {} [{}]: {!r}'.format(var, type(val), pickleable))
                
                if not pickleable:
                    print(
                        ' '.join("""
                           Variable [%s] of type [%s] doesn't raise a
                           TypeError when pickled, but the value is
                           not __eq__ to the roundtripped value.
                        """.split()) % (var, type(val)))
                    
                return pickleable
            
            except AttributeError as e:
                print(str(e))
                return False

            except TypeError:
                # only issue warning if we had to manually test picleability.
                msg = ' '.join("""
                    Variable [%s] of type [%s] is not pickleable.
                    You can remove this warning by setting the attribute
                    _can_pickle to False on the object.
                    """.split())
                print(msg % (var, type(val)), exc_info=1)
                return False
            
        for var in self._order:
            if var not in skiplist:
                val = self[var]

                if can_pickle(var, val):
                    state[var] = val
                else:
                    print(' '.join(
                        """Variable %s [%s] will not be part of the
                           viewstate because it can't be pickled.
                           Turn loglevel to logging.DEBUG to see why.
                           """.split()) % (var, type(val)))
                
        return state

    def fetch_view_vars(self):
        """WARNING: security risk!
        
           Return a list of pset(name, value) objects for all
           properties added after ``__init__``.  This will typically
           be the variables the view has added (hence the name).

           This function is useful when the template needs to capture its
           (the view's) context and pass it on in an ajax call.

           You can get at it from a template tag::

               page = template.Variable('page').resolve(ctx)
               ctx['view_vars'] = page.fetch_view_vars()
               
        """
        res = []
        for var in self._order:
            if var not in self._predefined:
                val = self[var]
                if hasattr(val, '__dict__'):
                    if hasattr(val, '__json__'):
                        res.append(pset(name=var, value=val.__json__()))
                    else:
                        pass  # general case is not safe.
                else:
                    res.append(pset(name=var, value=val))
        return res

    def debug_print(self, skip=('META', 'COOKIES', 'request', 'page_secret_selfref')):
        keylen = max([len(k) for k in self._order])
        print('Page contents (except keys: %s)' % list(skip))
        print('-' * 75)
        for var in self._order:
            if var not in skip:
                val = self[var]
                print('%*s: %s' % (keylen, var, val))


page = Page