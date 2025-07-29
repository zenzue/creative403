# Creative 403 Bypass Scanner

A fast, creative, and clear tool for web security testers and bug bounty hunters to discover possible 403 (Forbidden) bypass techniques on any web endpoint.

This scanner tries multiple payload and header combinations to identify potential access control misconfigurations, then reports only what matters in an easy-to-read console table.

---

## Features

* **Comprehensive Payloads:** Tries dozens of common and tricky path payloads and HTTP headers to trigger 403 bypasses.
* **Threaded Scanning:** Fast and efficient, with customizable concurrency.
* **Unique Result Detection:** Shows only unique, successful bypasses (non-403) with details.
* **Content Diffing:** Highlights differences between unique bypassed contents.
* **Colorized Output:** Beautiful summary tables and panels with [rich](https://github.com/Textualize/rich).
* **No CSV/JSON clutter:** Clear results only in the console.

---

## Installation

```bash
pip install requests beautifulsoup4 rich
```

---

## Usage

```bash
python creative403.py <url> <path> [--threads N] [--timeout S]
```

**Examples:**

```bash
python creative403.py https://target.com admin
python creative403.py https://target.com dashboard --threads 20
```

---

## Output Example

```
Testing 72 combinations. Please wait...

┏━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳────────────┓
┃ Status ┃ URL                                  ┃ Len  ┃ Title           ┃ Payload        ┃ Header                           ┃ Time (s)   ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┯━━━━━━┯━━━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┯────────────┩
│ [green]200[/green] │ https://target.com/admin%2e       │ 1543 │ Dashboard        │ admin%2e        │ -                               │ 0.11       │
│ [yellow]302[/yellow] │ https://target.com/admin         │ 0    │ -               │ admin           │ X-Forwarded-For: 127.0.0.1      │ 0.08       │
│ [green]200[/green] │ https://target.com/admin/.env     │ 352  │ Index of /admin │ admin/.env      │ -                               │ 0.13       │
└────────┴──────────────────────────────────────┴──────┴───────────────┴──────────────┴────────────────────────────────────┴────────────┘

╭───────────────────────────────────────────── Summary ───────────────────────────────────────────╮
│ Total tested: 72                                                                                │
│ Bypasses: 3 (3 unique responses)                                                                │
│ Fastest: admin (0.08s)                                                                          │
│ Slowest: admin/.env (0.13s)                                                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────╯

Differences between unique bypassed responses (first lines):

╭────────────────────────────────────────────────────────────╮
│ --- admin%2e                                               │
│ +++ admin/.env                                             │
│ @@                                                         │
│ <!DOCTYPE html>                                            │
│ <html lang="en">                                           │
│ <head>                                                     │
│ <meta charset="UTF-8">                                     │
│ <title>Index of /admin</title>                             │
╰────────────────────────────────────────────────────────────╯
```

---

## Recommended Use Cases

* Web app penetration testing
* WAF/ACL bypass research
* Bug bounty hunting
* Red teaming, purple teaming

---

## Notes

* For best results, run from a VPN or authorized test environment.
* Always have permission to test your targets.

---

## License

MIT

---

## Author

**Aung Myat Thu (w01f)**
[GitHub: zenzue](https://github.com/zenzue)
