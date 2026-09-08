# -*- coding: utf-8 -*-
"""数据源整改:去掉携程(ctrip)数据与署名
规则:
1. score 字段:值含「携程」→ 整个值视为携程数据,置「以门店为准」(点评高分徽章依此自动摘牌)
2. 其他字段:剥掉携程署名(（携程...）/(携程...)/携程X.X分，)保留事实本体
3. sources:移除含 ctrip 的链接(字符串化列表,解析后过滤再还原)
"""
import json, os, re, ast

WORK = '/Users/boai/Documents/美食攻略/_work'
FIELDS = ['phone', 'hours', 'booking', 'queue', 'score', 'chef', 'story', 'tip', 'reason', 'addr', 'percap', 'category']

ATTRIB = re.compile(r'[（(]\s*携程[^）)]{0,40}[）)]')
BARE = re.compile(r'携程\s*\d(?:\.\d)?\s*分\s*[，,]\s*')

def clean_value(k, v):
    if v is None:
        return v
    s = str(v)
    if '携程' not in s:
        return v
    if k == 'score':
        return '以门店为准'
    s = ATTRIB.sub('', s)
    s = BARE.sub('', s)
    # 残留的「携程」字样(如「携程载」)直接清掉
    s = s.replace('携程', '').strip()
    # 清理多余标点/空格
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'[，,]\s*[，,]', '，', s)
    s = re.sub(r'[（(]\s*[)）]', '', s)
    s = re.sub(r'[，,]\s*$', '', s)
    s = s.strip()
    if not s or s in ('，', ',', '；', ';'):
        return '以门店为准'
    return s

def clean_sources(src):
    if not src:
        return src
    if isinstance(src, list):
        return [u for u in src if 'ctrip' not in str(u)]
    if isinstance(src, str):
        try:
            lst = ast.literal_eval(src)
            if isinstance(lst, list):
                lst = [u for u in lst if 'ctrip' not in str(u)]
                return str(lst)
        except Exception:
            pass
        # 非列表字符串:正则剔除 ctrip URL
        return re.sub(r'https?://[^\s\'\"\]]*ctrip[^\s\'\"\]]*', '', src)
    return src

def process_file(path, kind):
    data = json.load(open(path, encoding='utf-8'))
    n_val = n_src = 0
    stores = data.get('stores') if isinstance(data, dict) else None
    if stores is not None:
        for s in stores:
            for k in FIELDS:
                v = s.get(k)
                if v is not None and '携程' in str(v):
                    s[k] = clean_value(k, v)
                    n_val += 1
            if s.get('sources'):
                old = s['sources']
                new = clean_sources(old)
                if new != old:
                    s['sources'] = new
                    n_src += 1
    elif isinstance(data, dict):  # final_districts.json 结构
        for dist, lst in data.items():
            for s in lst:
                for k in FIELDS:
                    v = s.get(k)
                    if v is not None and '携程' in str(v):
                        s[k] = clean_value(k, v)
                        n_val += 1
                if s.get('sources'):
                    old = s['sources']
                    new = clean_sources(old)
                    if new != old:
                        s['sources'] = new
                        n_src += 1
    else:  # top10.json 列表
        for s in data:
            for k in FIELDS:
                v = s.get(k)
                if v is not None and '携程' in str(v):
                    s[k] = clean_value(k, v)
                    n_val += 1
            if s.get('sources'):
                old = s['sources']
                new = clean_sources(old)
                if new != old:
                    s['sources'] = new
                    n_src += 1
    json.dump(data, open(path, 'w'), ensure_ascii=False, indent=1)
    return n_val, n_src

def main():
    total_v = total_s = 0
    for f in sorted(os.listdir(WORK)):
        if f.startswith('fields_') and f.endswith('.json'):
            nv, ns = process_file(f'{WORK}/{f}', 'fields')
            total_v += nv; total_s += ns
            if nv or ns:
                print(f'{f}: 值 {nv}, sources {ns}')
    for f in ['final_districts.json', 'top10.json']:
        nv, ns = process_file(f'{WORK}/{f}', 'base')
        total_v += nv; total_s += ns
        if nv or ns:
            print(f'{f}: 值 {nv}, sources {ns}')
    print(f'总计:字段值清理 {total_v} 处,来源链接清理 {total_s} 处')

if __name__ == '__main__':
    main()
