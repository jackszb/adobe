#!/usr/bin/env python3
"""
从上游 pihole 格式域名列表生成 sing-box rule-set 源文件 (adobe-reject.json)。

用法:
    python3 generate_rule.py <输入文件> <输出文件>
"""
import json
import re
import sys

# 一个合法域名标签的粗略校验：字母数字及连字符，且不以连字符开头/结尾
DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
    r"(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))+$"
)


def extract_domains(text: str):
    domains = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        # 兼容 "0.0.0.0 domain" / "127.0.0.1 domain" 这类 hosts 格式，
        # 以及纯域名格式（pihole.txt 目前是纯域名一行一个）。
        parts = line.split()
        domain = parts[-1].lower().rstrip(".")
        if DOMAIN_RE.match(domain):
            domains.add(domain)
    return domains


def main():
    if len(sys.argv) != 3:
        print(f"用法: {sys.argv[0]} <输入文件> <输出文件>", file=sys.stderr)
        sys.exit(1)

    src_path, out_path = sys.argv[1], sys.argv[2]

    with open(src_path, "r", encoding="utf-8") as f:
        text = f.read()

    domains = sorted(extract_domains(text))

    if not domains:
        print("错误：未提取到任何域名，终止以避免生成空规则集。", file=sys.stderr)
        sys.exit(1)

    rule_set = {
        "version": 5,
        "rules": [
            {
                "domain_suffix": domains,
            }
        ],
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rule_set, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"共提取 {len(domains)} 个去重域名，已写入 {out_path}")


if __name__ == "__main__":
    main()
