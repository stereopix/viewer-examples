#!/usr/bin/env python3

import sys
import re
import json
import urllib.parse
from optparse import OptionParser

def find_images(filename):
    images = []
    pattern = re.compile('<A HREF="index.html\?(.+)"><IMG SRC="(.+)"></A>', re.IGNORECASE)
    with open(filename) as f:
        for line in f:
            m = pattern.search(line)
            if m: images.append(m.groups())
    return images

def find_title(filename):
    pattern = re.compile('<h1.*>(.+)</h1>', re.IGNORECASE)
    with open(filename) as f:
        for line in f:
            m = pattern.search(line)
            if m: return m.group(1)
    return None

def generate_json(images, base=''):
    out = {'media': [], 'meta': {}}
    for img, thumb in images:
        out['media'].append({'url': img, 'url_thumb': thumb})
    out['meta']['url_base'] = base
    with open('list.json', 'w') as f:
        json.dump(out, f, indent='\t')

def generate_viewer_page(images, title, base=''):
    with open('stereopix_viewer.html', 'w') as f:
        f.write('''<!doctype html>
<html>
	<head>
		<meta charset="utf-8">
		<title>Stereoscopic (3D) photo viewer</title>
		<style>
			body {
				background: #eee;
				font-family: 'Open Sans', arial, sans-serif;
				text-align: center;
				margin: 20px 0;
				padding: 0;
			}
			h1, a {
				color: #909;
			}
			iframe {
				box-sizing: border-box;
			}
			.thumbs {
				margin: 12px;
				display: grid;
				grid-template-columns: repeat(auto-fill, 198px);
				grid-gap: 12px;
				justify-content: center;
			}
			.thumbs a {
				width: 190px;
				height: 190px;
				border: 5px solid #fff;
				background: #fff;
				display: flex;
				justify-content: center;
				align-items: center;
			}
			.thumbs a.active {
				border-color: #c00000;
			}
			.thumbs a img {
				margin: 20px;
				max-width: 150px;
			}
		</style>
	</head>
	<body>
''')
        f.write('		<h1>{}</h1>\n'.format(title if title else 'Stereoscopic (3D) photo viewer'))
        f.write('''		<p>Using the viewer of <a href="https://stereopix.net/">Stereopix</a>.</p>

		<script type="text/javascript">
			var current = 0;
			window.addEventListener('message', function(e) {
				if (e.origin == 'https://stereopix.net') {
					var links = document.getElementsByClassName('gallery_link');
					if (e.data.type == 'viewerReady') {
						var json = { "media": [] };
						for (var i = 0; i < links.length; i++) {
							json.media.push({ "url": (new URL(links[i].href, document.location.href)).href });
							links[i]['data-position'] = i;
							links[i].addEventListener('click', function(click_event) {
								click_event.preventDefault();
								e.source.postMessage({ 'stereopix_action': 'goto', 'position': this['data-position'] }, 'https://stereopix.net');
							});
						}
						e.source.postMessage({ 'stereopix_action': 'list_add_json', 'media': json }, 'https://stereopix.net');
					} else if (e.data.type == 'mediumChanged') {
						links[current].classList.remove("active");
						current = e.data.position;
						links[current].classList.add("active");
					}
				}
			});
		</script>

		<iframe title="Stereoscopic (3D) photo viewer" id="stereopix_viewer"
			style="width: 100%; height: 960px; max-height: 100vh; max-width: 100vw; border: 2px solid black; margin: 8px 0;" 
			allowfullscreen="yes" allowvr="yes" allow="fullscreen;xr-spatial-tracking;accelerometer;gyroscope" 
			src="https://stereopix.net/viewer:embed/"></iframe>

		<div class="thumbs">
''')
        for img, thumb in images:
            f.write('			<a class="gallery_link" href="{}"><img src="{}" /></a>\n'.format(base+img, base+thumb))
        f.write('''		</div>
	</body>
</html>''')

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-b", "--base-url", "--base", dest="base", default='', help="Base URL")
    parser.add_option("-i", "--index_m", "--index", dest="index_m", default='index_m.html', help="Path of the index_m.html file")
    o, args = parser.parse_args()

    images = find_images(o.index_m)
    title = find_title(o.index_m)
    generate_json(images, o.base)
    generate_viewer_page(images, title, o.base)
