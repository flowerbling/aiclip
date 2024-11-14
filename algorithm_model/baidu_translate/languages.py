import enum
from typing import Tuple, Union

from .errors import UnknownLanguage


class Lang(enum.Enum):
    # will be replace with real language
    AUTO = 'auto'  # 自动检测

    # Common Languages
    ZH = 'zh'  # 中文(简体)
    EN = 'en'  # 英语
    SPA = 'spa'  # 西班牙语
    ARA = 'ara'  # 阿拉伯语
    FRA = 'fra'  # 法语
    RU = 'ru'  # 俄语

    # More Languages
    JP = 'jp'  # 日语
    TH = 'th'  # 泰语
    KOR = 'kor'  # 韩语
    DE = 'de'  # 德语
    PT = 'pt'  # 葡萄牙语
    IT = 'it'  # 意大利语
    EL = 'el'  # 希腊语
    NL = 'nl'  # 荷兰语
    PL = 'pl'  # 波兰语
    FIN = 'fin'  # 芬兰语
    CS = 'cs'  # 捷克语
    BUL = 'bul'  # 保加利亚语
    DAN = 'dan'  # 丹麦语
    EST = 'est'  # 爱沙尼亚语
    HU = 'hu'  # 匈牙利语
    ROM = 'rom'  # 罗马尼亚语
    SLO = 'slo'  # 斯洛文尼亚语
    SWE = 'swe'  # 瑞典语
    VIE = 'vie'  # 越南语
    YUE = 'yue'  # 中文(粤语)
    CHT = 'cht'  # 中文(繁体)
    WYW = 'wyw'  # 中文(文言文)
    AFR = 'afr'  # 南非荷兰语
    ALB = 'alb'  # 阿尔巴尼亚语
    AMH = 'amh'  # 阿姆哈拉语
    ARM = 'arm'  # 亚美尼亚语
    ASM = 'asm'  # 阿萨姆语
    AST = 'ast'  # 阿斯图里亚斯语
    AZE = 'aze'  # 阿塞拜疆语
    BAQ = 'baq'  # 巴斯克语
    BEL = 'bel'  # 白俄罗斯语
    BEN = 'ben'  # 孟加拉语
    BOS = 'bos'  # 波斯尼亚语
    BUR = 'bur'  # 缅甸语
    CAT = 'cat'  # 加泰罗尼亚语
    CEB = 'ceb'  # 宿务语
    HRV = 'hrv'  # 克罗地亚语
    EPO = 'epo'  # 世界语
    FAO = 'fao'  # 法罗语
    FIL = 'fil'  # 菲律宾语
    GLG = 'glg'  # 加利西亚语
    GEO = 'geo'  # 格鲁吉亚语
    GUJ = 'guj'  # 古吉拉特语
    HAU = 'hau'  # 豪萨语
    HEB = 'heb'  # 希伯来语
    HI = 'hi'  # 印地语
    ICE = 'ice'  # 冰岛语
    IBO = 'ibo'  # 伊博语
    ID = 'id'  # 印尼语
    GLE = 'gle'  # 爱尔兰语
    KAN = 'kan'  # 卡纳达语
    KLI = 'kli'  # 克林贡语
    KUR = 'kur'  # 库尔德语
    LAO = 'lao'  # 老挝语
    LAT = 'lat'  # 拉丁语
    LAV = 'lav'  # 拉脱维亚语
    LIT = 'lit'  # 立陶宛语
    LTZ = 'ltz'  # 卢森堡语
    MAC = 'mac'  # 马其顿语
    MG = 'mg'  # 马拉加斯语
    MAY = 'may'  # 马来语
    MAL = 'mal'  # 马拉雅拉姆语
    MLT = 'mlt'  # 马耳他语
    MAR = 'mar'  # 马拉地语
    NEP = 'nep'  # 尼泊尔语
    NNO = 'nno'  # 新挪威语
    PER = 'per'  # 波斯语
    SRD = 'srd'  # 萨丁尼亚语
    SRP = 'srp'  # 塞尔维亚语(拉丁文)
    SIN = 'sin'  # 僧伽罗语
    SK = 'sk'  # 斯洛伐克语
    SOM = 'som'  # 索马里语
    SWA = 'swa'  # 斯瓦希里语
    TGL = 'tgl'  # 他加禄语
    TGK = 'tgk'  # 塔吉克语
    TAM = 'tam'  # 泰米尔语
    TAT = 'tat'  # 鞑靼语
    TEL = 'tel'  # 泰卢固语
    TR = 'tr'  # 土耳其语
    TUK = 'tuk'  # 土库曼语
    UKR = 'ukr'  # 乌克兰语
    URD = 'urd'  # 乌尔都语
    OCI = 'oci'  # 奥克语
    KIR = 'kir'  # 吉尔吉斯语
    PUS = 'pus'  # 普什图语
    HKM = 'hkm'  # 高棉语
    HT = 'ht'  # 海地语
    NOB = 'nob'  # 书面挪威语
    PAN = 'pan'  # 旁遮普语
    ARQ = 'arq'  # 阿尔及利亚阿拉伯语
    BIS = 'bis'  # 比斯拉马语
    FRN = 'frn'  # 加拿大法语
    HAK = 'hak'  # 哈卡钦语
    HUP = 'hup'  # 胡帕语
    ING = 'ing'  # 印古什语
    LAG = 'lag'  # 拉特加莱语
    MAU = 'mau'  # 毛里求斯克里奥尔语
    MOT = 'mot'  # 黑山语
    POT = 'pot'  # 巴西葡萄牙语
    RUY = 'ruy'  # 卢森尼亚语
    SEC = 'sec'  # 塞尔维亚-克罗地亚语
    SIL = 'sil'  # 西里西亚语
    TUA = 'tua'  # 突尼斯阿拉伯语
    ACH = 'ach'  # 亚齐语
    AKA = 'aka'  # 阿肯语
    ARG = 'arg'  # 阿拉贡语
    AYM = 'aym'  # 艾马拉语
    BAL = 'bal'  # 俾路支语
    BAK = 'bak'  # 巴什基尔语
    BEM = 'bem'  # 本巴语
    BER = 'ber'  # 柏柏尔语
    BHO = 'bho'  # 博杰普尔语
    BLI = 'bli'  # 比林语
    BRE = 'bre'  # 布列塔尼语
    CHR = 'chr'  # 切罗基语
    NYA = 'nya'  # 齐切瓦语
    CHV = 'chv'  # 楚瓦什语
    COR = 'cor'  # 康瓦尔语
    COS = 'cos'  # 科西嘉语
    CRE = 'cre'  # 克里克语
    CRI = 'cri'  # 克里米亚鞑靼语
    DIV = 'div'  # 迪维希语
    ENO = 'eno'  # 古英语
    FRM = 'frm'  # 中古法语
    FRI = 'fri'  # 弗留利语
    FUL = 'ful'  # 富拉尼语
    GLA = 'gla'  # 盖尔语
    LUG = 'lug'  # 卢干达语
    GRA = 'gra'  # 古希腊语
    GRN = 'grn'  # 瓜拉尼语
    HAW = 'haw'  # 夏威夷语
    HIL = 'hil'  # 希利盖农语
    IDO = 'ido'  # 伊多语
    INA = 'ina'  # 因特语
    IKU = 'iku'  # 伊努克提图特语
    JAV = 'jav'  # 爪哇语
    KAB = 'kab'  # 卡拜尔语
    KAL = 'kal'  # 格陵兰语
    KAU = 'kau'  # 卡努里语
    KAS = 'kas'  # 克什米尔语
    KAH = 'kah'  # 卡舒比语
    KIN = 'kin'  # 卢旺达语
    KON = 'kon'  # 刚果语
    KOK = 'kok'  # 孔卡尼语
    LIM = 'lim'  # 林堡语
    LIN = 'lin'  # 林加拉语
    LOJ = 'loj'  # 逻辑语
    LOG = 'log'  # 低地德语
    LOS = 'los'  # 下索布语
    MAI = 'mai'  # 迈蒂利语
    GLV = 'glv'  # 曼克斯语
    MAO = 'mao'  # 毛利语
    MAH = 'mah'  # 马绍尔语
    NBL = 'nbl'  # 南恩德贝莱语
    NEA = 'nea'  # 那不勒斯语
    NQO = 'nqo'  # 西非书面语
    SME = 'sme'  # 北方萨米语
    NOR = 'nor'  # 挪威语
    OJI = 'oji'  # 奥杰布瓦语
    ORI = 'ori'  # 奥里亚语
    ORM = 'orm'  # 奥罗莫语
    OSS = 'oss'  # 奥塞梯语
    PAM = 'pam'  # 邦板牙语
    PAP = 'pap'  # 帕皮阿门托语
    PED = 'ped'  # 北索托语
    QUE = 'que'  # 克丘亚语
    ROH = 'roh'  # 罗曼什语
    RO = 'ro'  # 罗姆语
    SM = 'sm'  # 萨摩亚语
    SAN = 'san'  # 梵语
    SCO = 'sco'  # 苏格兰语
    SHA = 'sha'  # 掸语
    SNA = 'sna'  # 修纳语
    SND = 'snd'  # 信德语
    SOL = 'sol'  # 桑海语
    SOT = 'sot'  # 南索托语
    SYR = 'syr'  # 叙利亚语
    TET = 'tet'  # 德顿语
    TIR = 'tir'  # 提格利尼亚语
    TSO = 'tso'  # 聪加语
    TWI = 'twi'  # 契维语
    UPS = 'ups'  # 高地索布语
    VEN = 'ven'  # 文达语
    WLN = 'wln'  # 瓦隆语
    WEL = 'wel'  # 威尔士语
    FRY = 'fry'  # 西弗里斯语
    WOL = 'wol'  # 沃洛夫语
    XHO = 'xho'  # 科萨语
    YID = 'yid'  # 意第绪语
    YOR = 'yor'  # 约鲁巴语
    ZAZ = 'zaz'  # 扎扎其语
    ZUL = 'zul'  # 祖鲁语
    SUN = 'sun'  # 巽他语
    HMN = 'hmn'  # 苗语
    SRC = 'src'  # 塞尔维亚语(西里尔文)

    @classmethod
    def get_lang_with_cn(cls, lang: str) -> 'Lang':
        lang_dict = {
            '中文(简体)': cls.ZH,
            '英语': cls.EN,
            '西班牙语': cls.SPA,
            '阿拉伯语': cls.ARA,
            '法语': cls.FRA,
            '俄语': cls.RU,
            '日语': cls.JP,
            '泰语': cls.TH,  
            '韩语': cls.KOR,
            '德语': cls.DE, 
            '葡萄牙语': cls.PT,
            '意大利语': cls.IT,
            '希腊语': cls.EL,
            '荷兰语': cls.NL,
            '波兰语': cls.PL,
            '芬兰语': cls.FIN,
            '捷克语': cls.CS,
            '保加利亚语': cls.BUL,
            '丹麦语': cls.DAN,
            '爱沙尼亚语': cls.EST,
            '匈牙利语': cls.HU,
            '罗马尼亚语': cls.ROM,
            '斯洛文尼亚语': cls.SLO,
            '瑞典语': cls.SWE,
            '越南语': cls.VIE,
            '中文(粤语)': cls.YUE,
            '中文(繁体)': cls.CHT,
            '中文(文言文)': cls.WYW,
            '南非荷兰语': cls.AFR,
            '阿尔巴尼亚语': cls.ALB,
            '阿姆哈拉语': cls.AMH,
            '亚美尼亚语': cls.ARM,
            '阿萨姆语': cls.ASM,
            '阿斯图里亚斯语': cls.AST,
            '阿塞拜疆语': cls.AZE,
            '巴斯克语': cls.BAQ,
            '白俄罗斯语': cls.BEL,  
            '孟加拉语': cls.BEN,
            '波斯尼亚语': cls.BOS,
            '缅甸语': cls.BUR,
            '加泰罗尼亚语': cls.CAT,
            '宿务语': cls.CEB,
            '克罗地亚语': cls.HRV,
            '世界语': cls.EPO,
            '法罗语': cls.FAO,
            '菲律宾语': cls.FIL,
            '加利西亚语': cls.GLG,
            '格鲁吉亚语': cls.GEO,
            '古吉拉特语': cls.GUJ,
            '豪萨语': cls.HAU, 
            '希伯来语': cls.HEB,
            '印地语': cls.HI,
            '冰岛语': cls.ICE,
            '伊博语': cls.IBO,
            '印尼语': cls.ID,
            '爱尔兰语': cls.GLE,
            '卡纳达语': cls.KAN,  
            '克林贡语': cls.KLI,
            '库尔德语': cls.KUR,
            '老挝语': cls.LAO,
            '拉丁语': cls.LAT,
            '拉脱维亚语': cls.LAV,
            '立陶宛语': cls.LIT,
            '卢森堡语': cls.LTZ,
            '马其顿语': cls.MAC,
            '马拉加斯语': cls.MG, 
            '马来语': cls.MAY,
            '马拉雅拉姆语': cls.MAL,
            '马耳他语': cls.MLT,
            '马拉地语': cls.MAR,
            '尼泊尔语': cls.NEP,
            '新挪威语': cls.NNO,
            '波斯语': cls.PER,
            '萨丁尼亚语': cls.SRD,
            '塞尔维亚语(拉丁文)': cls.SRP,
            '僧伽罗语': cls.SIN,
            '斯洛伐克语': cls.SK,
            '索马里语': cls.SOM,
            '斯瓦希里语': cls.SWA,
            '他加禄语': cls.TGL,
            '塔吉克语': cls.TGK,
            '泰米尔语': cls.TAM,
            '鞑靼语': cls.TAT,
            '泰卢固语': cls.TEL,
            '土耳其语': cls.TR,
            '土库曼语': cls.TUK,
            '乌克兰语': cls.UKR,
            '乌尔都语': cls.URD,
            '奥克语': cls.OCI,  
            '吉尔吉斯语': cls.KIR,
            '普什图语': cls.PUS,
            '高棉语': cls.HKM,
            '海地语': cls.HT,
            '书面挪威语': cls.NOB,
            '旁遮普语': cls.PAN,
            '阿尔及利亚阿拉伯语': cls.ARQ,
            '比斯拉马语': cls.BIS,
            '加拿大法语': cls.FRN,
                '哈卡钦语': cls.HAK,
                '胡帕语': cls.HUP,
                '印古什语': cls.ING,
                '拉特加莱语': cls.LAG,
                '毛里求斯克里奥尔语': cls.MAU,
                '黑山语': cls.MOT,
                '巴西葡萄牙语': cls.POT,
                '卢森尼亚语': cls.RUY,
                '塞尔维亚-克罗地亚语': cls.SEC,
                '西里西亚语': cls.SIL,
                '突尼斯阿拉伯语': cls.TUA,
                '亚齐语': cls.ACH,
                '阿肯语': cls.AKA,
                '阿拉贡语': cls.ARG,
                '艾马拉语': cls.AYM,
                '俾路支语': cls.BAL,
                '巴什基尔语': cls.BAK,
                '本巴语': cls.BEM,
                '柏柏尔语': cls.BER,
                '博杰普尔语': cls.BHO,
                '比林语': cls.BLI,
                '布列塔尼语': cls.BRE,
                '切罗基语': cls.CHR,  
                '齐切瓦语': cls.NYA,
                '楚瓦什语': cls.CHV,
                '康瓦尔语': cls.COR,
                '科西嘉语': cls.COS,
                '克里克语': cls.CRE,  
                '克里米亚鞑靼语': cls.CRI,
                '迪维希语': cls.DIV,
                '古英语': cls.ENO,
                '中古法语': cls.FRM,
                '弗留利语': cls.FRI, 
                '富拉尼语': cls.FUL,
                '盖尔语': cls.GLA,
                '卢干达语': cls.LUG,
                '古希腊语': cls.GRA,
                '瓜拉尼语': cls.GRN,
                '夏威夷语': cls.HAW,
                '希利盖农语': cls.HIL,  
                '伊多语': cls.IDO,
                '因特语': cls.INA,
                '伊努克提图特语': cls.IKU,
                '爪哇语': cls.JAV,
                '卡拜尔语': cls.KAB,
                '格陵兰语': cls.KAL,
                '卡努里语': cls.KAU,
                '克什米尔语': cls.KAS,
                '卡舒比语': cls.KAH,
                '卢旺达语': cls.KIN,
                '刚果语': cls.KON,
                '孔卡尼语': cls.KOK,
                '林堡语': cls.LIM,
                '林加拉语': cls.LIN,
                '逻辑语': cls.LOJ,
                '低地德语': cls.LOG,
                '下索布语': cls.LOS,
                '迈蒂利语': cls.MAI,
                '曼克斯语': cls.GLV, 
                '毛利语': cls.MAO,
                '马绍尔语': cls.MAH,
                '南恩德贝莱语': cls.NBL,
                '那不勒斯语': cls.NEA,
                '西非书面语': cls.NQO,
                '北方萨米语': cls.SME,
                '挪威语': cls.NOR,
                '奥杰布瓦语': cls.OJI,
                '奥里亚语': cls.ORI,
                '奥罗莫语': cls.ORM,
                '奥塞梯语': cls.OSS, 
                '邦板牙语': cls.PAM, 
                '帕皮阿门托语': cls.PAP,
                '北索托语': cls.PED,
                '克丘亚语': cls.QUE,
                '罗曼什语': cls.ROH,
                '罗姆语': cls.RO,
                '萨摩亚语': cls.SM,
                '梵语': cls.SAN,
                '苏格兰语': cls.SCO,
                '掸语': cls.SHA,
                '修纳语': cls.SNA,
                '信德语': cls.SND,
                '桑海语': cls.SOL,  
                '南索托语': cls.SOT,
                '叙利亚语': cls.SYR,
                '德顿语': cls.TET,
                '提格利尼亚语': cls.TIR,
                '聪加语': cls.TSO,
                '契维语': cls.TWI,
                '高地索布语': cls.UPS,
                '文达语': cls.VEN,  
                '瓦隆语': cls.WLN,
                '威尔士语': cls.WEL,
                '西弗里斯语': cls.FRY,
                '沃洛夫语': cls.WOL,
                '科萨语': cls.XHO,
                '意第绪语': cls.YID,
                '约鲁巴语': cls.YOR,
                '扎扎其语': cls.ZAZ, 
                '祖鲁语': cls.ZUL, 
                '巽他语': cls.SUN,
                '苗语': cls.HMN,
                '塞尔维亚语(西里尔文)': cls.SRC
            }
        return lang_dict.get(lang, cls.AUTO)  # 如果找不到对应语言，返回自动检测

def lang_from_string(string: Union[str, Lang]) -> Lang:
    if isinstance(string, Lang):
        return string

    if string not in Lang._value2member_map_:
        raise UnknownLanguage('Unsupported language ' + string)
    return Lang._value2member_map_[string]


def normalize_language(
    detected: str, fromLang: Union[Lang, str], toLang: Union[Lang, str]
) -> Tuple[Lang, Lang]:
    fromLang = lang_from_string(fromLang)
    toLang = lang_from_string(toLang)

    if fromLang == Lang.AUTO:
        if not detected:
            raise UnknownLanguage(
                'Can\'t detect language, please set `from_` argument.'
            )
        fromLang = lang_from_string(detected)
    if toLang == Lang.AUTO:
        toLang = Lang.EN if fromLang == Lang.ZH else Lang.ZH

    return fromLang, toLang
