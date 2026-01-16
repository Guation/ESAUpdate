#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Guation"
__all__ = ["update_ip", "update_port", "init"]

import time, uuid, hashlib, hmac, requests, json
from urllib.parse import quote, urlencode
from logging import debug, info, warning, error

__id: str = None
__token: str = None
__sub_domain: str = None
__domain: str = None

def init(id: str, token: str, sub_domain: str, domain: str):
    global __id, __token, __sub_domain, __domain
    __id = id
    __token = token
    __sub_domain = sub_domain
    __domain = domain

def domain2punycode(domain: str):
    return domain.encode('idna').decode('ascii')

def flattening_params(params, prefix = "", upper_params: dict = None):
    if upper_params is None:
        upper_params = {}
    if params is None:
        return upper_params
    elif isinstance(params, (list, tuple)):
        for i, item in enumerate(params):
            flattening_params(item, f"{prefix}.{i + 1}", upper_params)
    elif isinstance(params, dict):
        for sub_key, sub_value in params.items():
            flattening_params(sub_value, f"{prefix}.{sub_key}", upper_params)
    else:
        prefix = prefix.lstrip(".")
        upper_params[prefix] = params.decode("utf-8") if isinstance(params, bytes) else str(params)
    return upper_params

def request(method: str, action: str, params: dict = None):
    headers = {
        "host": "esa.cn-hangzhou.aliyuncs.com",
        "x-acs-action": action,
        "x-acs-version": "2024-09-10",
        "x-acs-date": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "x-acs-signature-nonce": str(uuid.uuid4()),
        "x-acs-content-sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
    headers = dict(sorted(headers.items()))
    canonical_query_string = "&".join(
        f"{quote(k)}={quote(str(v))}"
        for k, v in sorted(flattening_params(params).items())
    )
    canonical_headers = "\n".join(f"{k}:{v}" for k, v in headers.items()) + "\n"
    signed_headers = ";".join(headers.keys())
    canonical_request = "\n".join([method, "/", canonical_query_string, canonical_headers, signed_headers, headers["x-acs-content-sha256"]])
    hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
    signature = hmac.new(__token.encode("utf-8"), f"ACS3-HMAC-SHA256\n{hashed_canonical_request}".encode("utf-8"), hashlib.sha256).digest().hex().lower()
    headers["Authorization"] = f"ACS3-HMAC-SHA256 Credential={__id},SignedHeaders={signed_headers},Signature={signature}"
    debug("action=%s, params=%s, headers=%s", action, params, headers)
    try:
        response = requests.request(method, f"https://{headers['host']}/?{urlencode(params, doseq=True, safe='*')}", headers=headers)
        r = response.content
        if response.status_code != 200:
            raise ValueError(
                '服务器拒绝了请求：action=%s, status_code=%d, response=%s' % (action, response.status_code, r)
            )
        else:
            j = json.loads(r)
            debug("action=%s, response=%s", action, j)
            return j
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(
            "%s 请求失败" % action
        ) from e

def search_siteid(domain: str) -> int:
    domainPunycode = domain2punycode(domain)
    for i in request("GET", "ListSites", {})["Sites"]:
        if domain2punycode(i["SiteName"]) == domainPunycode:
            return i["SiteId"]
    raise ValueError(
        "无法搜索到域名%s" % domain
    )

def search_recordid(sub_domain: str, siteid: int) -> int:
    domainPunycode = domain2punycode(sub_domain)
    params = {
        "SiteId": siteid,
        "PageSize": 500
    }
    for i in request("GET", "ListRecords", params)["Records"]:
        if domain2punycode(i["RecordName"]) == domainPunycode:
            return i["RecordId"]
    raise ValueError(
        "无法搜索到前缀%s" % sub_domain
    )

def search_configid(sub_domain: str, siteid: int) -> int:
    domainPunycode = domain2punycode(sub_domain)
    params = {
        "SiteId": siteid,
        "PageSize": 500
    }
    for i in request("GET", "ListOriginRules", params)["Configs"]:
        if domain2punycode(i.get("RuleName", "")) == domainPunycode:
            return i["ConfigId"]
    raise ValueError(
        "无法搜索到前缀%s" % sub_domain
    )

def update_ip(ip: str):
    sub_domain = __sub_domain
    domain = __domain
    siteid = search_siteid(domain)
    recordid = search_recordid(f"{sub_domain}.{domain}", siteid)
    payload = {
        "RecordId": recordid,
        "Data": {
            "Value": ip
        }
    }
    return request("POST", "UpdateRecord", payload)

def update_port(port: int):
    sub_domain = __sub_domain
    domain = __domain
    siteid = search_siteid(domain)
    configid = search_configid(sub_domain, siteid)
    payload = {
        "SiteId": siteid,
        "ConfigId": configid,
        "OriginHttpPort": port,
        "OriginHttpsPort": port
    }
    return request("POST", "UpdateOriginRule", payload)
