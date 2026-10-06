def _p(s):
    return [x.strip() for x in s.split(",")]

LOCATIONS = {
    "Toshkent shahri": _p("Bektemir, Chilonzor, Yashnobod, Yakkasaroy, Mirobod, Mirzo Ulug'bek, Olmazor, Sergeli, Shayxontohur, Uchtepa, Yunusobod, Yangihayot"),
    "Toshkent viloyati": _p("Nurafshon shahri, Angren shahri, Bekobod shahri, Chirchiq shahri, Olmaliq shahri, Ohangaron shahri, Yangiyo'l shahri, Bekobod, Bo'ka, Bo'stonliq, Chinoz, Qibray, Ohangaron, Oqqo'rg'on, Parkent, Piskent, Quyi Chirchiq, O'rta Chirchiq, Yangiyo'l, Yuqori Chirchiq, Zangiota, Toshkent"),
    "Andijon viloyati": _p("Andijon shahri, Xonobod shahri, Andijon, Asaka, Baliqchi, Bo'z, Buloqboshi, Izboskan, Jalaquduq, Xo'jaobod, Qo'rg'ontepa, Marhamat, Oltinko'l, Paxtaobod, Shahrixon, Ulug'nor"),
    "Buxoro viloyati": _p("Buxoro shahri, Kogon shahri, Buxoro, Vobkent, G'ijduvon, Jondor, Kogon, Olot, Peshku, Romitan, Shofirkon, Qorako'l, Qorovulbozor"),
    "Farg'ona viloyati": _p("Farg'ona shahri, Marg'ilon shahri, Qo'qon shahri, Quvasoy shahri, Beshariq, Bag'dod, Buvayda, Dang'ara, Farg'ona, Furqat, O'zbekiston, Oltiariq, Qo'shtepa, Quva, Rishton, So'x, Toshloq, Uchko'prik, Yozyovon"),
    "Jizzax viloyati": _p("Jizzax shahri, Arnasoy, Baxmal, Do'stlik, Forish, G'allaorol, Sharof Rashidov, Mirzacho'l, Paxtakor, Yangiobod, Zomin, Zafarobod, Zarbdor"),
    "Xorazm viloyati": _p("Urganch shahri, Xiva shahri, Bog'ot, Gurlan, Xonqa, Hazorasp, Xiva, Qo'shko'pir, Shovot, Urganch, Yangiariq, Yangibozor, Tuproqqal'a"),
    "Namangan viloyati": _p("Namangan shahri, Chortoq, Chust, Kosonsoy, Mingbuloq, Namangan, Norin, Pop, To'raqo'rg'on, Uchqo'rg'on, Uychi, Yangiqo'rg'on, Davlatobod"),
    "Navoiy viloyati": _p("Navoiy shahri, Zarafshon shahri, Konimex, Qiziltepa, Navbahor, Karmana, Nurota, Tomdi, Uchquduq, Xatirchi"),
    "Qashqadaryo viloyati": _p("Qarshi shahri, Shahrisabz shahri, Chiroqchi, Dehqonobod, G'uzor, Qamashi, Qarshi, Koson, Kasbi, Kitob, Mirishkor, Muborak, Nishon, Shahrisabz, Yakkabog', Ko'kdala"),
    "Samarqand viloyati": _p("Samarqand shahri, Kattaqo'rg'on shahri, Bulung'ur, Ishtixon, Jomboy, Kattaqo'rg'on, Narpay, Nurobod, Oqdaryo, Pastdarg'om, Paxtachi, Payariq, Qo'shrabot, Samarqand, Toyloq, Urgut"),
    "Sirdaryo viloyati": _p("Guliston shahri, Shirin shahri, Yangiyer shahri, Boyovut, Guliston, Mirzaobod, Oqoltin, Sardoba, Sayxunobod, Sirdaryo, Xovos"),
    "Surxondaryo viloyati": _p("Termiz shahri, Angor, Bandixon, Boysun, Denov, Jarqo'rg'on, Muzrabot, Oltinsoy, Qiziriq, Qumqo'rg'on, Sariosiyo, Sherobod, Sho'rchi, Termiz, Uzun"),
    "Qoraqalpog'iston Respublikasi": _p("Nukus shahri, Amudaryo, Beruniy, Bo'zatov, Chimboy, Ellikqal'a, Kegeyli, Mo'ynoq, Nukus, Qanliko'l, Qo'ng'irot, Qorao'zak, Shumanay, Taxtako'pir, To'rtko'l, Xo'jayli, Taxiatosh"),
}
