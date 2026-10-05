"""Opt-in app-owned macOS generic-password items, never shell arguments/files.

The operating system may ask the user to unlock/allow Keychain access. Denial is
an error, never a fallback to plaintext. Existing Passwords entries are untouched.
"""
import ctypes as c
import hashlib
import json
import sys


class KeychainUnavailable(ValueError):
    def __init__(self): super().__init__('macos_keychain_unavailable')


def item_key(source, tenant, actor, account):
    parts=(source,tenant,actor,account)
    if (source not in ('confluence','jira','slack','drive','deepseek')
            or any(not isinstance(v,str) or not 1<=len(v)<=512
                   or any(ord(ch)<32 for ch in v) for v in parts)):
        raise ValueError('Invalid credential store mapping')
    digest=hashlib.sha256(json.dumps(parts,ensure_ascii=False).encode()).hexdigest()
    return ('AI-Bang2 pilot v1 / '+source).encode(),digest.encode()


class MacKeychain:
    def __init__(self):
        if sys.platform!='darwin': raise KeychainUnavailable()
        try:
            self.sec=c.CDLL('/System/Library/Frameworks/Security.framework/Security')
            self.cf=c.CDLL('/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation')
            p=c.c_void_p; u=c.c_uint32
            signatures={
                'SecKeychainFindGenericPassword':[p,u,c.c_char_p,u,c.c_char_p,c.POINTER(u),c.POINTER(p),c.POINTER(p)],
                'SecKeychainAddGenericPassword':[p,u,c.c_char_p,u,c.c_char_p,u,p,c.POINTER(p)],
                'SecKeychainItemModifyAttributesAndData':[p,p,u,p],
                'SecKeychainItemFreeContent':[p,p],
                'SecKeychainItemDelete':[p]}
            for name,args in signatures.items():
                f=getattr(self.sec,name);f.argtypes=args;f.restype=c.c_int32
            self.cf.CFRelease.argtypes=[p];self.cf.CFRelease.restype=None
        except Exception: raise KeychainUnavailable() from None

    def get(self,source,tenant,actor,account):
        service,key=item_key(source,tenant,actor,account)
        size=c.c_uint32();data=c.c_void_p()
        status=self.sec.SecKeychainFindGenericPassword(None,len(service),service,len(key),key,c.byref(size),c.byref(data),None)
        if status==-25300: return None  # errSecItemNotFound only
        if status!=0: raise KeychainUnavailable()
        try:
            if not data.value or not 0<size.value<=32768: raise KeychainUnavailable()
            return c.string_at(data,size.value).decode('utf-8')
        except (UnicodeError,ValueError): raise KeychainUnavailable() from None
        finally: self.sec.SecKeychainItemFreeContent(None,data)

    def put(self,source,tenant,actor,account,value):
        service,key=item_key(source,tenant,actor,account)
        if not isinstance(value,str) or not value or len(value.encode())>32768:
            raise ValueError('Invalid credential value')
        raw=value.encode();buf=c.create_string_buffer(raw);item=c.c_void_p()
        try:
            status=self.sec.SecKeychainAddGenericPassword(None,len(service),service,len(key),key,len(raw),buf,None)
            if status==-25299:  # errSecDuplicateItem: modify only this exact item
                status=self.sec.SecKeychainFindGenericPassword(None,len(service),service,len(key),key,None,None,c.byref(item))
                if status==0: status=self.sec.SecKeychainItemModifyAttributesAndData(item,None,len(raw),buf)
            if status!=0: raise KeychainUnavailable()
        finally:
            c.memset(buf,0,len(buf))
            if item.value:self.cf.CFRelease(item)

    def delete(self,source,tenant,actor,account):
        service,key=item_key(source,tenant,actor,account);item=c.c_void_p()
        status=self.sec.SecKeychainFindGenericPassword(None,len(service),service,len(key),key,None,None,c.byref(item))
        if status==-25300:return
        if status!=0:raise KeychainUnavailable()
        try:
            if self.sec.SecKeychainItemDelete(item)!=0:raise KeychainUnavailable()
        finally:self.cf.CFRelease(item)


class ReplaceOne:
    """Ignore one saved item for this launch; replace only after new input succeeds."""
    def __init__(self,store,source):self.store,self.source=store,source
    def get(self,source,*mapping):
        return None if source==self.source else self.store.get(source,*mapping)
    def put(self,*args):return self.store.put(*args)
