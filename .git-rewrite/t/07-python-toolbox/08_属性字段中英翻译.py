# -*- coding: utf-8 -*-
import arcpy
import requests
import hashlib
import random

# =================== 参数设置 ===================
fc = r"学习用\审图号：GS(2024)0650\河南省\dijishi.shp"
field_to_translate = "name"   # 要翻译的字段
lang = "en"                   # "zh" 中文，"en" 英文
appid = "<你的百度翻译 APPID>"   # 你的百度翻译 APPID
secretKey = "<你的百度翻译密钥>"  # 你的百度翻译密钥
out_field = field_to_translate + "_" + lang

# =================== 检查字段 ===================
field_names = [f.name for f in arcpy.ListFields(fc)]
if out_field not in field_names:
    arcpy.AddMessage("创建新字段: {}".format(out_field))
    arcpy.AddField_management(fc, out_field, "TEXT", field_length=255)

# =================== 百度翻译函数 ===================
def baidu_translate(query, from_lang="auto", to_lang="zh"):
    url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    salt = str(random.randint(32768, 65536))
    sign = appid + query + salt + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    params = {
        'q': query,
        'from': from_lang,
        'to': to_lang,
        'appid': appid,
        'salt': salt,
        'sign': sign
    }
    try:
        r = requests.get(url, params=params)
        result = r.json()
        return result['trans_result'][0]['dst']
    except:
        return query  # 出错时返回原文

# =================== 批量翻译 ===================
with arcpy.da.UpdateCursor(fc, [field_to_translate, out_field]) as cursor:
    for row in cursor:
        if row[0]:
            translated = baidu_translate(str(row[0]), "auto", lang)
            row[1] = translated
            cursor.updateRow(row)
            print(f"{row[0]} -> {translated}")

print(f"翻译完成，结果已写入字段: {out_field}")
