#!/usr/bin/env python3
"""UI regression tests using Playwright + Chromium.

Uses set_content to test the offline app even in a sandbox that disallows local
navigation. Storage tests use an explicit in-memory localStorage double; they do
not claim to verify native cross-session persistence or the live GitHub deployment.
Install test tooling: pip install playwright && playwright install chromium
Run: python tests/test_lab.py
"""
import json
import os
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'docs/index.html').read_text(encoding='utf-8')
RESULTS = []

def passed(name):
    RESULTS.append(name)
    print('PASS:', name, flush=True)

def main():
    with sync_playwright() as playwright:
        executable = os.environ.get('CHROMIUM_PATH') or shutil.which('chromium')
        options = {'headless': True, 'args': ['--no-sandbox']}
        if executable:
            options['executable_path'] = executable
        browser = playwright.chromium.launch(**options)
        errors = []
        requests = []
        def page_new(width=1440, reduced=False, storage=None):
            page = browser.new_page(viewport={'width': width, 'height': 1000}, reduced_motion='reduce' if reduced else 'no-preference')
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('request', lambda req: requests.append(req.url))
            if storage is not None:
                page.evaluate('''(entries) => {
                  const data = new Map(Object.entries(entries));
                  Object.defineProperty(window, 'localStorage', { configurable:true, value: {
                    getItem:key => data.has(key) ? data.get(key) : null,
                    setItem:(key,value) => data.set(key,String(value)),
                    removeItem:key => data.delete(key)
                  }});
                  window.__testStorage = data;
                }''', storage)
            page.set_content(HTML)
            expect(page.locator('#score')).to_be_visible()
            return page

        page = page_new(storage={})
        expect(page.locator('#score')).to_have_text('0 / 4')
        page.locator('[data-verdict="aligned"]').click()
        expect(page.locator('#score')).to_have_text('0 / 4')
        page.locator('[data-verdict="mismatch"]').click()
        expect(page.locator('#score')).to_have_text('1 / 4')
        expect(page.locator('#trace')).to_contain_text('300')
        page.locator('[data-verdict="mismatch"]').click()
        expect(page.locator('#score')).to_have_text('1 / 4')
        passed('Doksima : écart recalculé, mauvais choix refusé, score idempotent')
        page.locator('#doc-case').select_option('missing')
        page.locator('[data-verdict="mismatch"]').click()
        expect(page.locator('#trace')).to_contain_text('Abstention requise')
        page.locator('[data-verdict="abstain"]').click()
        expect(page.locator('#trace')).to_contain_text('Aucun verdict forcé')
        page.locator('#doc-case').select_option('aligned')
        page.locator('[data-verdict="aligned"]').click()
        expect(page.locator('#trace')).to_contain_text('pas de garantie d’authenticité')
        passed('Doksima : concordance et pièce absente')

        page.locator('[data-station="agentflow"]').click()
        page.locator('#run-flow').click()
        expect(page.locator('#resume-flow')).to_be_visible(timeout=6000)
        expect(page.locator('.pipeline .finished')).to_have_count(1)
        expect(page.locator('.pipeline .failed')).to_have_count(1)
        page.locator('#resume-flow').click()
        expect(page.locator('#score')).to_have_text('2 / 4', timeout=6000)
        expect(page.locator('.pipeline .finished')).to_have_count(4)
        plan_count = page.locator('#trace li').filter(has_text='Planification…').count()
        assert plan_count == 1, f'Planification repeated: {plan_count}'
        passed('AgentFlow : panne, checkpoint, reprise sans répéter le plan')

        page.locator('[data-station="echotrust"]').click()
        expect(page.locator('#publish-draft')).to_be_disabled()
        page.locator('#generate-draft').click()
        expect(page.locator('#trace')).to_contain_text('BLOQUÉ')
        expect(page.locator('#human-review')).to_be_disabled()
        page.locator('#unsafe-promise').uncheck()
        page.locator('#generate-draft').click()
        expect(page.locator('#publish-draft')).to_be_disabled()
        page.locator('#human-review').check()
        expect(page.locator('#publish-draft')).to_be_enabled()
        page.locator('#publish-draft').click()
        expect(page.locator('#score')).to_have_text('3 / 4')
        page.locator('#unsafe-promise').check()
        expect(page.locator('#publish-draft')).to_be_disabled()
        passed('EchoTrust : promesse bloquée, revue obligatoire, invalidation après modification')

        page.locator('[data-station="pixellight"]').click()
        page.locator('#run-router').click()
        expect(page.locator('#score')).to_have_text('4 / 4', timeout=6000)
        expect(page.locator('#trace')).to_contain_text('B sélectionné')
        expect(page.locator('#pixel-output i')).to_have_count(80)
        expect(page.locator('#success')).to_be_visible()
        passed('PixelLight : panne de A, repli B, budget respecté, mosaïque locale')
        page.locator('#budget').fill('1')
        page.locator('#run-router').click()
        expect(page.locator('#trace')).to_contain_text('B trop coûteux', timeout=5000)
        expect(page.locator('#pixel-output')).to_be_hidden()
        page.locator('#provider-failure').uncheck()
        page.locator('#run-router').click()
        expect(page.locator('#trace')).to_contain_text('A sélectionné', timeout=5000)
        passed('PixelLight : budget insuffisant et fournisseur primaire disponible')

        saved = page.evaluate('Object.fromEntries(window.__testStorage)')
        restored = page_new(storage=saved)
        expect(restored.locator('#score')).to_have_text('4 / 4')
        restored.once('dialog', lambda dialog: dialog.accept())
        restored.locator('#reset').click()
        expect(restored.locator('#score')).to_have_text('0 / 4')
        assert restored.evaluate('window.__testStorage.size') == 0
        passed('Sauvegarde, restauration et réinitialisation avec doublure de stockage explicite')
        restored.close()

        page.locator('[data-station="agentflow"]').click()
        page.locator('#worker-failure').uncheck()
        page.locator('#run-flow').click()
        page.locator('[data-station="echotrust"]').click()
        page.wait_for_timeout(2200)
        expect(page.locator('#mission-name')).to_have_text('EchoTrust')
        expect(page.locator('#trace')).not_to_contain_text('Workflow terminé')
        passed('Changement de station : les anciens traitements asynchrones sont annulés')

        page.locator('#scene').focus()
        before = int(page.locator('#coord-x').inner_text())
        page.keyboard.down('ArrowRight'); page.wait_for_timeout(400); page.keyboard.up('ArrowRight')
        page.wait_for_timeout(250)
        after = int(page.locator('#coord-x').inner_text())
        assert after > before, (before, after)
        passed('Déplacement au clavier et coordonnées mises à jour')
        page.close()

        blocked = page_new()  # about:blank denies native storage; fallback must work.
        blocked.locator('[data-verdict="mismatch"]').click()
        expect(blocked.locator('#score')).to_have_text('1 / 4')
        passed('Jeu utilisable même lorsque le stockage est indisponible')
        blocked.close()
        malformed = page_new(storage={'billel-agent-lab.v1': '{broken'})
        expect(malformed.locator('#score')).to_have_text('0 / 4')
        malformed.close()
        invalid = page_new(storage={'billel-agent-lab.v1': '["doksima","unknown",42,"doksima"]'})
        expect(invalid.locator('#score')).to_have_text('1 / 4')
        invalid.close()
        passed('Stockage corrompu ou identifiants inconnus ignorés')

        reduced = page_new(reduced=True)
        expect(reduced.locator('#motion')).to_have_attribute('aria-pressed', 'true')
        reduced.locator('#motion').click()
        expect(reduced.locator('#motion')).to_have_attribute('aria-pressed', 'false')
        reduced.close()
        passed('Préférence de mouvement réduit et bouton de pause')

        for width in (320, 390, 768, 1024, 1440):
            responsive = page_new(width=width)
            assert not responsive.evaluate('document.documentElement.scrollWidth > innerWidth'), f'Horizontal overflow at {width}'
            for station, title in [('agentflow', 'AgentFlow'), ('echotrust', 'EchoTrust'), ('pixellight', 'PixelLight'), ('doksima', 'Doksima')]:
                responsive.locator(f'[data-station="{station}"]').click()
                expect(responsive.locator('#mission-name')).to_have_text(title)
                assert not responsive.evaluate('document.documentElement.scrollWidth > innerWidth'), f'{station}: overflow at {width}'
            if width == 390:
                expect(responsive.locator('.touch-controls')).to_be_visible()
                responsive.locator('#scene').scroll_into_view_if_needed()
                x_before = int(responsive.locator('#coord-x').inner_text())
                button = responsive.locator('[data-dir="ArrowRight"]')
                # Actual mouse pointer dispatch to exercise the same pointer handlers.
                box = button.bounding_box()
                responsive.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2)
                responsive.mouse.down(); responsive.wait_for_timeout(300); responsive.mouse.up()
            responsive.close()
            passed(f'Affichage et sélection des 4 stations à {width}px, sans débordement horizontal')
        assert not errors, errors
        assert not requests, requests
        passed('Aucune erreur JavaScript et aucune requête réseau durant les tests')
        version = browser.version
        browser.close()
    report = {'browser': f'Chromium {version}', 'passed_groups': len(RESULTS), 'tests': RESULTS,
              'limits': ['Rendu en mémoire via set_content ; pas de navigation file:// ou HTTP locale dans ce bac à sable.',
                         'Persistance testée avec une doublure explicite ; persistance native intersessions non testée ici.',
                         'Publication GitHub Pages et rendu réel du README non testés avant mise en ligne.',
                         'Pas de test Safari/Firefox ni d’audit complet d’accessibilité.']}
    (ROOT / 'tests/last-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\n{len(RESULTS)} test groups passed on Chromium {version}.')

if __name__ == '__main__':
    main()
