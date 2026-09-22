#!/usr/bin/env python3
"""高德可搜性验证工具
通道 A: 百度地图 suggest (map.baidu.com/su) —— 拿规范 POI 名 (快、稳)
通道 B: 360 搜索 "店名 高德地图" -> 抓 amap.com/place/<ID> —— 高德存在性证据 (慢)
用法: python3 verify_poi.py "店名" ["店名2" ...]
"""
import json, re, sys, time, urllib.parse, urllib.request

UA_PC = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
         '(KHTML, like Gecko) Chrome/128.0 Safari/537.36')
UA_MOB = ('Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 '
          '(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1')


def _get(url, ua, referer=None, timeout=15, tries=3):
    for t in range(tries):
        try:
            h = {'User-Agent': ua}
            if referer:
                h['Referer'] = referer
            req = urllib.request.Request(url, headers=h)
            return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', 'ignore')
        except Exception:
            time.sleep(1.2 * (t + 1))
    return None


def parse_su(raw):
    """百度 su 返回: 城市$区$$店名$uid$  -> [(city, district, name)]"""
    out = []
    for x in raw:
        p = x.split('$')
        if len(p) >= 4:
            out.append((p[0], p[1], p[3]))
    return out


def baidu_su(name):
    url = 'https://map.baidu.com/su?' + urllib.parse.urlencode(
        {'wd': name, 'cid': 131, 'type': 0})
    body = _get(url, UA_PC, 'https://map.baidu.com/')
    if not body:
        return None
    try:
        return parse_su(json.loads(body).get('s', []))
    except Exception:
        return None


def so_amap_ids(name):
    """360 搜索找 amap.com/place/<ID>，返回去重后的 POI ID 列表"""
    url = 'https://m.so.com/s?' + urllib.parse.urlencode({'q': f'{name} 高德地图'})
    body = _get(url, UA_MOB)
    if not body:
        return []
    return sorted(set(re.findall(r'amap\.com/place/([A-Za-z0-9]+)', body)))


def check(name):
    clean = re.sub(r'[（(].*$', '', name).strip()
    su = baidu_su(clean)
    ids = so_amap_ids(clean)
    gz = [n for c, d, n in (su or []) if '广州' in c]
    exact = [n for n in gz if clean in n or n.startswith(clean[:3])]
    return {
        'query': clean,
        'baidu_gz': gz[:5],
        'amap_ids': ids,
        'verdict': ('AMAP_OK' if ids else ('BAIDU_LIKELY' if exact else
                    ('MISMATCH' if gz else 'NOT_FOUND'))),
    }


if __name__ == '__main__':
    args = sys.argv[1:]
    results = []
    for a in args:
        r = check(a)
        results.append(r)
        print(f"[{r['verdict']:12}] {a}")
        print(f"    百度(广州): {' | '.join(r['baidu_gz']) or '—'}")
        print(f"    高德place: {', '.join(r['amap_ids']) or '—'}")
        time.sleep(0.8)
    json.dump(results, open('poi_verify_out.json', 'w'), ensure_ascii=False, indent=1)
