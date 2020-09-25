import re
import sys
import traceback

from functools import partial

import click
import requests

from . import __APP_NAME__, __VERSION__


DNSMASQ_FORMAT = "address=/{domain}/0.0.0.0"
DOMAIN_FIND = re.compile(
    r"(([\da-zA-Z])([_\w-]{,62})\.){,127}(([\da-zA-Z])[_\w-]{,61})?([\da-zA-Z]\.((xn\-\-[a-zA-Z\d]+)|([a-zA-Z\d]{2,})))",
    re.IGNORECASE,
)
SKIP_DOMAINS = [
    "localhost",
    "localhost.localdomain",
]

"""
127.0.0.1 localhost
127.0.0.1 localhost.localdomain
127.0.0.1 local
255.255.255.255 broadcasthost
::1 localhost
::1 ip6-localhost
::1 ip6-loopback
fe80::1%lo0 localhost
ff00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
ff02::3 ip6-allhosts
0.0.0.0 0.0.0.0
"""

SOURCES = {
    "hosts_file": {
        "badd_boyz.dl": "https://raw.githubusercontent.com/mitchellkrogza/Badd-Boyz-Hosts/master/hosts",
        "kadhosts.dl": "https://raw.githubusercontent.com/azet12/KADhosts/master/KADhosts.txt",
        "sbc.dl": "http://sbc.io/hosts/hosts",
        "someonewhocares.dl": "https://someonewhocares.org/hosts/hosts",
        "steven_black.dl": "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
        "sysctlorg_cameleon.dl": "http://sysctl.org/cameleon/hosts",
        "yoyo.dl": "http://pgl.yoyo.org/as/serverlist.php?mimetype=plaintext",
    },
    "domain_list": {
        "discon_ads.dl": "https://s3.amazonaws.com/lists.disconnect.me/simple_ad.txt",
        "discon_track.dl": "https://s3.amazonaws.com/lists.disconnect.me/simple_tracking.txt",
        "malware_dom.dl": "https://mirror1.malwaredomains.com/files/justdomains",
    },
}


def download_content(url: str):
    return requests.get(url).text


@click.version_option(version=__VERSION__, prog_name=__APP_NAME__)
@click.command(short_help="Generates the dnsmasq blacklist file")
@click.option(
    "--outfile",
    "-o",
    type=click.Path(exists=False, file_okay=True, dir_okay=False),
    required=False,
    default=None,
    help=(
        "The output file to the generated blacklist config. If not set, the "
        "output will be set to stdout."
    ),
)
def cli(outfile):
    to_err = partial(click.echo, file=sys.stderr)
    blocked_hosts = []

    for k, v in SOURCES["domain_list"].items():
        try:
            to_err(f"downloading domains from {k}")
            content = download_content(v)
            for line in content.split("\n"):
                line = line.strip()
                if line != "" and not line.startswith("#"):
                    if " " in line:
                        host = line.split()[1].strip()
                    else:
                        host = line.strip()
                    host, *_ = host.split("#")
                    if host not in blocked_hosts:
                        blocked_hosts.append(host)
        except Exception:
            to_err("")
            to_err("==============================================")
            to_err(f"error while downloading {k}")
            to_err("")
            traceback.print_exc(file=sys.stderr)
            to_err("==============================================")

    for k, v in SOURCES["hosts_file"].items():
        try:
            to_err(f"downloading domains from {k}")
            content = download_content(v)
            for line in content.split("\n"):
                line = line.strip()
                if line != "" and not line.startswith("#"):
                    res = DOMAIN_FIND.search(line)
                    if res is None:
                        continue
                    host = res.group(0)
                    if host in SKIP_DOMAINS:
                        continue
                    if host not in blocked_hosts:
                        blocked_hosts.append(host)
        except Exception:
            to_err("")
            to_err("==============================================")
            to_err(f"error while downloading {k}")
            to_err("")
            traceback.print_exc(file=sys.stderr)
            to_err("==============================================")

    blocked_hosts.sort()

    output = "\n".join(
        [DNSMASQ_FORMAT.format(domain=h) for h in blocked_hosts]
    )

    if outfile is None:
        outfile = "-"

    with click.open_file(outfile, 'w') as f:
        f.write(output)

    to_err("done!")


if __name__ == "__main__":
    try:
        cli()
    except SystemExit:
        pass
