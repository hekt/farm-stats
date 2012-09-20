#! /usr/local/env python
# -*- coding:utf-8 -*-

import sys
sys.path.append("./")
import os

# use Django 1.2
from google.appengine.dist import use_library
use_library('django', '1.2')

# Google App Engine libraries
from google.appengine.api import memcache, urlfetch
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from django.utils import simplejson as json


class LatestStats(db.Model):
    team = db.StringProperty()
    stats_kind = db.StringProperty()
    stats = db.TextProperty()

    
class Manage(db.Model):
    date = db.DateProperty()
    digest = db.TextProperty()
    game_count = db.TextProperty()


class Results(object):
    def buildStats(self, team, stats_kind):
        query = LatestStats.all()
        query.filter("team = ", team)
        query.filter("stats_kind =", stats_kind)
        data = eval(query.get().stats)

        conv_teamname = {'marines': 'M',
                         'giants': 'G',
                         'baystars': 'De',
                         'eagles': 'E',
                         'fighters': 'F',
                         'swallows': 'S',
                         'lions': 'L',
                         'tigers': 'T',
                         'buffaloes': 'Bs',
                         'howks': 'H',
                         'dragons': 'D',
                         'carp': 'C'}


        def pitching(data):
            from BaseballStatistics import PitchingStats
            
            stats_list = []
            for p in data:
                dic = {'team': conv_teamname[team], 'throws': p[0],
                       'name': p[1],
                       'g': int(p[2]), 'w': int(p[3]), 'l': int(p[4]),
                       'sv': int(p[5]), 'cg': int(p[6]), 'sho': int(p[7]),
                       'zbc': int(p[8]), 'wpct': float(p[9]), 'bf': int(p[10]),
                       'h': int(p[13]), 'hr': int(p[14]),
                       'bb': int(p[15]), 'ibb': int(p[16]), 'hb': int(p[17]),
                       'so': int(p[18]), 'wp': int(p[19]), 'bk': int(p[20]),
                       'r': int(p[21]), 'er': int(p[22]),
                       'era': float(p[23]) if p[23] != '----' else '-'}
                if p[11] == '+':
                    dic['ip'] = '0.0'
                    dic['outs'] = 0
                elif p[12]:
                    dic['ip'] = "%s%s" % (p[11], p[12])
                    dic['outs'] = int(p[11]) * 3 + int(p[12][1:])
                else:
                    dic['ip'] = "%s.0" % p[11]
                    dic['outs'] = int(p[11]) * 3
                sebr = PitchingStats().getAll(g=dic['g'], h=dic['h'],
                                              hr=dic['hr'], bb=dic['bb'],
                                              ibb=dic['ibb'], hb=dic['hb'],
                                              so=dic['so'], r=dic['r'],
                                              outs=dic['outs'])
                dic.update(sebr)

                #formatting
                if dic['throws'] == '*': dic['throws'] = 'L'
                elif dic['throws'] == '+': dic['throws'] = 'S'
                else: dic['throws'] = 'R'
                if isinstance(dic['wpct'], (int, float)):
                    dic['wpct'] = ("%.3f" % round(dic['wpct'], 3))
                    dic['wpct'] = dic['wpct'][1:] if dic['wpct'][0] == '0'\
                                  else dic['wpct']
                if isinstance(dic['era'], (int, float)):
                    dic['era'] = ("%.2f" % round(dic['era'], 2)) \
                                 if dic['era'] != 'N/A' else dic['era']
                if isinstance(dic['whip'], (int, float)):
                    dic['whip'] = "%.2f" % round(dic['whip'], 2)
                if isinstance(dic['fip'], (int, float)):
                    dic['fip'] = "%.2f" % round(dic['fip'], 2)
                if isinstance(dic['lobp'], (int, float)):
                    dic['lobp'] = "%.1f%%" % round(dic['lobp'] * 100, 2)
                if isinstance(dic['kbb'], (int, float)):
                    dic['kbb'] = "%.2f" % round(dic['kbb'], 2)
                if isinstance(dic['k9'], (int, float)):
                    dic['k9'] = "%.2f" % round(dic['k9'], 2)
                if isinstance(dic['bb9'], (int, float)):
                    dic['bb9'] = "%.2f" % round(dic['bb9'], 2)
                if isinstance(dic['hr9'], (int, float)):
                    dic['hr9'] = "%.2f" % round(dic['hr9'], 2)
                if isinstance(dic['ipg'], (int, float)):
                    dic['ipg'] = "%.2f" % round(dic['ipg'], 2)
                if isinstance(dic['babip'], (int, float)):
                    dic['babip'] = ("%.3f" % round(dic['babip'], 3))[1:]

                stats_list.append(dic.copy())

            return stats_list

        def batting(data):
            from BaseballStatistics import BattingStats
            
            stats_list = []
            for p in data:
                dic = {'team': conv_teamname[team], 'bats': p[0],
                       'name': p[1],
                       'g': int(p[2]), 'pa': int(p[3]), 'ab': int(p[4]),
                       'r': int(p[5]), 'h': int(p[6]), 'dbl': int(p[7]),
                       'tpl': int(p[8]), 'hr': int(p[9]), 'tb': int(p[10]),
                       'rbi': int(p[11]), 'sb': int(p[12]), 'cs': int(p[13]),
                       'sh': int(p[14]), 'sf': int(p[15]), 'bb': int(p[16]),
                       'ibb': int(p[17]), 'hbp': int(p[18]), 'so': int(p[19]),
                       'gd': int(p[20]), 'avg': float(p[21]),
                       'slg': float(p[22]), 'obp': float(p[23])}
                sebr = BattingStats().getAll(ab=dic['ab'], h=dic['h'],
                                             dbl=dic['dbl'], tpl=dic['tpl'],
                                             hr=dic['hr'], sb=dic['sb'],
                                             cs=dic['cs'], sh=dic['sh'],
                                             sf=dic['sf'], bb=dic['bb'],
                                             ibb=dic['ibb'], hbp=dic['hbp'],
                                             so=dic['so'], gd=dic['gd'])
                dic.update(sebr)

                # formating
                if dic['bats'] == '*': dic['bats'] = 'L'
                elif dic['bats'] == '+': dic['bats'] = 'S'
                else: dic['bats'] = 'R'
                if isinstance(dic['avg'], (int, float)):
                    dic['avg'] = "%.3f" % round(dic['avg'], 3)
                    dic['avg'] = dic['avg'][1:] if dic['avg'][0] == '0'\
                                 else dic['avg']
                if isinstance(dic['slg'], (int, float)):
                    dic['slg'] = "%.3f" % round(dic['slg'], 3)
                    dic['slg'] = dic['slg'][1:] if dic['slg'][0] == '0'\
                                 else dic['slg']
                if isinstance(dic['obp'], (int, float)):
                    dic['obp'] = "%.3f" % round(dic['obp'], 3)
                    dic['obp'] = dic['obp'][1:] if dic['obp'][0] == '0'\
                                 else dic['obp']
                if isinstance(dic['ops'], (int, float)):
                    dic['ops'] = "%.3f" % round(dic['ops'], 3)
                    dic['ops'] = dic['ops'][1:] if dic['ops'][0] == '0'\
                                 else dic['ops']
                if isinstance(dic['gpa'], (int, float)):
                    dic['gpa'] = ("%.3f" % round(dic['gpa'], 3))[1:]
                if isinstance(dic['babip'], (int, float)):
                    dic['babip'] = ("%.3f" % round(dic['babip'], 3))[1:]
                if isinstance(dic['isod'], (int, float)):
                    dic['isod'] = "%.3f" % round(dic['isod'], 3)
                    dic['isod'] = dic['isod'][1:] if dic['isod'][0] == '0'\
                                  else dic['isod']
                if isinstance(dic['isop'], (int, float)):
                    dic['isop'] = "%.3f" % round(dic['isop'], 3)
                    dic['isop'] = dic['isop'][1:] if dic['isop'][0] == '0'\
                                  else dic['isop']
                if isinstance(dic['sbp'], (int, float)):
                    dic['sbp'] = "%s%s" % (round(dic['sbp']*100, 1), "%")
                if isinstance(dic['noi'], (int, float)):
                    dic['noi'] = round(dic['noi'], 1)
                if isinstance(dic['rc'], (int, float)):
                    dic['rc'] = "%.2f" % round(dic['rc'], 2)
                if isinstance(dic['rc27'], (int, float)):
                    dic['rc27'] = "%.2f" % round(dic['rc27'], 2)
                if isinstance(dic['xr'], (int, float)):
                    dic['xr'] = "%.2f" % round(dic['xr'], 2)
                if isinstance(dic['xr27'], (int, float)):
                    dic['xr27'] = "%.2f" % round(dic['xr27'], 2)

                stats_list.append(dic.copy())

            return stats_list

        if stats_kind == 'batting':
            result = batting(data)
        elif stats_kind == 'pitching':
            result = pitching(data)

        return result

    def getStatsAsJson(self, team, stats_kind, callback=None):
        query_string = "%s-%s" % (team, stats_kind)
        get = memcache.get(query_string)
        if get is not None:
            if callback is not None:
                return "%s(%s)" % (callback, get)
            return get

        result = json.dumps(self.buildStats(team, stats_kind))
        memcache.add(query_string, result)

        if callback is not None:
            return "%s(%s)" % (callback, result)
        return result

    def getGamesCountAsJson(self):
        data = Manage.all().get()
        count = eval(data.game_count)

        return json.dumps(count)

    def getHTML(self, mode):
        template_values = {"mode": mode}
        path = os.path.join(os.path.dirname(__file__),
                            './resources/%s.html' % mode)
        return template.render(path, template_values).encode('utf-8')
        
    

