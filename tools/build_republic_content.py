#!/usr/bin/env python3
"""Generates full focus trees (20 focuses each) for the 11 non-federal tags, their national spirits
and en/ru localisation. Re-runnable. Edit this script, not the outputs.
Writes: common/national_focus/YGwar_republic_focus.txt
        common/ideas/YGwar_republic_ideas.txt
        localisation/english/YGwar_republics_l_english.yml
        localisation/russian/YGwar_republics_l_russian.yml
Also strips the old 3-focus stub strings from the YGwar_yug_l_*.yml files.
Territory cores in the 'define national territory' focus come from tools/state_republic_map.csv."""
import os, re, csv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAGS = ['SVN', 'CRO', 'BOS', 'SER', 'MNT', 'MAC', 'VOJ', 'KOS', 'RSB', 'RSK', 'HRZ', 'ALB']

# ---------------------------------------------------------------- territory
terr = {}
with open(os.path.join(ROOT, 'tools', 'state_republic_map.csv'), encoding='utf-8') as fh:
    for r in csv.DictReader(fh, delimiter=';'):
        terr[r['tag']] = [int(x) for x in r['state_ids'].split(',')]

terr['ALB'] = list(range(121, 133))     # Albania: states 121..132 (see tools/albania_files.py)

# ---------------------------------------------------------------- shared focus skeleton
# key: (x, y, cost, icon, prerequisites(AND groups; inner tuple = OR), reward kind)
SK = [
    ('consolidate_statehood',     0, 0, 5, 'national_unity',      [],                                   'start'),
    # military branch
    ('build_defence_forces',     -4, 1, 5, 'army_doctrines',      [('consolidate_statehood',)],         'mil1'),
    ('territorial_defence',      -4, 2, 5, 'construct_military',  [('build_defence_forces',)],          'mil2'),
    ('arms_procurement',         -5, 3, 5, 'construct_military',  [('territorial_defence',)],           'mil3'),
    ('border_fortification',     -3, 3, 5, 'army_doctrines',      [('territorial_defence',)],           'mil4'),
    ('professional_army',        -4, 4, 7, 'army_doctrines',      [('arms_procurement', 'border_fortification')], 'mil5'),
    # political branch
    ('seek_recognition',          0, 1, 5, 'political_pressure',  [('consolidate_statehood',)],         'pol1'),
    ('write_constitution',       -1, 2, 5, 'national_unity',      [('seek_recognition',)],              'pol2'),
    ('diplomatic_missions',       1, 2, 5, 'political_pressure',  [('seek_recognition',)],              'pol3'),
    ('national_legitimacy',       0, 3, 7, 'national_unity',      [('write_constitution',), ('diplomatic_missions',)], 'pol4'),
    ('define_national_territory', 0, 4, 7, 'demand_territory',    [('national_legitimacy',)],           'terr'),
    # economic branch
    ('secure_the_economy',        4, 1, 5, 'construct_civilian',  [('consolidate_statehood',)],         'eco1'),
    ('repair_infrastructure',     3, 2, 5, 'construct_civilian',  [('secure_the_economy',)],            'eco2'),
    ('revive_industry',           5, 2, 5, 'construct_civilian',  [('secure_the_economy',)],            'eco3'),
    ('open_trade_routes',         4, 3, 5, 'political_pressure',  [('repair_infrastructure',), ('revive_industry',)], 'eco4'),
    ('national_economy',          4, 4, 7, 'construct_civilian',  [('open_trade_routes',)],             'eco5'),
    # tag-specific capstones
    ('u1',                       -2, 5, 7, 'major_war',           [('professional_army',), ('define_national_territory',)], 'u1'),
    ('u2',                        2, 5, 7, 'construct_civilian',  [('national_economy',), ('define_national_territory',)],  'u2'),
    ('u3',                        0, 5, 7, 'national_unity',      [('define_national_territory',)],     'u3'),
    ('u4',                        0, 6, 10, 'major_war',          [('u1',), ('u2',), ('u3',)],          'u4'),
]

