# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    int_or_none,
)


class AolIE(InfoExtractor):
    IE_NAME = 'on.aol.com'
    _VALID_URL = r'(?:aol-video:|https?://on\.aol\.com/video/.*-)(?P<id>[^/?-]+)'

    _TESTS = [{
        'url': 'http://on.aol.com/video/u-s--official-warns-of-largest-ever-irs-phone-scam-518167793?icid=OnHomepageC2Wide_MustSee_Img',
        'md5': '18ef68f48740e86ae94b98da815eec42',
        'info_dict': {
            'id': '518167793',
            'ext': 'mp4',
            'title': 'U.S. Official Warns Of \'Largest Ever\' IRS Phone Scam',
            'description': 'A major phone scam has cost thousands of taxpayers more than $1 million, with less than a month until income tax returns are due to the IRS.',
            'timestamp': 1395405060,
            'upload_date': '20140321',
            'uploader': 'Newsy Studio',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        }
    }, {
        'url': 'http://on.aol.com/video/netflix-is-raising-rates-5707d6b8e4b090497b04f706?context=PC:homepage:PL1944:1460189336183',
        'info_dict': {
            'id': '5707d6b8e4b090497b04f706',
            'ext': 'mp4',
            'title': 'Netflix is Raising Rates',
            'description': 'Netflix is rewarding millions of it’s long-standing members with an increase in cost. Veuer’s Carly Figueroa has more.',
            'upload_date': '20160408',
            'timestamp': 1460123280,
            'uploader': 'Veuer',
        },
        'params': {
            # m3u8 download
            'skip_download': True,
        }
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        response = self._download_json(
            'https://feedapi.b2c.on.aol.com/v1.0/app/videos/aolon/%s/details' % video_id,
            video_id)['response']
        if response['statusText'] != 'Ok':
            raise ExtractorError('%s said: %s' % (self.IE_NAME, response['statusText']), expected=True)

        video_data = response['data']
        formats = []
        m3u8_url = video_data.get('videoMasterPlaylist')
        if m3u8_url:
            formats.extend(self._extract_m3u8_formats(
                m3u8_url, video_id, 'mp4', m3u8_id='hls', fatal=False))
        for rendition in video_data.get('renditions', []):
            video_url = rendition.get('url')
            if not video_url:
                continue
            ext = rendition.get('format')
            if ext == 'm3u8':
                formats.extend(self._extract_m3u8_formats(
                    video_url, video_id, 'mp4', m3u8_id='hls', fatal=False))
            else:
                f = {
                    'url': video_url,
                    'format_id': rendition.get('quality'),
                }
                mobj = re.search(r'(\d+)x(\d+)', video_url)
                if mobj:
                    f.update({
                        'width': int(mobj.group(1)),
                        'height': int(mobj.group(2)),
                    })
                formats.append(f)
        self._sort_formats(formats, ('width', 'height', 'tbr', 'format_id'))

        return {
            'id': video_id,
            'title': video_data['title'],
            'duration': int_or_none(video_data.get('duration')),
            'timestamp': int_or_none(video_data.get('publishDate')),
            'view_count': int_or_none(video_data.get('views')),
            'description': video_data.get('description'),
            'uploader': video_data.get('videoOwner'),
            'formats': formats,
        }


class AolFeaturesIE(InfoExtractor):
    IE_NAME = 'features.aol.com'
    _VALID_URL = r'https?://features\.aol\.com/video/(?P<id>[^/?#]+)'

    _TESTS = [{
        'url': 'http://features.aol.com/video/behind-secret-second-careers-late-night-talk-show-hosts',
        'md5': '7db483bb0c09c85e241f84a34238cc75',
        'info_dict': {
            'id': '519507715',
            'ext': 'mp4',
            'title': 'What To Watch - February 17, 2016',
        },
        'add_ie': ['FiveMin'],
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)
        return self.url_result(self._search_regex(
            r'<script type="text/javascript" src="(https?://[^/]*?5min\.com/Scripts/PlayerSeed\.js[^"]+)"',
            webpage, '5min embed url'), 'FiveMin')
