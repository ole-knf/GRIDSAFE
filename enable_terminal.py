import argparse
import getpass
import subprocess
import sys


def main():
    # Get network namespace of parameter
    parser = argparse.ArgumentParser("Open a terminal for a running host")
    parser.add_argument("entity_id", help="The entity ID of the host")
    args = parser.parse_args()
    namespace = f"w_{args.entity_id}"
    user = getpass.getuser()

    #connect to namespace
    subprocess.run(
        f"sudo -E ip netns exec {namespace} ibus-daemon --xim -d -r", shell=True
    )

    #start bash in namespace
    cmd = [
        "sudo",
        "-E",
        "ip",
        "netns",
        "exec",
        namespace,
        "/bin/bash",
        "-c",
        f"'su -m {user}'",
    ]
    cmd = " ".join(cmd)
    print(f"Joining node {args.entity_id} as {user}")
    p = subprocess.Popen(
        cmd, shell=True, stdin=sys.stdin, stderr=sys.stderr, stdout=sys.stdout
    )

    #Shell remains open as long as the process lives
    p.wait()
    print("Goodbye")


if __name__ == "__main__":
    main()
