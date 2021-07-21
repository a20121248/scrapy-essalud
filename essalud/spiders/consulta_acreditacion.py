# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
import scrapy
from essalud.captcha_solve import captchaSolve
from essalud.items import AfiliadoItem
from PIL import Image
import io
import numpy as np
from joblib import load
from datetime import datetime

class ConsultaAcreditacionSpider(scrapy.Spider):
    name = 'consulta_acreditacion'
    YYYYMMDD_HHMMSS = datetime.now().strftime("%Y%m%d_%H%M%S")

    def __init__(self, *args, **kwargs):
        super(ConsultaAcreditacionSpider, self).__init__(*args, **kwargs)
        self.in_path = './1_INPUT/'
        self.out_path = './2_OUTPUT/'
        self.search_URL = 'http://ww4.essalud.gob.pe:7777/acredita/servlet/Ctrlwacre'
        self.captcha_URL = 'http://ww4.essalud.gob.pe:7777/acredita/captcha.jpg'
        self.model = load('essalud/modelCaptcha.joblib')

        # INPUT
        dtype = {'DNI': str}
        self.input_df = pd.read_csv(self.in_path+self.filename, sep='\t', usecols=['DNI'], dtype=dtype, encoding='utf8')

    def start_requests(self):
        for row_idx, row in self.input_df.iterrows():
            meta = {
                'dni': row['DNI'],
                'cookiejar': row_idx + 1
            }
            yield scrapy.Request(url=self.captcha_URL, meta=meta, callback=self.parse, dont_filter=True)

    def parse(self, response):
        dni = response.meta.get('dni')
        
        imgBytes = response.body
        img = Image.open(io.BytesIO(imgBytes))
        
        open_cv_image = np.array(img)
        open_cv_image = open_cv_image[:, :, ::-1].copy()

        captchaValue = captchaSolve(open_cv_image, self.model).testingModel()
        
        formdata = {
            'pg': '1',
            'll': 'Libreta Electoral/DNI',
            'td': '1',
            'nd': dni,
            'submit': 'Consultar',
            'captchafield_doc': captchaValue
        }        
        meta = {
            'cookiejar': response.meta.get('cookiejar'),
            'dni': dni
        }
        yield scrapy.FormRequest(self.search_URL, formdata=formdata, callback=self.parseWeb, meta=meta, dont_filter=True)
        
    def parseWeb(self, response):
        con = response.meta.get('cookiejar')
        dni = response.meta.get('dni')
        
        #print(con, dni)
        
        item = AfiliadoItem()
        
        if 'codigo es incorrecto' in response.text:
            
            yield scrapy.Request(url=self.captcha_URL, callback=self.parse, meta={'cookiejar':con,'dni':dni}, dont_filter=True)
            
            return "bad captcha"
        
        elif 'Error al obtener el detalle del asegurado' in response.text or 'No se encontro Datos con los criterios de busqueda indicados' in response.text:
            
            yield scrapy.Request(url=self.captcha_URL, callback=self.parse, meta={'cookiejar':con,'dni':dni}, dont_filter=True)
            
            return "taking a rest"
        
        elif 'No se encontraron registros' in response.text or 'Se encontró más de un resultado' in response.text:
            
            item['dni'] = dni#encrypt(dni,'az_berl')
            item['name'] = '-'
            item['insuredType'] = '-'
            item['code'] = '-'
            item['insuranceType'] = '-'
            item['attentionCenter'] = '-'
            item['dateFrom'] = '-'
            item['dateTo'] = '-'
            item['address'] = '-'
            item['affiliated'] = '-'
            item['businessName'] = ''
            
            yield item
            
            return 'no info'
        
        resultList = response.css('td[class="tdDetRigth"]').css('::text').extract()
        headerList = response.css('td[class="tdDetLeft"]').css('::text').extract()
        
        resultList = list(map(lambda x: x.replace('\r\n','').strip(), resultList))
        headerList = list(map(lambda x: x.replace('\r\n','').strip(), headerList))
        
        #print(resultList)
        
        resultList.pop(4)
        
        if '(*)' in resultList:
            resultList.pop(8)
        
        resultList = [a for a in resultList if a!='(*)']
        headerList = [b for b in headerList if b!='(*)' and b!='']
        
        #print(resultList)
        #print(headerList)
        
        #print(dict(zip(headerList, resultList)))
        
        #return 'stop'
        
        #if len(resultList) != len(headerList):
         #   headerList.remove('Desde')
          #  headerList.remove('Hasta')
            
        resultDict = dict(zip(headerList, resultList))
        
        
        item['dni'] = dni#encrypt(dni,'az_berl')
        item['name'] = resultDict.get('Nombres')
        item['insuredType'] = resultDict.get('Tipo de Asegurado')
        item['code'] = resultDict.get('Autogenerado')
        item['insuranceType'] = resultDict.get('Tipo de Seguro')
        item['attentionCenter'] = resultDict.get('Centro Asistencial')
        item['dateFrom'] = resultDict.get('Desde')
        item['dateTo'] = resultDict.get('Hasta')
        item['address'] = resultDict.get('Dirección C.A.')
        item['affiliated'] = resultDict.get('Afiliado(a) a')
        item['businessName'] = resultDict.get('Razón Social EPS')        
        yield item