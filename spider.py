import asyncio
from pathlib import Path
import re
import httpx
import parsel
import requests
from tqdm import tqdm
from csv_manipulation import CSVArranger


class ScrapingComex:
    """ Grabs the last three years (available) of exportation and importation csv files. """

    main_url = 'https://www.gov.br/produtividade-e-comercio-exterior/pt-br/assuntos/comercio-exterior/estatisticas/base-de-dados-bruta'

    def __init__(self, desc_path: str):
        self.exportacao_urls = []
        self.importacao_urls = []
        self.download_urls = []
        self.downloaded_csv_files_dir = desc_path

    async def go(self):
        Path(self.downloaded_csv_files_dir).mkdir(parents=True, exist_ok=True)
        self._get_last_three_years_imp_exp_csv()
        await asyncio.gather(*[self._download_csv(url) for url in self.download_urls])

    def _get_last_three_years_imp_exp_csv(self):
        r = requests.get(self.main_url)
        if r.status_code == 200:
            selector = parsel.Selector(r.text)
            scraped_links_to_down = list(filter(lambda x: x.endswith('.csv') and re.search(r'\d', x), selector.xpath('//a[contains(@href, "ncm")]/@href').getall()))
            if scraped_links_to_down:
                for link in scraped_links_to_down:
                    if 'EXP' in link:
                        self.exportacao_urls.append(link)
                    elif 'IMP' in link:
                        self.importacao_urls.append(link)
                self.download_urls.extend(self.exportacao_urls[-3:])
                self.download_urls.extend(self.importacao_urls[-3:])
            else:
                raise Exception('Please, check the page, perhaps the layout has changed.')
        else:
            raise Exception(f'Http status: {r.status_code}')

    async def _download_csv(self, url: str):
        csv_name = '/'.join((self.downloaded_csv_files_dir, url.split('/').pop()))
        with open(csv_name, 'w') as f:
            async with httpx.AsyncClient(verify=False) as c:
                async with c.stream('GET', url) as r:
                    bar = tqdm(
                        desc=csv_name,
                        mininterval=5,
                        maxinterval=10,
                        total=int(r.headers.get('content-length')),
                        unit='iB', unit_scale=True, unit_divisor=1024)
                    async for chunk in r.aiter_text(chunk_size=1024):
                        size = f.write(chunk)
                        bar.update(size)


if __name__ == '__main__':
    asyncio.run(ScrapingComex(desc_path='downloaded_csv_files').go())
    CSVArranger(path='downloaded_csv_files').go()
