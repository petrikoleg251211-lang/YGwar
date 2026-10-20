#!/usr/bin/env python3
"""
YGwar: remove references to country TAGs that do not exist in this mod from vanilla technology files.

Why: the mod only defines 12 tags (YUG, SER, CRO, BOS, SVN, MAC, MNT, KOS, VOJ, RSK, RSB, HRZ).
Vanilla common/technologies/*.txt contain things like  `GER = { has_war = yes }`  inside
ai_will_do / allow blocks. With the tag missing, the parser fails on the first one and every
technology after it in the file is lost ("Unexpected token: infantry_weapons2 ...").

What it does (read-only on the game folder, writes only into the mod folder):
  * `XXX = { ... }`            (XXX = unknown 3-letter tag scope)  -> `always = no`   (trigger blocks)
                                                                      removed         (effect blocks)
  * `tag / original_tag / has_war_with / is_ally_with / ... = XXX`   -> `always = no` / removed
  * everything else is left byte-for-byte as in the vanilla file.
  * the output file is only written if braces are still balanced.

Usage:
    python tools/sanitize_vanilla_techs.py --game "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV"
Optional:
    --mod  <mod folder>            (default: folder above this script)
    --files infantry.txt support.txt naval.txt      (default; add more names to process more files)
    --dry-run                      only print the report
The report is also written to tools/sanitize_report.txt
"""
import argparse, os, re, sys

TAG_RE = re.compile(r'^[A-Z][A-Z0-9]{2}$')
KEEP_SCOPES = {'AND', 'NOT', 'ROOT', 'PREV', 'FROM', 'THIS', 'OR', 'ALL'}
TAG_VALUE_KEYS = {'tag', 'original_tag', 'has_war_with', 'has_defensive_war_with', 'has_offensive_war_with',
                  'is_ally_with', 'is_in_faction_with', 'is_puppet_of', 'is_subject_of', 'is_owned_by',
                  'is_controlled_by', 'has_guaranteed', 'is_neighbor_of', 'exists', 'has_embargo_against',
                  'is_justifying_wargoal_against', 'has_non_aggression_pact_with', 'has_military_access_to',
                  'gives_military_access_to', 'is_in_faction_with'}
EFFECT_KEYS = {'on_research_complete', 'effect', 'immediate', 'completion_reward', 'on_complete', 'hidden_effect'}
TRIGGER_KEYS = {'limit', 'allow', 'available', 'trigger', 'visible', 'potential', 'cancel', 'bypass'}
MTTH_KEYS = {'ai_will_do'}

def tokenize(text):
    toks = []; i = 0; n = len(text)
    while i < n:
        c = text[i]
        if c in ' \t\r\n': i += 1; continue
        if c == '#':
            while i < n and text[i] != '\n': i += 1
            continue
        if c in '{}': toks.append((c, i, i + 1)); i += 1; continue
        if c in '=<>!':
            j = i + 1
            if j < n and text[j] == '=': j += 1
            toks.append(('op', i, j)); i = j; continue
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"': j += 1
            toks.append(('word', i, j + 1)); i = j + 1; continue
        j = i
        while j < n and text[j] not in ' \t\r\n{}=<>!#"': j += 1
        if j == i: j = i + 1
        toks.append(('word', i, j)); i = j
    return toks

class Node:
    __slots__ = ('key', 'start', 'end', 'children', 'value', 'is_block', 'key_end')

def parse(text, toks):
    pos = 0
    def parse_list():
        nonlocal pos
        items = []
        while pos < len(toks) and toks[pos][0] != '}':
            t = toks[pos]
            if t[0] == 'word':
                nd = Node(); nd.key = text[t[1]:t[2]]; nd.start = t[1]; nd.key_end = t[2]
                nd.children = None; nd.value = None; nd.is_block = False
                pos += 1
                if pos < len(toks) and toks[pos][0] == 'op':
                    pos += 1
                    if pos < len(toks) and toks[pos][0] == '{':
                        pos += 1
                        nd.children = parse_list(); nd.is_block = True
                        if pos >= len(toks): raise ValueError('unbalanced braces')
                        nd.end = toks[pos][2]; pos += 1
                    elif pos < len(toks) and toks[pos][0] == 'word':
                        nd.value = text[toks[pos][1]:toks[pos][2]]; nd.end = toks[pos][2]; pos += 1
                    else: raise ValueError('value expected near offset %d' % t[1])
                else:
                    nd.end = t[2]
                items.append(nd)
            elif t[0] == '{':
                pos += 1; sub = parse_list()
                if pos >= len(toks): raise ValueError('unbalanced braces')
                pos += 1
                nd = Node(); nd.key = ''; nd.start = t[1]; nd.key_end = t[2]; nd.children = sub; nd.is_block = True
                nd.value = None; nd.end = toks[pos - 1][2]; items.append(nd)
            else:
                pos += 1   # stray operator, skip
        return items
    root = parse_list()
    if pos != len(toks): raise ValueError('unexpected closing brace')
    return root

