from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, validator, root_validator
import hashlib


class ItemModel(BaseModel):
    cve: Dict
    configurations: Optional[Dict]
    impact: Optional[Dict]
    publishedDate: datetime
    lastModifiedDate: datetime
    fingerprint: str

    @root_validator(pre=True)
    def _get_finterprint(cls, values):
        hex_date = str(values['publishedDate']).encode('utf-8').hex()
        hash = hashlib.blake2b(values['cve']['CVE_data_meta']['ID'].encode('utf-8'),
            digest_size=20).hexdigest()
        values['fingerprint'] = f'{hex_date}{hash}'
        return values

class ResultModel(BaseModel):
    CVE_data_timestamp: datetime
    CVE_data_type: str
    CVE_Items: List[ItemModel]

    @validator('CVE_data_type')
    def fixed_type(cls, v):
        assert v == 'CVE', 'Must be of type CVE'
        return v

class ResponseModel(BaseModel):
    resultsPerPage: int
    startIndex: int
    totalResults: int
    result: ResultModel

