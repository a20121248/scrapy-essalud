# -*- coding: utf-8 -*-

import pandas as pd
from essalud.items import AfiliadoItem

class csvWriterPipeline(object):
    out_path = './2_OUTPUT/'
    items_written_infogeneral = 0

    def open_spider(self, spider):
        spider_name = type(spider).__name__
        if spider_name == 'ConsultaAcreditacionSpider':
            self.ctd_save_infogeneral = 5
            self.columnsPrincipal = ['dni','name','insuredType','code','insuranceType','attentionCenter','address','affiliated','businessName','dateFrom','dateTo']
            self.prename_infogeneral = f"{self.out_path}{getattr(spider, 'filename').split('.')[0]}_{getattr(spider, 'YYYYMMDD_HHMMSS')}.txt"
        self.data_encontrada_infogeneral = []

    def process_item(self, item, spider):
        if isinstance(item, AfiliadoItem):
            item_df = pd.DataFrame([item], columns=item.keys())
        
        self.items_written_infogeneral += 1
        self.data_encontrada_infogeneral.append(item_df)
        if self.items_written_infogeneral % self.ctd_save_infogeneral == 0:
            self.data_encontrada_infogeneral = self.guarda_data(self.data_encontrada_infogeneral, self.items_written_infogeneral)
        return item

    def guarda_data(self, lista_df, ctd_items=0):
        pd.concat(lista_df).to_csv(self.prename_infogeneral, sep='\t', header=ctd_items<=self.ctd_save_infogeneral, index=False, encoding="utf-8", columns=self.columnsPrincipal, mode='a')
        return [pd.DataFrame(columns = self.columnsPrincipal)]

    def __del__(self):
        self.guarda_data(self.data_encontrada_infogeneral, self.items_written_infogeneral)
        print(25*'=','THE END',25*'=')