from setuptools import setup

setup(
    name="network-tools",
    version="0.1.0",
    py_modules=["ping2", "traceroute2"],
    entry_points={
        "console_scripts": [
            "ping2=ping2:main",
            "traceroute2=traceroute2:main",
        ],
    },
    description="Network diagnostic tools with ICMP/TCP ping and traceroute",
    author="Your Name",
)