# shared names/descriptions (country-neutral wording so they read correctly for every tag)
SH = {
 'consolidate_statehood': ('Consolidate Statehood', 'Set up the working institutions of the new state: a government, a budget, a police and a postal service.',
                           'Укрепление государственности', 'Наладить работу институтов нового государства: правительство, бюджет, полицию и почту.'),
 'build_defence_forces': ('Build Defence Forces', 'Turn local units and volunteers into a single chain of command.',
                          'Создание сил обороны', 'Свести местные отряды и добровольцев в единую систему командования.'),
 'territorial_defence': ('Territorial Defence', 'Organise reserve units in every municipality so the state is not defenceless on the first day.',
                         'Территориальная оборона', 'Создать резервные части в каждой общине, чтобы государство не осталось беззащитным в первый же день.'),
 'arms_procurement': ('Arms Procurement', 'Take over local depots and look for suppliers willing to sell to a new state.',
                      'Закупка вооружений', 'Принять местные склады и найти поставщиков, готовых продавать оружие новому государству.'),
 'border_fortification': ('Border Fortification', 'Fortify the roads, bridges and passes that decide who can enter the country.',
                          'Укрепление границ', 'Укрепить дороги, мосты и перевалы, которые решают, кто может войти в страну.'),
 'professional_army': ('A Professional Army', 'Replace improvised formations with trained, paid and properly supplied brigades.',
                       'Профессиональная армия', 'Заменить импровизированные формирования обученными, оплачиваемыми и снабжаемыми бригадами.'),
 'seek_recognition': ('Seek Recognition', 'Win acceptance among neighbours and in the capitals that matter.',
                      'Поиск признания', 'Добиться признания у соседей и в столицах, от которых это зависит.'),
 'write_constitution': ('Write a Constitution', 'Define the institutions, the rights of minorities and the source of authority.',
                        'Новая конституция', 'Определить институты, права меньшинств и источник власти.'),
 'diplomatic_missions': ('Diplomatic Missions', 'Open missions abroad and make the case for the new state in person.',
                         'Дипломатические миссии', 'Открыть представительства за рубежом и отстаивать интересы нового государства лично.'),
 'national_legitimacy': ('National Legitimacy', 'Back the new order with elections, public ceremonies and visible results.',
                         'Национальная легитимность', 'Подкрепить новый порядок выборами, публичными церемониями и видимыми результатами.'),
 'define_national_territory': ('Define the National Territory', 'Settle in law what the state considers its own land. All its core territory is confirmed as national.',
                               'Определение национальной территории', 'Закрепить в законе, что государство считает своей землёй. Вся его основная территория подтверждается как национальная.'),
 'secure_the_economy': ('Secure the Economy', 'Keep the banks open, the wages paid and the shops stocked.',
                        'Защита экономики', 'Сохранить работу банков, выплату зарплат и наполненность магазинов.'),
 'repair_infrastructure': ('Repair Infrastructure', 'Restore the roads, rails and power lines that the old federal system left half-finished.',
                           'Восстановление инфраструктуры', 'Починить дороги, железные дороги и линии электропередач, которые прежняя федеральная система оставила недоделанными.'),
 'revive_industry': ('Revive Industry', 'Reconnect factories to raw materials and customers that used to sit in other republics.',
                     'Возрождение промышленности', 'Заново связать заводы с сырьём и покупателями, которые раньше находились в других республиках.'),
 'open_trade_routes': ('Open Trade Routes', 'Replace the federal market with agreements that work across new borders.',
                       'Открытие торговых путей', 'Заменить федеральный рынок договорами, работающими через новые границы.'),
 'national_economy': ('A National Economy', 'Build an economy that stands on its own currency, its own budget and its own plans.',
                      'Национальная экономика', 'Построить экономику, опирающуюся на собственную валюту, собственный бюджет и собственные планы.'),
}

