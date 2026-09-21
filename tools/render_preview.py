#!/usr/bin/env python3
"""Render a README preview from the actual app. Requires Playwright and Pillow."""
import io
import os
from pathlib import Path
import shutil
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PREVIEW_CSS = '''
html{scroll-behavior:auto}.page{padding:0;max-width:1000px;margin:0}
.topbar,.hero,.after-lab,.projects,.closing,footer{display:none}
.lab{width:1000px;margin:0;border-radius:12px;box-shadow:none}
.lab-grid{display:block}.inspector,.world-bottom,.touch-controls{display:none}
.scene{aspect-ratio:1000/580}.lab-top{height:64px;padding:0 23px}
.lab-title{font-size:12px;gap:11px}.lab-icon{font-size:25px}.version{display:none}
.lab-meta{gap:8px}.local-badge{font-size:10px}.icon-btn{display:none}
.world-label{font-size:10px;left:23px;top:17px}
.station{padding:12px 15px}.station-name{font-size:22px;line-height:1.4}
.station-sub{font-size:11px}.station-top,.station-tag,.station-number{font-size:9px}
.station .mini{max-height:58px}.paper b{font-size:10px}.mini-chat>span{font-size:9px}
.mini-chat>b{font-size:8px}.mini-chat strong{font-size:12px}
.station .mini-flow i{width:34px;height:34px;font-size:18px}
.mini-pixels>span{font-size:12px}.scene-coordinates{font-size:8px}
.progress-row{height:84px;min-height:84px;padding:18px 23px;background:#17231d}
.progress-row>div{max-width:none}.progress-title{font:13px var(--mono);color:var(--green)}
.segments{display:none}.progress-row p{display:none}
.progress-row::after{content:'CLIQUEZ POUR JOUER ↗';font:600 12px var(--mono);color:#102318;background:var(--green);padding:12px 16px;border-radius:4px;white-space:nowrap}
'''

def main():
    (ROOT / 'assets').mkdir(exist_ok=True)
    with sync_playwright() as p:
        options = {'headless':True,'args':['--no-sandbox']}
        executable = os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
        if executable: options['executable_path'] = executable
        browser = p.chromium.launch(**options)
        page = browser.new_page(viewport={'width':1100,'height':1000}, device_scale_factor=1)
        page.set_content((ROOT / 'docs/index.html').read_text(encoding='utf-8'))
        page.add_style_tag(content=PREVIEW_CSS)
        page.locator('.lab-title strong').evaluate("node => node.textContent = 'BILLEL HELALI / AGENT LAB'")
        page.locator('#progress-title').evaluate("node => node.textContent = '4 projets. Des agents. À vous de jouer.'")
        page.wait_for_timeout(200)
        frames = []
        for i in range(48):
            if i in (12,24,36):
                station = {12:'agentflow',24:'echotrust',36:'pixellight'}[i]
                page.locator(f'[data-station="{station}"]').click()
                page.locator('#progress-title').evaluate("node => node.textContent = '4 projets. Des agents. À vous de jouer.'")
            data = page.locator('#labo').screenshot(animations='allow')
            frames.append(Image.open(io.BytesIO(data)).convert('RGB'))
            page.wait_for_timeout(100)
        frames[0].save(ROOT / 'assets/agent-lab-preview.png', optimize=True)
        frames[0].save(ROOT / 'assets/agent-lab-preview.webp', save_all=True, append_images=frames[1:], duration=140, loop=0, quality=85, method=5)
        browser.close()
    print('Preview: 48 frames, animated WebP + static PNG.')
    for name in ['agent-lab-preview.webp','agent-lab-preview.png']:
        print(name, (ROOT / 'assets' / name).stat().st_size, 'bytes')

if __name__ == '__main__':
    main()
