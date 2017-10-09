import cherrypy
import os
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('html'))
import tabloid_scrapers
from tabloid_scrapers import tabloid_search


class HelloWorld(object):
    @cherrypy.expose
    def index(self):
        data_to_show = ['Hello', 'world']
        tmpl = env.get_template('index.html')
        return tmpl.render(data=data_to_show)

    @cherrypy.expose
    def scrape(self, search_term, num_days_ago):
        try:
            print("---BEGINNING REQUEST---")
            print("User yelp search POST params: %s" %
                  (cherrypy.request.params))
            print("User yelp search POST body: %s" %
                  (cherrypy.request.body.read()))
            url_safe_search_term = search_term.replace(' ', '+')
            scraped_data = tabloid_search.tabloid_search(search_term,
                                             num_days_ago)
            cherrypy.response.headers['Content-Type'] = 'text/plain'
            cherrypy.response.headers[
                'Content-Disposition'] = "attachment; filename='scraped_data.txt'"
            cherrypy.response.headers['Content-Length'] = len(scraped_data)
            return scraped_data
        except Exception as e:
            print("EXCEPTION RAISED WHILE PROCESSING")
            tmpl = env.get_template('error.html')
            error_msg = "Sorry, but something went wrong trying to scrape this request. It's possible that there were no search results for your query, but it's also possible that Dr. Robotnik spilled hydrocholoric acid on the WebProcessor2000 again. We'll look into it!"
            return tmpl.render(error_msg=error_msg)
        finally:
            print("---COMPLETING REQUEST---")


config = {
    'global': {
        'server.socket_host': '0.0.0.0',
        'server.socket_port': int(os.environ.get('PORT', 5000)),
    },
    '/assets': {
        'tools.staticdir.root': os.path.dirname(os.path.abspath(__file__)),
        'tools.staticdir.on': True,
        'tools.staticdir.dir': 'assets',
    }
}

cherrypy.quickstart(HelloWorld(), '/', config=config)