import netrc

__, __, api_key = netrc.netrc().authenticators('openai')