# tag-specific: name (en, ru) + four focuses u1..u4 = (en title, en desc, ru title, ru desc)
TAGINFO = {
 'SVN': (('Slovenia', 'Словения'), [
   ('Alpine Defence Line', 'Use the mountain passes and the short, well-known border to make any intervention costly.',
    'Альпийская оборонительная линия', 'Использовать горные перевалы и короткую, хорошо знакомую границу, чтобы сделать любое вмешательство дорогим.'),
   ('Gateway to Central Europe', 'Tie the economy to Austrian and Italian markets and to the Adriatic ports.',
    'Ворота в Центральную Европу', 'Привязать экономику к австрийскому и итальянскому рынкам и адриатическим портам.'),
   ('Return to Europe', 'Present Slovenia as a settled, democratic state that belongs in the European institutions.',
    'Возвращение в Европу', 'Представить Словению как устоявшееся демократическое государство, которому место в европейских институтах.'),
   ('A Small State, Secured', 'Defence, economy and diplomacy now support each other. The state is small but it holds.',
    'Малое государство, сумевшее устоять', 'Оборона, экономика и дипломатия теперь поддерживают друг друга. Государство невелико, но держится.')]),
 'CRO': (('Croatia', 'Хорватия'), [
   ('Defend the Homeland', 'Mobilise the National Guard and the police and prepare the front lines along the Sava, Una and Danube.',
    'Защита родины', 'Мобилизовать Национальную гвардию и полицию и подготовить линии обороны вдоль Савы, Уны и Дуная.'),
   ('The Adriatic Economy', 'Make the coast, tourism and the shipyards the engine of the economy.',
    'Адриатическая экономика', 'Сделать побережье, туризм и верфи двигателем экономики.'),
   ('Reintegrate the Regions', 'Bring Slavonia, Dalmatia, Istria and the Krajina areas under one administration.',
    'Реинтеграция регионов', 'Объединить Славонию, Далмацию, Истрию и районы Краины в одной системе управления.'),
   ('A Sovereign Croatia', 'The state controls its borders, its coast and its institutions.',
    'Суверенная Хорватия', 'Государство контролирует свои границы, побережье и институты.')]),
 'BOS': (('Bosnia and Herzegovina', 'Босния и Герцеговина'), [
   ('Defend Every Municipality', 'The country is too mixed to defend from one centre. Local commands must hold on their own until reinforced.',
    'Оборона каждой общины', 'Страна слишком смешанная, чтобы обороняться из одного центра. Местные штабы должны держаться самостоятельно до подхода подкреплений.'),
   ('The Sarajevo Corridor', 'Keep roads, rail and the airport open so the capital stays connected to the rest of the country.',
    'Сараевский коридор', 'Сохранить открытыми дороги, железную дорогу и аэропорт, чтобы столица оставалась связанной с остальной страной.'),
   ('Common Institutions', 'Build shared institutions that Bosniaks, Serbs and Croats can all take part in.',
    'Общие институты', 'Создать общие институты, в которых смогут участвовать и боснийцы, и сербы, и хорваты.'),
   ('One Bosnia', 'A single state that includes all its communities, with a government that all of them recognise.',
    'Единая Босния', 'Единое государство, включающее все его общины, с правительством, которое признают все.')]),
 'SER': (('Serbia', 'Сербия'), [
   ('Inherit the Federal Army', 'Take over the garrisons, depots and officer corps that remain after the federation fades.',
    'Наследие федеральной армии', 'Принять гарнизоны, склады и офицерский корпус, остающиеся после угасания федерации.'),
   ('The Danube Economy', 'Rebuild the economy around the Danube, the Morava valley and the railway to the south.',
    'Дунайская экономика', 'Перестроить экономику вокруг Дуная, долины Моравы и железной дороги на юг.'),
   ('Serbs Outside Serbia', 'Define the state\'s relation to Serb communities in neighbouring republics.',
    'Сербы за пределами Сербии', 'Определить отношения государства с сербскими общинами в соседних республиках.'),
   ('The Central Power', 'Serbia becomes the largest and best-organised successor state in the region.',
    'Центральная держава', 'Сербия становится крупнейшим и лучше всех организованным государством-преемником в регионе.')]),
 'MNT': (('Montenegro', 'Черногория'), [
   ('Mountain Defence', 'Rely on rough terrain and clan-based local knowledge to make the country hard to occupy.',
    'Горная оборона', 'Опереться на тяжёлый рельеф и знание местности, чтобы страну было трудно оккупировать.'),
   ('The Coast and the Mountains', 'Develop the ports and the tourist coast alongside upland agriculture.',
    'Побережье и горы', 'Развивать порты и туристическое побережье наряду с горным сельским хозяйством.'),
   ('Heir of an Old State', 'Draw on the memory of Montenegrin independence to strengthen the new state.',
    'Наследник старого государства', 'Опереться на память о независимости Черногории, чтобы укрепить новое государство.'),
   ('Montenegro Stands', 'A small state with a coast, an army and its own foreign policy.',
    'Черногория держится', 'Малое государство с побережьем, армией и собственной внешней политикой.')]),
 'MAC': (('Macedonia', 'Македония'), [
   ('Peaceful Separation', 'Negotiate the withdrawal of federal units and avoid giving anyone a reason to fight.',
    'Мирное размежевание', 'Договориться о выводе федеральных частей и не дать никому повода для боевых действий.'),
   ('The Vardar Axis', 'Develop the Vardar valley corridor that links the north and the south of the country.',
    'Ось Вардара', 'Развить коридор долины Вардара, соединяющий север и юг страны.'),
   ('Balance Between Communities', 'Give Macedonians, Albanians and other communities a stake in the same institutions.',
    'Баланс между общинами', 'Дать македонцам, албанцам и другим общинам долю в одних и тех же институтах.'),
   ('A Stable Macedonia', 'Through caution and compromise the state avoids the wars of its neighbours.',
    'Стабильная Македония', 'Благодаря осторожности и компромиссам государство избегает войн, охвативших соседей.')]),
 'VOJ': (('Vojvodina', 'Воеводина'), [
   ('Plain Defence', 'The open plain offers no natural lines. Mobile reserves and rail links must take their place.',
    'Оборона равнины', 'Открытая равнина не даёт естественных рубежей. Их должны заменить мобильные резервы и железнодорожные связи.'),
   ('Breadbasket of the Balkans', 'Turn agriculture and food processing into the main source of income.',
    'Житница Балкан', 'Сделать сельское хозяйство и переработку продуктов главным источником доходов.'),
   ('Autonomy Restored', 'Reclaim the self-government that Vojvodina held within the federation.',
    'Восстановленная автономия', 'Вернуть самоуправление, которым Воеводина обладала внутри федерации.'),
   ('A Multi-Ethnic Province', 'Hungarians, Serbs, Slovaks, Croats and others share a single administration.',
    'Многонациональная провинция', 'Венгры, сербы, словаки, хорваты и другие живут под единым управлением.')]),
 'KOS': (('Kosovo', 'Косово'), [
   ('Defend the Province', 'Organise local defence and keep the main roads open in a territory with no heavy weapons of its own.',
    'Оборона края', 'Организовать местную оборону и держать открытыми главные дороги на территории без собственного тяжёлого вооружения.'),
   ('Mines and Power', 'Revive the mines and power stations that were once the province\'s main source of industry.',
    'Шахты и энергетика', 'Возродить шахты и электростанции, бывшие главным источником промышленности края.'),
   ('A Voice Abroad', 'Present the case for Kosovo\'s statehood to the diplomatic world.',
    'Голос за рубежом', 'Изложить дипломатическому миру аргументы в пользу государственности Косова.'),
   ('Kosovo Is Heard', 'The state has institutions, a budget and attention from foreign governments.',
    'Косово услышано', 'У государства есть институты, бюджет и внимание иностранных правительств.')]),
 'RSB': (('Republika Srpska', 'Республика Сербская'), [
   ('Army of the Republic', 'Form a unified army from local units and former federal officers.',
    'Армия республики', 'Создать единую армию из местных частей и бывших федеральных офицеров.'),
   ('The Northern Corridor', 'Secure the road and rail links that join the western and eastern parts of the territory.',
    'Северный коридор', 'Обеспечить дорожные и железнодорожные связи между западной и восточной частями территории.'),
   ('Ties with Serbia', 'Build economic and political links with neighbouring Serbia.',
    'Связи с Сербией', 'Выстроить экономические и политические связи с соседней Сербией.'),
   ('A Serb Republic in Bosnia', 'The entity has institutions, an army and a defined territory within Bosnia and Herzegovina.',
    'Сербская республика в Боснии', 'У образования есть институты, армия и определённая территория в Боснии и Герцеговине.')]),
 'RSK': (('Republika Srpska Krajina', 'Республика Сербская Краина'), [
   ('Defend the Krajina', 'Hold the lines in Knin, Banija, Kordun and Lika with a locally raised army.',
    'Оборона Краины', 'Удержать рубежи в Книне, Бании, Кордуне и Лике силами местной армии.'),
   ('Isolated Economy', 'Run an economy cut off from its natural markets and rely on aid from outside.',
    'Экономика в изоляции', 'Вести хозяйство, отрезанное от естественных рынков, и опираться на внешнюю помощь.'),
   ('Link to the Serb Lands', 'Seek political and logistical ties to Serb-populated regions elsewhere.',
    'Связь с сербскими землями', 'Искать политические и логистические связи с регионами, населёнными сербами.'),
   ('The Krajina Stands', 'The territory has its own administration, army and a defined claim.',
    'Краина держится', 'У территории есть собственная администрация, армия и определённая претензия.')]),
 'ALB': (('Albania', 'Албания'), [
   ('The Bunker Network', 'Turn the hundreds of thousands of concrete bunkers into a defence system that someone actually staffs and supplies.',
    'Сеть бункеров', 'Превратить сотни тысяч бетонных бункеров в оборонительную систему, у которой есть гарнизоны и снабжение.'),
   ('Chrome, Oil and Hydropower', 'Sell chromium, oil and electricity to pay for what Albania has never been able to import.',
    'Хром, нефть и гидроэнергия', 'Продавать хром, нефть и электроэнергию, чтобы оплатить то, что Албания никогда не могла ввозить.'),
   ('End of Isolation', 'Open the borders, restore diplomatic ties and let Albanians travel and trade abroad.',
    'Конец изоляции', 'Открыть границы, восстановить дипломатические отношения и разрешить албанцам ездить и торговать за рубежом.'),
   ('Albania Opens', 'The country is no longer closed to the world: it has a defence, an economy and partners.',
    'Албания открыта', 'Страна больше не закрыта от мира: у неё есть оборона, экономика и партнёры.')]),
 'HRZ': (('Herceg-Bosna', 'Герцег-Босна'), [
   ('Croatian Defence Council', 'Organise local Croat units into a coordinated defence force.',
    'Хорватский совет обороны', 'Организовать местные хорватские части в скоординированные силы обороны.'),
   ('The Neretva and the Coast', 'Develop trade through the Neretva valley and links to the Adriatic.',
    'Неретва и побережье', 'Развивать торговлю через долину Неретвы и связи с Адриатикой.'),
   ('Ties with Croatia', 'Seek economic and political links with neighbouring Croatia.',
    'Связи с Хорватией', 'Искать экономические и политические связи с соседней Хорватией.'),
   ('A Croat Entity', 'The entity has its own institutions, its own defence and a defined territory.',
    'Хорватское образование', 'У образования есть собственные институты, собственная оборона и определённая территория.')]),
}

