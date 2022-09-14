import contextlib
import pathlib

from openpyxl import Workbook

from .models import Company


def generate_offers_xlsx(file_path: pathlib.Path | str, company: Company) -> None:
    wb = Workbook(write_only=True)
    with contextlib.closing(wb):
        ws = wb.create_sheet('Товары')
        ws.append(('Название товара', 'SKU', 'Бренд', 'Цена', 'ID складов (можно перечислять несколько через запятую)'))
        for offer in company.offer_set.all():
            store_ids = ','.join(available_store.marketplace_store_id
                                 for available_store in offer.available_stores.all())
            ws.append((offer.name, offer.sku, offer.brand, offer.price, store_ids))
        wb.save(file_path)
