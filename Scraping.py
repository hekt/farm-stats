#! /usr/local/env python
# -*- coding:utf-8 -*-

import sys
sys.path.append("./")

from google.appengine.ext import db
from google.appengine.api import memcache, urlfetch


class LatestStats(db.Model):
    team = db.StringProperty()
    stats_kind = db.StringProperty()
    stats = db.TextProperty()

    
class Manage(db.Model):
    date = db.DateProperty()
    digest = db.TextProperty()
    game_count = db.TextProperty()


class Scraping(object):
    TEAMS = ('marines', 'giants', 'baystars', 'eagles', 'fighters', 'swallows',
             'lions', 'tigers', 'buffaloes', 'howks', 'dragons', 'carp')
    TEAMS_TABLE = [['name_en', 'abbr_en', 'sponsor_jp_justified'],
                   ['baystars', 'db', u'DeNA'],
                   ['buffaloes', 'bs', u'オリックス'],
                   ['carp', 'c', u'広　　島'],
                   ['dragons', 'd', u'中　　日'],
                   ['eagles', 'e', u'楽　　天'],
                   ['fighters', 'f', u'日本ハム'],
                   ['giants', 'g', u'巨　　人'],
                   ['howks', 'h', u'ソフトバンク'],
                   ['lions', 'l', u'西　　武'],
                   ['marines', 'm', u'ロ ッ テ'],
                   ['swallows', 's', u'ヤクルト'],
                   ['tigers', 't', u'阪　　神']]

    INDEX_URL = 'http://bis.npb.or.jp/2012/stats/index_farm.html'
    BASE_URL_P = 'http://bis.npb.or.jp/2012/stats/idp2_%s.html'
    BASE_URL_B = 'http://bis.npb.or.jp/2012/stats/idb2_%s.html'

    def convertTeamName(self, name, to='name_en'):
        pos = self.TEAMS_TABLE[0].index(to)
        
        for i in self.TEAMS_TABLE[1:]:
            if name in i:
                return i[pos]
        else:
            return None

    def getTreeFromDocument(self, path):
        from BeautifulSoup import BeautifulSoup

        doc = urlfetch.fetch(path).content

        return BeautifulSoup(doc)

    def getStatsFromTree(self, tree):
        wrap_div = tree.find('div', attrs={'id': 'stdivmaintbl'})
        if wrap_div is None:
            return None
        table = wrap_div.find('table')
        
        results = []
        rows = table.findAll('tr', attrs={'class': 'ststats'})
        for row in rows:
            cells = row.findAll('td')
            str_list = [s.string for s in cells]
            results.append(str_list)

        return results

    def getStatsByTeam(self, team, stats_kind='both'):
        if not team in self.TEAMS:
            raise ValueError('invalid team')

        initial = self.convertTeamName(team, to='abbr_en')

        if stats_kind is 'both':
            tree_p = self.getTreeFromDocument(self.BASE_URL_P % initial)
            tree_b = self.getTreeFromDocument(self.BASE_URL_B % initial)
            stats_p = self.getStatsFromTree(tree_p)
            stats_b = self.getStatsFromTree(tree_b)
            if stats_p is None or stats_b is None:
                stats = None
            else:
                stats = {'pitching': stats_p,
                         'batting': stats_b}
        elif stats_kind == 'pitching':
            tree = self.getTreeFromDocument(self.BASE_URL_P % initial)
            stats = getStatsFromTree(tree)
        elif stats_kind == 'batting':
            tree = self.getTreeFromDocument(self.BASE_URL_B % initial)
            stats = getStatsFromTree(tree)
        else:
            raise ValueError('invalid stats_kind')

        return stats

    def getGameCountsFromTree(self, tree):
        def getCount(wrap_div):
            d = {}
            TEAM_CLASS = {'class': 'standingsTeam'}
            GAME_CLASS = {'class': 'standingsGame'}
            
            table = wrap_div.find('table')
            rows = table.findAll('tr')
            for row in rows:
                team_cell = row.find('td', attrs=TEAM_CLASS)
                if not team_cell:
                    continue
                team = team_cell.string
                if team is None:
                    continue
                team = self.convertTeamName(team, to='name_en')
                count = row.find('td', attrs=GAME_CLASS).string
                d[team] = int(count)

            return d

        result = {}
        # east
        wrap_div = tree.find('div', attrs={'id': 'stdel'})
        result.update(getCount(wrap_div))
        # west
        wrap_div = tree.find('div', attrs={'id': 'stdwl'})
        result.update(getCount(wrap_div))

        return result

    def getDigest(self, url):
        import hashlib
        f = urlfetch.fetch(url)
        digest = hashlib.sha224(f.content).hexdigest()
        return digest

    def updateStats(self, dic):
        # dic = {team: {stats_kind: stats_str, ...}, ...}

        def update(stats_kind):
            put_items = []
            for k in dic.keys():
                q = LatestStats.all()
                q.filter('team =', k)
                q.filter('stats_kind =', stats_kind)
                e = q.get()
                if e is None:
                    e = LatestStats(team = k,
                                    stats_kind = stats_kind,
                                    stats = str(dic[k][stats_kind]))
                else:
                    e.stats = str(dic[k][stats_kind])
                put_items.append(e)
            return put_items

        db.put(update('pitching') + update('batting'))

    def updateManage(self, digest, game_count=None, date=None):
        import datetime

        if date is None:
            date = datetime.date.today()

        if game_count is None:
            tree = self.getTreeFromDocument(self.INDEX_URL)
            game_count = str(self.getGameCountsFromTree(tree))

        e = Manage.all().get()
        if e is None:
            e = Manage(date=date, digest=digest, game_count=game_count)
        else:
            e.date = date
            e.digest = digest
            e.game_count = game_count

        db.put(e)

    def dailyTask(self):
        e = Manage.all().get()
        latest_digest = Manage.all().get().digest if e else ''
        new_digest = self.getDigest(self.INDEX_URL)

        if latest_digest == new_digest:
            return False

        all_stats = {}
        for team in self.TEAMS:
            stats = self.getStatsByTeam(team, 'both')
            if stats is not None:
                all_stats[team] = stats
        if all_stats:
            self.updateStats(all_stats)
            self.updateManage(new_digest)

        memcache.flush_all()        

        return True


if __name__ == '__main__':
    app = Scraping()
    app.dailyTask()
