import enum
from dataclasses import dataclass
import shutil

class PageAccess(enum.Enum):
    USER_ONLY   = 1
    GUEST_ONLY  = 2
    USER_GUEST  = 3

class Page:
    def __init__(self, name, filename_guest, filename_user, access):
        def get_content(pathname):
            if pathname == None:
                return None
            with open(pathname) as f:
                return f.read()
        self.name = name
        self.filename_guest = filename_guest
        self.filename_user = filename_user
        self.access = access
        self.contents_guest = get_content(filename_guest)
        self.contents_user  = get_content(filename_user)

    def get_contents(self, access):
        if access == PageAccess.USER_ONLY:
            return self.contents_user
        elif access == PageAccess.GUEST_ONLY:
            return self.contents_guest
        else:
            print("Wrong access passed")
            return ""

PAGE_DIR = "templates/"
pagetab = {
    "index.html"    : Page("Home",      PAGE_DIR + "index.html",    PAGE_DIR + "index_user.html", PageAccess.USER_GUEST),
    "about.html"    : Page("About",     PAGE_DIR + "about.html",    PAGE_DIR + "about.html",      PageAccess.USER_GUEST),
    "login.html"    : Page("Login",     PAGE_DIR + "login.html",    None,                         PageAccess.GUEST_ONLY),
    "getkr.html"    : Page("Play",      None,                       PAGE_DIR + "getkr.html",      PageAccess.USER_ONLY),
    "shop.html"     : Page("Shop",      None,                       PAGE_DIR + "shop.html",       PageAccess.USER_ONLY),
    "stats.html"    : Page("See stats", None,                       PAGE_DIR + "stats.html",      PageAccess.USER_ONLY),
}

def load_page_cached(url):
    global cache
    cache = {}
    if url not in cache:
        with open(PAGE_DIR + url, "r") as f:
            cache[url] = f.read()
    return cache[url]

def copy_page(url):
    shutil.copyfile(PAGE_DIR + url, url)

HEAD_TEMPLATE = load_page_cached("head.html")

def make_div(divclass, content):
    return "<div class=\"" + divclass + "\">\n" + content + "\n</div>"

def make_sidebar(access):
    sidebar = ""
    for url in pagetab:
        page = pagetab[url]
        if page.access.value & access.value:
            sidebar += "<a href=\"/" + url + "\">" + pagetab[url].name + "</a>\n"
    return sidebar

# Create a dynamic page.
#   url: name of the dynamic page, should end with .html.
#   username: name of the user that is accessing, or None for a "guest" user.
# If the user doesn't have access to the page (for example, a guest visiting a
# page only visitable by a user), then the function returns false.
def create_page(url, username):
    def logged_user_message(username):
        if username == None:
            return ""
        return "<footer>Logged in as " + username + "</footer>"

    if url not in pagetab:
        return
    access = PageAccess.GUEST_ONLY if username == None else PageAccess.USER_ONLY
    page = pagetab[url]
    page_content = page.get_contents(access)
    if page_content == None:
        return False

    with open(url, "w") as out:
        def wr(s): out.write(s + '\n')
        wr("<html>")
        wr("    </head>")
        wr("    <title>Krunker Store: " + page.name + "</title>")
        wr(HEAD_TEMPLATE)
        wr("    </head>")
        wr("    <body>")
        wr(make_div("sidenav", make_sidebar(access)))
        wr(make_div("main", page_content))
        wr(make_div("foot", logged_user_message(username)))
        wr("    </body>")
        wr("</html>")

    return True

