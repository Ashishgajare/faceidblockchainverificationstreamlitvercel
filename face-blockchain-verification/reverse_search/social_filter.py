from __future__ import annotations
from typing import Iterable, List
from pydantic import BaseModel
from .result_parser import SearchResult
from urllib.parse import urlparse


DEFAULT_SOCIAL_DOMAINS = [
    "instagram.com",
    "facebook.com",
    "x.com",
    "twitter.com",
    "linkedin.com",
]


class SocialMediaCandidate(BaseModel):
    platform: str
    url: str
    title: str | None
    image_url: str | None
    raw: dict


def _domain_from_url(url: str | None) -> str | None:
    if not url:
        return None
    try:
        parsed = urlparse(url)
        return (parsed.hostname or "").lower().removeprefix("www.") or None
    except Exception:
        return None


def _platform_for_result(result: SearchResult) -> str:
    domain = _domain_from_url(result.link)
    return domain or result.source or "web"


def to_candidates(results: Iterable[SearchResult]) -> List[SocialMediaCandidate]:
    """Convert every parsed search result into a comparable web candidate."""
    return [
        SocialMediaCandidate(
            platform=_platform_for_result(result),
            url=result.link or "",
            title=result.title,
            image_url=result.thumbnail,
            raw=result.raw,
        )
        for result in results
        if result.link
    ]


def filter_social_results(results: Iterable[SearchResult], domains: Iterable[str] | None = None) -> List[SocialMediaCandidate]:
    domains = {domain.lower().removeprefix("www.") for domain in (domains or DEFAULT_SOCIAL_DOMAINS)}
    out: List[SocialMediaCandidate] = []
    for r in results:
        dom = _domain_from_url(r.link)
        if dom and (dom in domains or any(dom.endswith(f".{domain}") for domain in domains)):
            platform = dom.split(".")[-2] if "." in dom else dom
            if platform == "twitter":
                platform = "twitter"
            out.append(SocialMediaCandidate(platform=platform, url=r.link or "", title=r.title, image_url=r.thumbnail, raw=r.raw))
    return out