def collect(nodes, ctx, parent_key, allowed, edits):
    for nd in nodes:
        if nd.is_block and TAG_RE.match(nd.key or '') and nd.key not in allowed and nd.key not in KEEP_SCOPES:
            delete = (ctx == 'effect') or (parent_key in MTTH_KEYS)
            edits.append((nd.start, nd.end, '' if delete else 'always = no', nd.key, 'scope'))
            continue
        if (not nd.is_block) and nd.value is not None and nd.key in TAG_VALUE_KEYS \
                and TAG_RE.match(nd.value) and nd.value not in allowed and nd.value not in KEEP_SCOPES:
            delete = (ctx == 'effect') or (parent_key in MTTH_KEYS)
            edits.append((nd.start, nd.end, '' if delete else 'always = no', nd.key + ' = ' + nd.value, 'value'))
            continue
        if nd.is_block:
            new_ctx = ctx
            if nd.key in EFFECT_KEYS: new_ctx = 'effect'
            elif nd.key in TRIGGER_KEYS: new_ctx = 'trigger'
            collect(nd.children, new_ctx, nd.key, allowed, edits)

def line_of(text, off): return text.count('\n', 0, off) + 1

def read_allowed_tags(mod):
    allowed = set()
    d = os.path.join(mod, 'common', 'country_tags')
    if os.path.isdir(d):
        for fn in os.listdir(d):
            if fn.endswith('.txt'):
                for m in re.finditer(r'^\s*([A-Z][A-Z0-9]{2})\s*=', open(os.path.join(d, fn), encoding='utf-8-sig').read(), re.M):
                    allowed.add(m.group(1))
    return allowed

def process(text, allowed):
    toks = tokenize(text)
    tree = parse(text, toks)
    edits = []
    collect(tree, 'trigger', None, allowed, edits)
    # drop edits nested inside another edit
    edits.sort(key=lambda e: (e[0], -e[1]))
    flat = []
    for e in edits:
        if flat and e[0] < flat[-1][1]: continue
        flat.append(e)
    out = text
    for s, e, rep, what, kind in sorted(flat, key=lambda e: -e[0]):
        out = out[:s] + rep + out[e:]
    # sanity: braces must stay balanced and file must still parse
    parse(out, tokenize(out))
    return out, flat

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--game', required=True)
    ap.add_argument('--mod', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument('--files', nargs='*', default=['infantry.txt', 'support.txt', 'naval.txt'])
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    allowed = read_allowed_tags(a.mod)
    if not allowed: sys.exit('No tags found in %s/common/country_tags' % a.mod)
    print('Allowed (existing) tags:', ' '.join(sorted(allowed)))
    report = []
    for fn in a.files:
        src = os.path.join(a.game, 'common', 'technologies', fn)
        if not os.path.isfile(src):
            report.append('!! not found: %s' % src); continue
        raw = open(src, 'rb').read()
        text = raw.decode('utf-8-sig')
        try:
            new, edits = process(text, allowed)
        except ValueError as ex:
            report.append('!! %s: NOT written, parser problem: %s' % (fn, ex)); continue
        report.append('== %s: %d change(s)' % (fn, len(edits)))
        for s, e, rep, what, kind in edits:
            report.append('   line %-5d %-6s %-38s -> %s' % (line_of(text, s), kind, what, rep or '(removed)'))
        if edits and not a.dry_run:
            dst_dir = os.path.join(a.mod, 'common', 'technologies'); os.makedirs(dst_dir, exist_ok=True)
            dst = os.path.join(dst_dir, fn)
            open(dst, 'wb').write(new.encode('utf-8'))   # no BOM (BOM in active .txt files caused problems earlier)
            report.append('   written: %s' % dst)
        elif not edits:
            report.append('   nothing to change (file left as vanilla)')
    out = '\n'.join(report)
    print(out)
    if not a.dry_run:
        open(os.path.join(a.mod, 'tools', 'sanitize_report.txt'), 'w', encoding='utf-8').write(out + '\n')

if __name__ == '__main__':
    main()