# ---------------------------------------------------------------- reward builders
def rewards(tag, kind):
    n = lambda s: f'{tag}_{s}'
    r = {
        'start': ['add_stability = 0.05', 'add_political_power = 50', f'add_ideas = {n("statehood_spirit")}'],
        'mil1':  ['add_war_support = 0.05', 'YGwar_build_mil = yes'],
        'mil2':  [f'add_ideas = {n("territorial_defence_spirit")}', 'add_war_support = 0.03'],
        'mil3':  ['YGwar_build_mil = yes', 'add_war_support = 0.03'],
        'mil4':  ['YGwar_build_infra = yes', 'add_stability = 0.02'],
        'mil5':  ['add_war_support = 0.05', 'add_political_power = 50'],
        'pol1':  ['add_political_power = 50'],
        'pol2':  ['add_stability = 0.05'],
        'pol3':  ['add_political_power = 75'],
        'pol4':  ['add_stability = 0.05', 'add_political_power = 75'],
        'terr':  ['add_political_power = 50', 'add_war_support = 0.03'] + [f'{s} = {{ add_core_of = {tag} }}' for s in terr[tag]],
        'eco1':  ['add_stability = 0.03', 'YGwar_build_civ = yes'],
        'eco2':  ['YGwar_build_infra = yes', 'YGwar_build_infra = yes'],
        'eco3':  ['YGwar_build_civ = yes', 'YGwar_build_civ = yes'],
        'eco4':  ['add_political_power = 50', 'add_stability = 0.02'],
        'eco5':  [f'add_ideas = {n("national_economy_spirit")}', 'YGwar_build_civ = yes'],
        'u1':    ['add_war_support = 0.05', 'YGwar_build_mil = yes'],
        'u2':    ['add_stability = 0.03', 'YGwar_build_civ = yes', 'YGwar_build_infra = yes'],
        'u3':    ['add_political_power = 100', 'add_stability = 0.03'],
        'u4':    [f'add_ideas = {n("national_resolve")}', 'add_political_power = 100'],
    }
    return r[kind]

