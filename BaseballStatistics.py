class PitchingStats(object):
    def getAll(self, g, h, hr, bb, ibb, hb, so, r, outs):
        d = {}
        d['whip'] = self.whip(h=h, bb=bb, outs=outs)
        d['fip'] = self.fip(hr=hr, bb=bb, ibb=ibb, hb=hb, so=so, outs=outs)
        d['lobp'] = self.lobp(h=h, hr=hr, bb=bb, hb=hb, r=r)
        d['kbb'] = self.kbb(bb=bb, so=so)
        d['k9'] = self.k9(so=so, outs=outs)
        d['bb9'] = self.bb9(bb=bb, outs=outs)
        d['hr9'] = self.hr9(hr=hr, outs=outs)
        d['ipg'] = self.ipg(g=g, outs=outs)
        d['babip'] = self.babip(h=h, hr=hr, so=so, outs=outs)

        return d
               
    def tryDiv(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (ZeroDivisionError), e:
                return '-'
        return wrapper

    # whip
    @tryDiv
    def whip(self, h, bb, outs):
        return (h + bb) / (outs / 3.0)

    # fip
    @tryDiv
    def fip(self, hr, bb, ibb, hb, so, outs):
        return ((bb - ibb + hb) * 3 + hr * 13 - so * 2) / (outs / 3.0) + 3.12

    # lob%
    @tryDiv
    def lobp(self, h, hr, bb, hb, r):
        return (h + bb + hb - r) / (h + bb + hb - (1.4 * hr))

    # k/bb
    @tryDiv
    def kbb(self, bb, so):
        return float(so) / bb
    # k/9
    @tryDiv
    def k9(self, so, outs):
        return (so * 9 * 3) / float(outs)
    # bb/9
    @tryDiv
    def bb9(self, bb, outs):
        return (bb * 9 * 3) / float(outs)
    # hr/9
    @tryDiv
    def hr9(self, hr, outs):
        return (hr * 9 * 3) / float(outs)
    # ip/g
    @tryDiv
    def ipg(self, g, outs):
        return (outs / 3.0) / g
    # babip
    @tryDiv
    def babip(self, h, hr, so, outs):
        return (h - hr) / (outs / 3.0 * 2.8 + h - hr - so)


class BattingStats(object):
    def getAll(self, ab=0, h=0, dbl=0, tpl=0, hr=0, sb=0, cs=0,
               sh=0, sf=0, bb=0, ibb=0, hbp=0, so=0, gd=0):
        d = {}
        d['tb'] = self.tb(h=h, dbl=dbl, tpl=tpl, hr=hr)
        d['avg'] = self.avg(ab=ab, h=h)
        d['slg'] = self.slg(ab=ab, tb=d['tb']) if \
                   isinstance(d['tb'], (int, float)) else '-'
        d['obp'] = self.obp(ab=ab, h=h, bb=bb, hbp=hbp, sf=sf)
        d['sbp'] = self.sbp(sb=sb, cs=cs)
        d['ops'] = self.ops(obp=d['obp'], slg=d['slg']) if \
                   (isinstance(d['obp'], (int, float)) and
                    isinstance(d['slg'], (int, float))) else '-'
        d['noi'] = self.noi(obp=d['obp'], slg=d['slg']) if \
                   (isinstance(d['obp'], (int, float)) and
                    isinstance(d['slg'], (int, float))) else '-'
        d['gpa'] = self.gpa(obp=d['obp'], slg=d['slg']) if \
                   (isinstance(d['obp'], (int, float)) and
                    isinstance(d['slg'], (int, float))) else '-'
        d['to'] = self.to(ab=ab, h=h, sh=sh, sf=sf, cs=cs, gd=gd)
        d['rc'] = self.rc(ab=ab, tb=d['tb'], h=h, bb=bb, hbp=hbp,
                          sh=sh, so=so, gd=gd, sb=sb, cs=cs) if \
                          isinstance(d['tb'], (int, float)) else '-'
        d['rc27'] = self.rc27(rc=d['rc'], to=d['to']) if \
                    (isinstance(d['rc'], (int, float)) and
                     isinstance(d['to'], (int, float))) else '-'
        d['xr'] = self.xr(ab=ab, h=h, dbl=dbl, tpl=tpl, hr=hr, bb=bb, ibb=ibb,
                          hbp=hbp, sb=sb, cs=cs, sh=sh, sf=sf, so=so, gd=gd)
        d['xr27'] = self.xr27(xr=d['xr'], to=d['to']) if \
                    (isinstance(d['xr'], (int, float)) and
                     isinstance(d['to'], (int, float))) else '-'
        d['babip'] = self.babip(ab=ab, h=h, hr=hr, sf=sf, so=so)
        d['isop'] = self.isop(avg=d['avg'], slg=d['slg']) if \
                    (isinstance(d['avg'], (int, float)) and
                     isinstance(d['slg'], (int, float))) else '-'
        d['isod'] = self.isod(avg=d['avg'], obp=d['obp']) if \
                    (isinstance(d['avg'], (int, float)) and
                     isinstance(d['obp'], (int, float))) else '-'

        return d

    def tryDiv(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (ZeroDivisionError), e:
                return '-'
        return wrapper

    # total bases
    @tryDiv
    def tb(self, h, dbl=0, tpl=0, hr=0):
        return h + dbl + (tpl * 2) + (hr * 3)

    # average
    @tryDiv
    def avg(self, ab, h=0):
        return float(h) / ab

    # slugging percentage
    @tryDiv
    def slg(self, ab, tb=None, h=0, dbl=0, tpl=0, hr=0):
        if tb is None:
            tb = self.tb(h=h, dbl=dbl, tpl=tpl, hr=hr)
        return float(tb) / ab

    # on-base percentage
    @tryDiv
    def obp(self, ab, h=0, bb=0, hbp=0, sf=0):
        return (float(h) + bb + hbp) / (ab + bb + hbp + sf)

    # stolen base percentage
    @tryDiv
    def sbp(self, sb, cs):
        return float(sb) / (sb + cs)

    # on-base plus slugging
    @tryDiv
    def ops(self, obp=None, slg=None,
            ab=0, tb=None, h=0, dbl=0, tpl=0, hr=0, bb=0, hbp=0, sf=0):
        if obp is None:
            obp = self.obp(ab=ab, h=h, bb=bb, hbp=hbp, sf=sf)
        if slg is None:
            slg = self.slg(ab=ab, tb=tb, h=h, dbl=dbl, tpl=tpl, hr=hr)
        return obp + slg

    # new offensive index
    @tryDiv
    def noi(self, obp=None, slg=None,
            ab=0, tb=None, h=0, dbl=0, tpl=0, hr=0, bb=0, hbp=0, sf=0):
        if obp is None:
            obp = self.obp(ab=ab, h=h, bb=bb, hbp=hbp, sf=sf)
        if slg is None:
            slg = self.slg(ab=ab, tb=tb, h=h, dbl=dbl, tpl=tpl, hr=hr)
        return (float(slg) / 3 + obp) * 1000

    # gross production average
    @tryDiv
    def gpa(self, obp=None, slg=None,
            ab=0, tb=None, h=0, dbl=0, tpl=0, hr=0, bb=0, hbp=0, sf=0):
        if obp is None:
            obp = self.obp(ab=ab, h=h, bb=bb, hbp=hbp, sf=sf)
        if slg is None:
            slg = self.slg(ab=ab, tb=tb, h=h, dbl=dbl, tpl=tpl, hr=hr)
        return (float(obp) * 1.8 + slg) / 4

    # total outs
    @tryDiv
    def to(self, ab=0, h=0, sh=0, sf=0, cs=0, gd=0):
        return ab - h + sh + sf + cs + gd

    # runs created
    @tryDiv
    def rc(self,
           ab=0, tb=None, h=0, dbl=0, tpl=0, hr=0, bb=0, hbp=0, sh=0, sf=0,
           so=0, gd=0, sb=0, cs=0):
        if tb is None:
            tb = self.tb(h=h, dbl=dbl, tpl=tpl, hr=hr)
        a = h + bb + hbp - cs - gd
        b = (tb + ((bb + hbp) * 0.26) + ((sh + sf) * 0.53) + (sb * 0.64) -
             (so * 0.03))
        c = ab + bb + hbp + sh + sf
        return (((float(a) + c * 2.4) * (b + c * 3)) / (c * 9)) - (c * 0.9)

    # runs created per 27 outs
    @tryDiv
    def rc27(self,
             ab=0, tb=None, h=0, dbl=0, tpl=0, hr=0, bb=0, hbp=0, sh=0, sf=0,
             so=0, gd=0, sb=0, cs=0, rc=None, to=None):
        if rc is None:
            rc = self.rc(ab=ab, tb=tb, h=h, dbl=dbl, tpl=tpl, hr=hr, bb=bb,
                         hbp=hbp, sh=sh, so=so, gd=gd, sb=sb, cs=cs)
        if to is None:
            to = self.to(ab=ab, h=h, sh=sh, sf=sf, cs=cs, gd=gd)
        return float(rc) / to * 27

    # extraprolated runs
    @tryDiv
    def xr(self,
           ab=0, h=0, dbl=0, tpl=0, hr=0, bb=0, ibb=0, hbp=0,
           sb=0, cs=0, sh=0, sf=0, so=0, gd=0):
        return ((0.5 * (h - dbl - tpl - hr)) + (0.72 * dbl) + (1.04 * tpl) +
                (1.44 * hr) + (0.34 * (bb - ibb + hbp)) + (0.25 * ibb) +
                (0.18 * sb) - (0.32 * cs) - (0.09 * (ab - h - so)) -
                (0.098 * so) - (0.37 * gd) + (0.37 * sf) + (0.04 * sh))

    # extraprolated runs per 27 outs
    @tryDiv
    def xr27(self,
             ab=0, h=0, dbl=0, tpl=0, hr=0, bb=0, ibb=0, hbp=0,
             sb=0, cs=0, sh=0, sf=0, so=0, gd=0, xr=None, to=None):
        if xr is None:
            xr = self.xr(ab=ab, h=h, dbl=dbl, tpl=tpl, hr=hr, bb=bb, ibb=ibb,
                         hbp=hbp, sb=sb, cs=cs, sh=sh, sf=sf, so=so, gd=gd)
        if to is None:
            to = self.to(ab=ab, h=h, sh=sh, sf=sf, cs=cs, hd=hd)
        return float(xr) / to * 27

    # batting average on balls in play
    @tryDiv
    def babip(self, ab=0, h=0, hr=0, sf=0, so=0):
        return (float(h) - hr) / (ab + sf - hr - so)

    # isolated power
    @tryDiv
    def isop(self, ab=0, tb=None, h=0, dbl=0, tpl=0, hr=0, avg=None, slg=None):
        if avg is None:
            avg = self.avg(ab=ab, h=h)
        if slg is None:
            slg = self.slg(ab=ab, tb=tb, h=h, dbl=dbl, tpl=tpl, hr=hr)
        return slg - avg

    # isolated discipline
    @tryDiv
    def isod(self, ab=0, h=0, bb=0, hbp=0, sf=0, avg=None, obp=None):
        if avg is None:
            avg = self.avg(ab=ab, h=h)
        if obp is None:
            obp = self.obp(ab=ab, h=h, bb=bb, hbp=hbp, sf=sf)
        return obp - avg
