from __future__ import annotations

import sys


def main() -> None:
    from roftegar.app import SysmonApp

    app = SysmonApp()
    app.run()


if __name__ == "__main__":
    main()
