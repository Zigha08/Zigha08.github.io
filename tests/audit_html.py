#!/usr/bin/env python3
"""HTML validator for T1 audit — finds tag balance issues, duplicate IDs,
missing alt, inline event handlers, void-element self-closing, etc."""
import sys, re, os
from html.parser import HTMLParser

VOID = {"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}

class Audit(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.stack = []
        self.dup_ids = {}
        self.ids = {}
        self.findings = []
        self.void_self_closed = []
        self.inline_events = []
        self.missing_alt = []
        self.aria_label_missing = []
        self.cur_line_for_tag = {}

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs) if isinstance(attrs, list) else dict(attrs)
        # duplicate IDs
        if "id" in attrs_d:
            iid = attrs_d["id"]
            if iid in self.ids:
                self.findings.append((self.getpos(), "DUPLICATE_ID", f"id='{iid}' first at line {self.ids[iid]}"))
            else:
                self.ids[iid] = self.getpos()[0]
        # void elements
        if tag in VOID:
            # HTMLParser doesn't call end_tag for void (good); but if explicitly self-closed, flag
            pass
        # missing alt on img
        if tag == "img" and "alt" not in attrs_d:
            self.findings.append((self.getpos(), "MISSING_ALT", f"<img> missing alt attribute"))
        # inline event handlers
        attr_list = attrs if isinstance(attrs, list) else list(attrs)
        for k, v in attr_list:
            if k.startswith("on") and k.lower() not in ("on","off"):
                self.inline_events.append((self.getpos(), f"{k}='{v[:40]}'"))
        # require aria-label or text for input type=search etc (skip)
        if tag not in VOID:
            self.stack.append((tag, self.getpos()))

    def handle_startendtag(self, tag, attrs):
        # self-closing tags — only XML/SVG valid; HTML5 void: ok
        if tag not in VOID:
            # non-void self-closing in HTML is technically wrong, but HTMLParser converts
            pass
        # check inline events on self-closing
        attr_list = attrs if isinstance(attrs, list) else list(attrs)
        for k, v in attr_list:
            if k.startswith("on") and k.lower() not in ("on","off"):
                self.inline_events.append((self.getpos(), f"{k}='{v[:40]}'"))
        if tag in VOID:
            self.void_self_closed.append((self.getpos(), tag))

    def handle_endtag(self, tag):
        if not self.stack:
            self.findings.append((self.getpos(), "UNMATCHED_CLOSE", f"</{tag}> with no open tag"))
            return
        # pop until match (handle nesting)
        for i in range(len(self.stack)-1, -1, -1):
            open_tag, open_pos = self.stack[i]
            if open_tag == tag:
                # pop everything above (those are unclosed)
                unclosed = self.stack[i+1:]
                for ut, up in unclosed:
                    self.findings.append((up, "UNCLOSED_TAG", f"<{ut}> opened but not closed (closed by </{tag}>)"))
                self.stack = self.stack[:i]
                return
        # not found
        self.findings.append((self.getpos(), "UNMATCHED_CLOSE", f"</{tag}> doesn't match any open tag (open: {[t for t,_ in self.stack[-3:]]})"))

    def error(self, message):
        self.findings.append((self.getpos(), "PARSE_ERROR", message))

def audit(path):
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    p = Audit(path)
    try:
        p.feed(src)
    except Exception as e:
        print(f"PARSE EXCEPTION in {path}: {e}")
    # any tags still on stack?
    for tag, pos in p.stack:
        p.findings.append((pos, "UNCLOSED_TAG", f"<{tag}> never closed"))
    return p

if __name__ == "__main__":
    for path in sys.argv[1:]:
        print(f"\n=== {path} ===")
        p = audit(path)
        # dedupe and sort
        seen = set()
        for pos, kind, msg in sorted(p.findings, key=lambda x: (x[0][0], x[0][1])):
            key = (pos, kind, msg)
            if key in seen: continue
            seen.add(key)
            print(f"  {path}:{pos[0]}:{pos[1]} [{kind}] {msg}")
        if p.inline_events:
            for pos, msg in p.inline_events:
                print(f"  {path}:{pos[0]}:{pos[1]} [INLINE_EVENT] {msg}")
        if not p.findings and not p.inline_events:
            print("  (clean)")
