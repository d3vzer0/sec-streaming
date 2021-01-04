from ..schema import ResponseModel
import aiohttp

class NVD:
    def __init__(self, params, base_url='https://services.nvd.nist.gov/rest/json/cves/1.0'):
        self.base_url = base_url
        self.params = params
        self._session = None
        self._total_results = None
        self.results = []

    @property
    async def cves(self):
        while self._total_results > len(self.results):
            await self._get(offset=len(self.results))
        return self.results

    async def _get(self, offset=0):
        self.params['startIndex'] = offset
        async with self._session.get(self.base_url, params=self.params) as resp:
            response = await resp.json()
            format_results = ResponseModel(**response)
            self._total_results = format_results.totalResults
            self.results += format_results.result.CVE_Items

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        await self._get(offset=0)
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._session.close()
