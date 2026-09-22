#!/usr/bin/env python3
"""百度地图 POI 查询工具（无需 AK / 无验证码）

发现于 2026-09-22：`api.map.baidu.com/?qt=s&wd=<词>&c=257` 返回完整 POI 数据，
含 name / addr / tel / area_name / uid / x,y 坐标 / std_tag / business_time，
是唯一可稳定获取"规范店名+门牌地址"的通道（高德全接口被封、百度 suggest 只给名字）。

注意：
- c=257 本地类目召回远好于 c=131（北京）
- 返回的 JSON 偶有非法转义字符，需容错解析
- 短名/常见名搜不准时，加「区名/镇名」限定再搜

用法：
  python3 baidu_poi.py "店名" ["店名2" ...]           # 打印结果
  python3 baidu_poi.py --json out.json "店名" ...     # 存 JSON
"""
import json, re, sys, time, urllib.parse, urllib.request

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/128.0 Safari/537.36')
KEEP = ('name', 'addr', 'tel', 'area_name', 'std_tag', 'uid', 'x', 'y',
        'business_time', 'city_name', 'poi_profile', 'is_authority_poi')


def _get(url, ref='https://map.baidu.com/', timeout=15, tries=3):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Referer': ref})
            return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', 'ignore')
        except Exception:
            time.sleep(1.2 * (t + 1))
    return None


def _tolerant(raw):
    """修掉 JSON 里的非法转义（该接口偶发）"""
    fixed = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', raw)
    try:
        return json.loads(fixed)
    except Exception:
        fixed2 = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', fixed)
        return json.loads(fixed2)


def query(word, city=257, limit=5):
    """返回 [{name,addr,tel,area_name,std_tag,...}, ...]；失败返回 None"""
    url = 'https://api.map.baidu.com/?' + urllib.parse.urlencode(
        {'qt': 's', 'wd': word, 'c': city})
    raw = _get(url)
    if not raw:
        return None
    try:
        d = _tolerant(raw)
    except Exception:
        return None
    content = d.get('content')
    if not isinstance(content, list):
        return None
    out = []
    for it in content[:limit]:
        if isinstance(it, dict):
            out.append({k: it.get(k) for k in KEEP if it.get(k) not in (None, '')})
    return out


def best_guangzhou(word):
    """取最可能的广州结果（优先 area_name 含「广州」的）"""
    res = query(word)
    if not res:
        return None
    gz = [r for r in res if '广州' in str(r.get('area_name', ''))]
    return (gz or res)[0]


if __name__ == '__main__':
    args = sys.argv[1:]
    out_path = None
    if args and args[0] == '--json':
        out_path = args[1]
        args = args[2:]
    if not args:
        print(__doc__)
        sys.exit(0)
    results = {}
    for w in args:
        r = query(w)
        results[w] = r
        print(f'===== {w}')
        if not r:
            print('  ❌ 无结果（或请求失败）')
            continue
        for it in r[:3]:
            print(f"  · {it.get('name')}")
            print(f"      地址: {it.get('addr','—')}")
            print(f"      区划: {it.get('area_name','—')} | 电话: {it.get('tel','—')}")
            print(f"      类目: {it.get('std_tag','—')}")
        time.sleep(1.0)
    if out_path:
        json.dump(results, open(out_path, 'w'), ensure_ascii=False, indent=1)
        print(f'\n已保存 {out_path}')
