from __future__ import annotations

import os
from dataclasses import dataclass

import psutil
from scapy.all import get_if_list


@dataclass
class InterfaceInfo:
    name: str
    is_up: bool
    addresses: list[str]


def list_interfaces() -> list[InterfaceInfo]:
    nic_stats = psutil.net_if_stats()
    nic_addrs = psutil.net_if_addrs()
    scapy_ifaces = set(get_if_list())

    interfaces: list[InterfaceInfo] = []
    for name, stats in nic_stats.items():
        if name not in scapy_ifaces:
            continue
        addresses = []
        for addr in nic_addrs.get(name, []):
            if addr.address:
                addresses.append(addr.address)
        interfaces.append(
            InterfaceInfo(name=name, is_up=stats.isup, addresses=addresses)
        )
    interfaces.sort(key=lambda x: x.name.lower())
    return interfaces


def pick_default_interface() -> str | None:
    for iface in list_interfaces():
        if iface.is_up and not iface.name.lower().startswith(("loopback", "lo")):
            return iface.name
    interfaces = list_interfaces()
    return interfaces[0].name if interfaces else None


def check_permission_hint() -> str | None:
    if os.name == "nt":
        return (
            "Windows 抓包通常需要管理员权限，并安装 Npcap "
            "(建议勾选 WinPcap API-compatible Mode)。"
        )
    if os.geteuid() != 0:  # type: ignore[attr-defined]
        return "Linux/macOS 建议 root 权限或 CAP_NET_RAW。"
    return None