def focus_block(tag, key, x, y, cost, icon, pre, kind):
    fid = f'{tag}_{key}'
    L = ['\tfocus = {', f'\t\tid = {fid}', f'\t\ticon = GFX_goal_generic_{icon}',
         f'\t\tx = {x}', f'\t\ty = {y}', f'\t\tcost = {cost}']
    for grp in pre:
        L.append('\t\tprerequisite = { ' + ' '.join(f'focus = {tag}_{p}' for p in grp) + ' }')
    L.append('\t\tai_will_do = { factor = 10 }')
    L.append('\t\tcompletion_reward = {')
    for e in rewards(tag, kind):
        L.append('\t\t\t' + e)
    L.append('\t\t}')
    L.append('\t}')
    return '\n'.join(L)

def build():
    focus_txt = ['# YGwar - full focus trees (20 focuses each) for the 11 non-federal tags.',
                 '# GENERATED by tools/build_republic_content.py - edit the script, not this file.', '']
    ideas_txt = ['# YGwar - national spirits for the 11 non-federal tags. GENERATED by tools/build_republic_content.py.',
                 'ideas = {', '\tcountry = {']
    en = ['\ufeffl_english:']
    ru = ['\ufeffl_russian:']
    def add(k, e, r):
        en.append(f' {k}:0 "{e}"')
        ru.append(f' {k}:0 "{r}"')
    q = lambda s: s.replace('"', "'")
    for tag in TAGS:
        (nen, nru), uniq = TAGINFO[tag]
        focus_txt += ['focus_tree = {', f'\tid = {tag}_focus_tree', '\tcountry = {', '\t\tfactor = 0',
                      f'\t\tmodifier = {{ add = 100 tag = {tag} }}', '\t}', '']
        for key, x, y, cost, icon, pre, kind in SK:
            focus_txt.append(focus_block(tag, key, x, y, cost, icon, pre, kind))
            if key.startswith('u'):
                en_t, en_d, ru_t, ru_d = uniq[int(key[1]) - 1]
            else:
                en_t, en_d, ru_t, ru_d = SH[key]
            add(f'{tag}_{key}', q(en_t), q(ru_t))
            add(f'{tag}_{key}_desc', q(en_d), q(ru_d))
        focus_txt += ['}', '']
        spirits = [
            ('statehood_spirit', 'stability_factor = 0.05 political_power_factor = 0.05', 'generic_pp_unity_bonus',
             'Statehood Spirit', 'The first months of independent institutions give the country a sense of purpose.',
             'Дух государственности', 'Первые месяцы работы собственных институтов дают стране ощущение цели.'),
            ('territorial_defence_spirit', 'army_defence_factor = 0.05 war_support_factor = 0.03', 'generic_manpower_bonus',
             'Territorial Defence', 'Reserve units in every municipality make the country harder to invade.',
             'Территориальная оборона', 'Резервные части в каждой общине затрудняют вторжение в страну.'),
            ('national_economy_spirit', 'industrial_capacity_factory = 0.05 production_speed_buildings_factor = 0.05', 'generic_production_bonus',
             'National Economy', 'The economy now runs on its own budget and its own plans.',
             'Национальная экономика', 'Экономика теперь работает на собственном бюджете и по собственным планам.'),
            ('national_resolve', 'stability_factor = 0.05 war_support_factor = 0.05', 'generic_pp_unity_bonus',
             'National Resolve', 'Defence, economy and diplomacy support each other.',
             'Национальная решимость', 'Оборона, экономика и дипломатия поддерживают друг друга.'),
        ]
        for sid, mod, pic, et, ed, rt, rd in spirits:
            ideas_txt += [f'\t\t{tag}_{sid} = {{', f'\t\t\tpicture = {pic}', '\t\t\tallowed = { always = no }',
                          '\t\t\tremoval_cost = -1', f'\t\t\tmodifier = {{ {mod} }}', '\t\t}']
            add(f'{tag}_{sid}', et, rt)
            add(f'{tag}_{sid}_desc', ed, rd)
    ideas_txt += ['\t}', '}', '']
    def w(rel, text):
        p = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(text)
    w('common/national_focus/YGwar_republic_focus.txt', '\n'.join(focus_txt))
    w('common/ideas/YGwar_republic_ideas.txt', '\n'.join(ideas_txt))
    w('localisation/english/YGwar_republics_l_english.yml', '\n'.join(en) + '\n')
    w('localisation/russian/YGwar_republics_l_russian.yml', '\n'.join(ru) + '\n')
    # strip the old stub strings (SVN_consolidate_statehood etc.) from the yug loc files
    pat = re.compile(r'^ [A-Z]{3}_(consolidate_statehood|build_defence_forces|seek_recognition)(_desc)?:0 ')
    for lang in ('english', 'russian'):
        p = os.path.join(ROOT, 'localisation', lang, f'YGwar_yug_l_{lang}.yml')
        lines = open(p, encoding='utf-8-sig').read().split('\n')
        keep = [l for l in lines if not pat.match(l)]
        with open(p, 'w', encoding='utf-8-sig', newline='\n') as fh:
            fh.write('\n'.join(keep))
        print(lang, 'stub loc lines removed:', len(lines) - len(keep))
    print('ok:', len(TAGS), 'trees x', len(SK), 'focuses')

if __name__ == '__main__':
    build()
