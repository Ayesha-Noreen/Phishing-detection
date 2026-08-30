import re
import socket
import requests
import whois

from urllib.parse import urlparse
from bs4 import BeautifulSoup


def extract_features(url):

    # Add scheme if missing
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    parsed = urlparse(url)

    domain = parsed.netloc
    domain = domain.split("@")[-1]
    domain = domain.split(":")[0]

    features = {}

    # ==========================================
    # 1. Have_IP
    # ==========================================

    ip_pattern = r"^(?:\d{1,3}\.){3}\d{1,3}$"

    features["Have_IP"] = 1 if re.match(ip_pattern, domain) else 0


    # ==========================================
    # 2. Have_At
    # ==========================================

    features["Have_At"] = 1 if "@" in url else 0


    # ==========================================
    # 3. URL_Length
    # ==========================================

    length = len(url)

    if length < 54:
        features["URL_Length"] = 1
    else:
        features["URL_Length"] = 0


    # ==========================================
    # 4. URL_Depth
    # ==========================================

    path_parts = [x for x in parsed.path.split("/") if x]

    features["URL_Depth"] = len(path_parts)


    # ==========================================
    # 5. Redirection
    # ==========================================

    # Look for // after the protocol
    remaining_url = re.sub(r"^https?://", "", url)

    features["Redirection"] = 1 if "//" in remaining_url else 0


    # ==========================================
    # 6. https_Domain
    # ==========================================

    features["https_Domain"] = 1 if parsed.scheme == "https" else 0


    # ==========================================
    # 7. TinyURL
    # ==========================================

    shortening_services = [
        "bit.ly",
        "tinyurl.com",
        "goo.gl",
        "t.co",
        "ow.ly",
        "is.gd",
        "buff.ly",
        "adf.ly",
        "bit.do",
        "cutt.ly",
        "shorturl.at"
    ]

    features["TinyURL"] = (
        1
        if any(service in domain.lower()
               for service in shortening_services)
        else 0
    )


    # ==========================================
    # 8. Prefix/Suffix
    # ==========================================

    features["Prefix/Suffix"] = 1 if "-" in domain else 0


    # ==========================================
    # 9. DNS_Record
    # ==========================================

    try:
        socket.gethostbyname(domain)
        features["DNS_Record"] = 1
    except:
        features["DNS_Record"] = 0


    # ==========================================
    # 10. Web_Traffic
    # ==========================================

    # Real traffic ranking requires an external
    # traffic-ranking API.
    #
    # Use neutral value for now.

    features["Web_Traffic"] = 1


    # ==========================================
    # 11. Domain_Age
    # ==========================================

    try:

        domain_info = whois.whois(domain)

        creation_date = domain_info.creation_date

        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        if creation_date:

            from datetime import datetime

            age_days = (datetime.now() - creation_date).days

            # Dataset convention:
            # 1 = older/established domain
            # 0 = young domain

            features["Domain_Age"] = 1 if age_days >= 180 else 0

        else:
            features["Domain_Age"] = 0

    except:

        features["Domain_Age"] = 0


    # ==========================================
    # 12. Domain_End
    # ==========================================

    try:

        domain_info = whois.whois(domain)

        expiration_date = domain_info.expiration_date

        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]

        if expiration_date:

            from datetime import datetime

            days_remaining = (
                expiration_date - datetime.now()
            ).days

            features["Domain_End"] = (
                1 if days_remaining > 30 else 0
            )

        else:

            features["Domain_End"] = 0

    except:

        features["Domain_End"] = 0


    # ==========================================
    # Download webpage
    # ==========================================

    html = ""

    try:

        response = requests.get(
            url,
            timeout=5,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        )

        html = response.text

    except:

        html = ""


    # ==========================================
    # BeautifulSoup
    # ==========================================

    soup = BeautifulSoup(
        html,
        "html.parser"
    )


    # ==========================================
    # 13. iFrame
    # ==========================================

    iframe_tags = soup.find_all("iframe")

    features["iFrame"] = (
        0 if len(iframe_tags) > 0 else 1
    )


    # ==========================================
    # 14. Mouse_Over
    # ==========================================

    mouse_over = False

    for tag in soup.find_all():

        events = [
            "onmouseover",
            "onmouseenter"
        ]

        for event in events:

            if tag.has_attr(event):

                mouse_over = True

    features["Mouse_Over"] = (
        0 if mouse_over else 1
    )


    # ==========================================
    # 15. Right_Click
    # ==========================================

    right_click_disabled = False

    for tag in soup.find_all():

        if tag.has_attr("oncontextmenu"):

            right_click_disabled = True

    if "contextmenu" in html.lower():
        right_click_disabled = True

    features["Right_Click"] = (
        0 if right_click_disabled else 1
    )


    # ==========================================
    # 16. Web_Forwards
    # ==========================================

    # Check HTTP redirect history

    try:

        response = requests.get(
            url,
            timeout=5,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            },
            allow_redirects=True
        )

        redirect_count = len(response.history)

        features["Web_Forwards"] = (
            0 if redirect_count > 2 else 1
        )

    except:

        features["Web_Forwards"] = 1


    return features