class Applications():
    def batting(self, environ, start_response):
        output = Results().getHTML('batting');
        response_headers = [('Content-Type', 'text/html'),
                            ('Content-Length', str(len(output)))]

        start_response('200 OK', response_headers)
        return [output]
    
    def pitching(self, environ, start_response):
        output = Results().getHTML('pitching');
        response_headers = [('Content-Type', 'text/html'),
                            ('Content-Length', str(len(output)))]

        start_response('200 OK', response_headers)
        return [output]
        
    def api(self, environ, start_response):
        from cgi import parse_qs

        query = parse_qs(environ.get('QUERY_STRING'))
        keys = query.keys()

        self.status = '400 Bad Request'
        output = 'Bad Request'
        response_headers = [('Content-Type', 'text/plain'),
                            ('Content-Length', str(len(output)))]

        if 'request_kind' in keys:
            if query['request_kind'][0] == 'games':
                self.status = '200 OK'
                output = Results().getGamesCountAsJson()
                response_headers = [('Content-Type', 'application/json'),
                                    ('Content-Length', str(len(output)))]
            elif ((query['request_kind'][0] == 'stats') and
                  ('team' in keys) and
                  ('stats_kind' in keys) and
                  ('callback' in keys)):
                self.status = '200 OK'
                output = Results().getStatsAsJson(query['team'][0],
                                                  query['stats_kind'][0],
                                                  query['callback'][0])
                response_headers = [('Content-Type', 'application/json'),
                                    ('Content-Length', str(len(output)))]
            else: output = 'hoge'
        else:
            output = 'nokind'

        start_response(self.status, response_headers)
        return [output]


class WsgiUrlMapper(object):
    def __init__(self, table):
        paths = sorted(table, key=lambda x: len(x), reverse=True)
        table = [(x, table[x]) for x in paths]
        self.table = table

    def __call__(self, environ, start_response):
        NAME = 'SCRIPT_NAME'
        INFO = 'PATH_INFO'

        scriptname = environ.get(NAME, '')
        pathinfo = environ.get(INFO, '')

        for path, app in self.table:
            if path == '' or path == '/' and pathinfo.startswith(path):
                return app(environ, start_response)

            if pathinfo == path or pathinfo.startswith(path) and \
                   pathinfo[len(path)] == '/':
                scriptname = scriptname + path
                pathinfo = pathinfo[len(path):]

                environ[NAME] = scriptname
                environ[INFO] = pathinfo

                return app(environ, start_response)


def main():
    app = Applications()
    url_map = {'/api/': app.api,
               '/p': app.pitching,
               '/b': app.batting,
               '/': app.batting}
    application = WsgiUrlMapper(url_map)
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
