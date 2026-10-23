#!/usr/bin/env python3
"""Slovenia content pass. Writes: common/national_focus/SVN_focus.txt, common/ideas/YGwar_SVN_ideas.txt,
common/scripted_effects/YGwar_SVN_effects.txt, events/YGwar_SVN_events.txt, common/decisions/YGwar_SVN_decisions.txt,
localisation/{english,russian}/YGwar_svn_l_*.yml, characters appended, SVN history spirits, removes SVN stub tree."""
import os, re
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W=lambda p,t: open(os.path.join(ROOT,p),'w',encoding='utf-8').write(t)
R=lambda p: open(os.path.join(ROOT,p),encoding='utf-8-sig').read()
rows=[]  # (key,en,ru)
def rec(n): return f'SVN_add_recognition = {{ VAL = {n} }}'
def pp(n): return f'add_political_power = {n}'
def stab(n): return f'add_stability = {n}'
def war(n): return f'add_war_support = {n}'
def idea(i): return f'add_ideas = {i}'
def flag(x): return f'set_country_flag = {x}'
def ev(n): return f'country_event = {{ id = YGwar_SVN.{n} }}'
def leader(ch,party,fl):
    return (f'recruit_character = {ch}\nif = {{ limit = {{ NOT = {{ has_country_flag = YGwar_regime_set }} }}\n  set_country_flag = YGwar_regime_set\n  set_country_flag = {fl}\n'
            f'  set_politics = {{ ruling_party = {party} }}\n  promote_character = {ch} }}')
CIV='YGwar_build_civ = yes'; MIL='YGwar_build_mil = yes'; INF='YGwar_build_infra = yes'
I={'u':'national_unity','p':'political_pressure','c':'construct_civilian','a':'army_doctrines','m':'construct_military','w':'major_war','d':'demand_territory'}
F=[]
def f(id,x,y,cost,ic,pre=(),orp=(),mx=(),av='',rw=(),en=('',''),ru=('',''),ai=None):
    F.append(dict(id='SVN_'+id,x=x,y=y,cost=cost,icon='GFX_goal_generic_'+I[ic],pre=['SVN_'+p for p in pre],orp=['SVN_'+p for p in orp],mx=['SVN_'+p for p in mx],av=av,rw=list(rw),ai=ai))
    rows.append(('SVN_'+id,en[0],ru[0])); rows.append(('SVN_'+id+'_desc',en[1],ru[1]))
FORK=['negotiated_future','declare_sovereignty','assert_control']
def fk(me): return [x for x in FORK if x!=me]
f('consolidate_statehood',0,0,5,'u',rw=[stab(0.05),pp(30),swap:='swap_ideas = { remove_idea = SVN_young_institutions add_idea = SVN_working_institutions }'],
  en=('Consolidate Statehood','Set up the working institutions of the republic: a government, a civil service and a treasury that answer to the assembly.'),
  ru=('Укрепление государственности','Создать работающие институты республики: правительство, администрацию и казну, подотчётные собранию.'))
# defence
f('build_defence_forces',-7,1,5,'a',pre=['consolidate_statehood'],rw=[war(0.03),MIL],
  en=('Build Defence Forces','Organize the republic\'s own defence structures out of what the federation left on its soil.'),ru=('Создание сил обороны','Организовать собственные структуры обороны из того, что федерация оставила на территории республики.'))
f('territorial_defence',-8,2,6,'a',pre=['build_defence_forces'],rw=[idea('SVN_territorial_defence_force')],
  en=('Territorial Defence','Local units with local stores, trained to hold the mountains and the passes.'),ru=('Территориальная оборона','Местные части с местными складами, обученные удерживать горы и перевалы.'))
f('route_security',-6,2,6,'m',pre=['build_defence_forces'],rw=[INF,stab(0.01)],
  en=('Secure Transport Routes','Guard the motorways, railways and tunnels that carry the republic\'s trade.'),ru=('Защита транспортных путей','Охрана магистралей, железных дорог и тоннелей, по которым идёт торговля республики.'))
f('reserve_training',-8,3,6,'a',pre=['territorial_defence'],rw=[idea('SVN_trained_reservists')],
  en=('Train the Reserves','A yearly cycle of reservist courses, kept cheap and regular.'),ru=('Подготовка резервов','Ежегодный цикл курсов для резервистов, недорогой и регулярный.'))
f('security_forces_reform',-6,3,6,'p',pre=['route_security'],rw=[stab(0.03),pp(-20)],
  en=('Reform the Security Forces','Put police, border guards and intelligence under civilian ministers.'),ru=('Реформа сил безопасности','Подчинить полицию, пограничников и разведку гражданским министрам.'))
f('border_guard',-7,4,7,'m',pre=['reserve_training','security_forces_reform'],rw=[MIL,war(0.03)],
  en=('Establish the Border Guard','A professional corps for the border and its crossings.'),ru=('Создание пограничной охраны','Профессиональный корпус для границы и пунктов пропуска.'))
# economy
f('industrial_modernization',-3,1,5,'c',pre=['consolidate_statehood'],rw=[CIV,CIV],
  en=('Industrial Modernization','Re-equip the factories in the valleys with credit from the republic\'s own banks.'),ru=('Промышленная модернизация','Переоснастить заводы в долинах за счёт кредитов собственных банков республики.'))
f('export_economy',-4,2,6,'c',pre=['industrial_modernization'],rw=[idea('SVN_export_champion')],
  en=('Export Economy','Turn the republic\'s workshops into suppliers for the whole region and beyond.'),ru=('Экспортная экономика','Превратить мастерские республики в поставщиков для всего региона и дальше.'))
f('infrastructure_investment',-2,2,6,'c',pre=['industrial_modernization'],rw=[INF,INF],
  en=('Infrastructure Investment','Finish the motorway axes and the freight rail links.'),ru=('Инвестиции в инфраструктуру','Достроить осевые магистрали и грузовые железнодорожные линии.'))
f('financial_stabilization',-4,3,6,'c',pre=['export_economy'],rw=[swap_:='swap_ideas = { remove_idea = SVN_export_dependence add_idea = SVN_financial_stability }'],
  en=('Financial Stabilization','Build reserves and a monetary framework before the old payment system fails.'),ru=('Финансовая стабилизация','Создать резервы и денежную систему до того, как старая платёжная система даст сбой.'))
f('production_cooperation',-2,3,6,'c',pre=['infrastructure_investment'],rw=[idea('SVN_open_market'),CIV],
  en=('Production Cooperation','Long-term supply contracts with factories in the other republics.'),ru=('Производственная кооперация','Долгосрочные контракты на поставки с заводами других республик.'))
f('adriatic_gateway',-3,4,8,'c',pre=['financial_stabilization','production_cooperation'],rw=[CIV,INF,stab(0.02)],
  en=('The Adriatic Gateway','Expand the port and its rail link into a trade gateway for central Europe.'),ru=('Адриатические ворота','Расширить порт и железнодорожную линию до него в торговые ворота Центральной Европы.'))
# political
f('constitutional_reform',2,1,5,'p',pre=['consolidate_statehood'],rw=[pp(40),flag('SVN_constitution_reformed')],
  en=('Constitutional Reform','Amend the republic\'s constitution to put sovereignty and its limits in writing.'),ru=('Конституционная реформа','Внести в конституцию республики поправки, закрепляющие суверенитет и его пределы.'))
f('federal_relations_review',4,1,5,'p',pre=['consolidate_statehood'],rw=[pp(30),flag('SVN_relations_reviewed')],
  en=('Review Relations with the Federation','Go through every federal obligation and ask what the republic gets for it.'),ru=('Пересмотр отношений с федерацией','Разобрать каждое федеральное обязательство и спросить, что республика за него получает.'))
f('future_of_the_state',3,2,8,'u',pre=['constitutional_reform','federal_relations_review'],rw=[pp(50)],
  en=('The Future of the State','The assembly debates three roads: a negotiated place in a reformed union, sovereignty by agreement, or control by force of will.'),
  ru=('Будущее государства','Собрание обсуждает три дороги: место в реформированном союзе по договорённости, суверенитет по соглашению или контроль силой воли.'))
f('negotiated_future',1,3,8,'u',pre=['future_of_the_state'],mx=fk('negotiated_future'),rw=[flag('SVN_path_association'),leader('SVN_tina_kos','democratic','YGwar_regime_social_dem')],ai=3,
  en=('A Negotiated Future','Stay at the table. Ask for wide autonomy and guarantees, and make the federation answer.'),ru=('Согласованное будущее','Остаться за столом переговоров. Просить широкую автономию и гарантии и заставить федерацию отвечать.'))
f('declare_sovereignty',3,3,8,'u',pre=['future_of_the_state'],mx=fk('declare_sovereignty'),rw=[flag('SVN_path_sovereignty'),leader('SVN_luka_novak','democratic','YGwar_regime_reformist'),ev(1)],ai=4,
  en=('Declare Sovereignty','Proclaim that the republic\'s law stands above federal law, and offer to negotiate the rest.'),ru=('Провозглашение суверенитета','Объявить, что закон республики выше федерального, и предложить обсудить остальное.'))
f('assert_control',5,3,8,'w',pre=['future_of_the_state'],mx=fk('assert_control'),rw=[flag('SVN_path_confrontation'),leader('SVN_andrej_bevc','neutrality','YGwar_regime_securitarian'),war(0.05),stab(-0.03)],ai=1,
  en=('Assert Control','Take control of the border, customs and public property before anyone else does.'),ru=('Утверждение контроля','Взять под контроль границу, таможню и государственное имущество раньше, чем это сделает кто-то другой.'))
f('association_treaty',1,4,8,'u',pre=['negotiated_future'],rw=[ev(2)],
  en=('Association Treaty','A treaty that leaves the republic sovereign in its own affairs and linked to the union in some.'),ru=('Договор об ассоциации','Договор, оставляющий республику суверенной в её делах и связанной с союзом в некоторых.'))
f('shared_market_agreement',1,5,7,'c',pre=['association_treaty'],av='has_country_flag = SVN_association_signed',rw=[idea('SVN_open_market'),stab(0.03),pp(40)],
  en=('Shared Market Agreement','Keep the common market and the payment system for as long as it serves both sides.'),ru=('Соглашение об общем рынке','Сохранить общий рынок и платёжную систему, пока они служат обеим сторонам.'))
f('constitutional_declaration',3,4,8,'p',pre=['declare_sovereignty'],rw=[flag('SVN_constitution_declared'),pp(60),SVN_rec:=rec(10)],
  en=('Constitutional Declaration','Adopt the founding documents of an independent state and set a date for their entry into force.'),ru=('Конституционная декларация','Принять основополагающие документы независимого государства и назначить дату их вступления в силу.'))
f('new_currency',3,5,8,'c',pre=['constitutional_declaration'],rw=[ev(5)],
  en=('Introduce a New Currency','Replace the old money with the republic\'s own, backed by reserves.'),ru=('Введение новой валюты','Заменить старые деньги собственными, обеспеченными резервами.'))
f('seize_federal_facilities',5,4,8,'w',pre=['assert_control'],rw=[ev(3)],
  en=('Take Over Federal Facilities','Customs posts, depots and offices that belong to the federation, on the republic\'s soil.'),ru=('Переход федеральных объектов','Таможенные посты, склады и учреждения федерации на территории республики.'))
f('defend_the_republic',5,5,9,'w',pre=['seize_federal_facilities'],rw=[idea('SVN_defiant_republic'),ev(6)],
  en=('Defend the Republic','Prepare to hold the passes if the federal army comes.'),ru=('Защита республики','Подготовиться удерживать перевалы, если придёт федеральная армия.'))
# diplomacy
f('seek_recognition',8,1,5,'p',pre=['consolidate_statehood'],rw=[pp(30),rec(5)],
  en=('Seek Recognition','Open channels to foreign governments and international bodies.'),ru=('Поиск признания','Наладить контакты с иностранными правительствами и международными организациями.'))
f('diplomatic_corps',8,2,6,'p',pre=['seek_recognition'],rw=[pp(40),rec(5)],
  en=('A Diplomatic Corps','Train a small service for representation abroad.'),ru=('Дипломатический корпус','Подготовить небольшую службу для представительства за рубежом.'))
f('recognition_campaign',8,4,8,'p',pre=['diplomatic_corps'],orp=['declare_sovereignty','negotiated_future'],rw=[ev(4)],
  en=('Recognition Campaign','A public effort to win support abroad for the path the republic has chosen.'),ru=('Кампания за признание','Публичные усилия, чтобы заручиться поддержкой за рубежом для выбранного республикой пути.'))
# validate
ids={x['id'] for x in F}; pos=set(); by={x['id']:x for x in F}
assert len(ids)==len(F)
for x in F:
    assert (x['x'],x['y']) not in pos,x['id']; pos.add((x['x'],x['y']))
    for p in x['pre']+x['orp']+x['mx']: assert p in ids,(x['id'],p)
    for p in x['pre']+x['orp']: assert by[p]['y']<x['y'],(x['id'],p)
def block(x):
    L=['\tfocus = {',f'\t\tid = {x["id"]}',f'\t\ticon = {x["icon"]}',f'\t\tx = {x["x"]}',f'\t\ty = {x["y"]}',f'\t\tcost = {x["cost"]}']
    for p in x['pre']: L.append(f'\t\tprerequisite = {{ focus = {p} }}')
    if x['orp']: L.append('\t\tprerequisite = { '+' '.join(f'focus = {p}' for p in x['orp'])+' }')
    if x['mx']: L.append('\t\tmutually_exclusive = { '+' '.join(f'focus = {p}' for p in x['mx'])+' }')
    if x['av']: L.append('\t\tavailable = {\n'+'\n'.join('\t\t\t'+l for l in x['av'].split('\n'))+'\n\t\t}')
    if x['ai'] is not None: L.append(f'\t\tai_will_do = {{ factor = {x["ai"]} }}')
    L.append('\t\tcompletion_reward = {')
    for r in x['rw']:
        for l in r.split('\n'): L.append('\t\t\t'+l)
    L+=['\t\t}','\t}']; return '\n'.join(L)
W('common/national_focus/SVN_focus.txt','# YGwar - Slovenia focus tree (GENERATED by tools/build_svn.py)\nfocus_tree = {\n\tid = SVN_focus_tree\n\tcountry = {\n\t\tfactor = 0\n\t\tmodifier = { add = 100 tag = SVN }\n\t}\n\n'+'\n\n'.join(block(x) for x in F)+'\n}\n')
# remove stub tree
t=R('common/national_focus/YGwar_republic_focus.txt')
t2=re.sub(r'focus_tree = \{\n\tid = SVN_focus_tree.*?\n\}\n\n(?=focus_tree = \{\n\tid = CRO_focus_tree)','',t,count=1,flags=re.S)
assert t2!=t or 'SVN_focus_tree' not in t
W('common/national_focus/YGwar_republic_focus.txt',t2)
# scripted effect
W('common/scripted_effects/YGwar_SVN_effects.txt','SVN_add_recognition = {\n\tadd_to_variable = { SVN_recognition = $VAL$ }\n\tclamp_variable = { var = SVN_recognition min = 0 max = 100 }\n}\n')
# ideas
ID=[('SVN_young_institutions','pp_unity','political_power_factor = -0.10','Young Institutions','Молодые институты','Offices and procedures are still being invented.','Учреждения и процедуры ещё только изобретаются.'),
('SVN_working_institutions','pp_unity','political_power_factor = 0.05','Working Institutions','Работающие институты','The republic\'s offices answer to the assembly and to each other.','Учреждения республики подотчётны собранию и друг другу.'),
('SVN_industrial_base','production','industrial_capacity_factory = 0.05','Industrial Base','Промышленная база','Dense workshops, skilled labour and good rail links.','Плотная сеть мастерских, квалифицированные кадры и хорошие железные дороги.'),
('SVN_alpine_terrain','manpower','army_defence_factor = 0.05','Alpine Terrain','Альпийский рельеф','Mountains and passes favour the defender.','Горы и перевалы благоприятствуют обороняющемуся.'),
('SVN_export_dependence','production','stability_factor = -0.03 production_factory_max_efficiency_factor = -0.03','Export Dependence','Зависимость от экспорта','Half the factories work for markets the republic does not control.','Половина заводов работает на рынки, которые республика не контролирует.'),
('SVN_financial_stability','production','stability_factor = 0.04','Financial Stability','Финансовая стабильность','Reserves and a clear monetary framework steady prices.','Резервы и чёткая денежная система стабилизируют цены.'),
('SVN_territorial_defence_force','manpower','army_defence_factor = 0.05 conscription_factor = 0.05','Territorial Defence Force','Силы территориальной обороны','Local units hold local stores and know the ground.','Местные части держат местные склады и знают местность.'),
('SVN_trained_reservists','manpower','conscription_factor = 0.08','Trained Reservists','Подготовленные резервисты','A regular cycle of courses keeps the reserve pool ready.','Регулярный цикл курсов держит резерв в готовности.'),
('SVN_export_champion','production','industrial_capacity_factory = 0.05 production_factory_max_efficiency_factor = 0.05 stability_factor = -0.02','Export Champion','Экспортный лидер','The workshops sell everywhere. A foreign downturn would be felt at once.','Мастерские продают везде. Иностранный спад был бы ощутим сразу.'),
('SVN_open_market','production','stability_factor = 0.03 production_speed_buildings_factor = 0.05','Open Market','Открытый рынок','Trade across republic lines keeps costs down.','Торговля через республиканские границы снижает издержки.'),
('SVN_defiant_republic','manpower','war_support_factor = 0.10 political_power_factor = 0.05 stability_factor = -0.03','Defiant Republic','Непокорная республика','The republic is ready to defend what it has taken.','Республика готова защищать то, что она взяла.'),
('SVN_neutral_course','pp_unity','war_support_factor = -0.05 stability_factor = 0.04','Neutral Course','Нейтральный курс','Stay out of every dispute that is not the republic\'s own.','Не вмешиваться ни в один спор, не касающийся самой республики.'),
('SVN_hard_money','production','stability_factor = 0.03 consumer_goods_factor = 0.03','Hard Money','Твёрдая валюта','A new currency backed by reserves.','Новая валюта, обеспеченная резервами.'),
('SVN_float_policy','production','production_factory_max_efficiency_factor = 0.05 stability_factor = -0.02','Floating Currency','Плавающая валюта','Exporters gain; households watch the exchange rate.','Экспортёры выигрывают; домохозяйства следят за курсом.')]
out='# YGwar - Slovenia national spirits. Pictures reuse generic vanilla ones.\nideas = {\n\tcountry = {\n'
for k,pic,mod,en,ru,de,dr in ID:
    out+=f'\t\t{k} = {{\n\t\t\tpicture = generic_{pic}_bonus\n\t\t\tallowed = {{ always = no }}\n\t\t\tremoval_cost = -1\n\t\t\tmodifier = {{ {mod} }}\n\t\t}}\n'
    rows+=[(k,en,ru),(k+'_desc',de,dr)]
W('common/ideas/YGwar_SVN_ideas.txt',out+'\t}\n}\n')
# history spirits
p='history/countries/SVN - Slovenia.txt'; t=R(p)
if 'SVN_industrial_base' not in t:
    t=t.replace('recruit_character = SVN_YGwar_leader','add_ideas = {\n    SVN_young_institutions\n    SVN_industrial_base\n    SVN_alpine_terrain\n    SVN_export_dependence\n}\n\nrecruit_character = SVN_YGwar_leader',1)
W(p,t)
# characters
p='common/characters/YGwar_leaders.txt'; t=R(p).rstrip()
ch=[('luka_novak','liberalism','popular_figurehead','Luka Novak','Лука Новак'),('tina_kos','socialism','silent_workhorse','Tina Kos','Тина Кос'),('andrej_bevc','despotism','dictator','Andrej Bevc','Андрей Бевц')]
add=''
for c,i,tr,en,ru in ch:
    if f'SVN_{c} =' not in t: add+=f'\n    SVN_{c} = {{\n        name = SVN_{c}\n        country_leader = {{\n            ideology = {i}\n            traits = {{ {tr} }}\n            expire = "2100.1.1"\n            id = -1\n        }}\n    }}\n'
    rows.append(('SVN_'+c,en,ru))
W(p,t[:-1].rstrip()+'\n'+add+'}\n')
# events
EV=[]
def e(n,t,d,opts): EV.append((n,t,d,opts))
e(1,('Sovereignty Declared','Суверенитет провозглашён'),('The assembly has voted. The republic\'s law now claims precedence over federal law, and every federal office on its soil has to decide what that means.','Собрание проголосовало. Закон республики теперь претендует на приоритет над федеральным, и каждому федеральному учреждению на её территории предстоит решить, что это значит.'),
 [(['SVN_add_recognition = { VAL = 5 }','add_stability = 0.03','YUG = { YGwar_add_cohesion = { VAL = -4 } }','set_country_flag = SVN_sovereignty_declared'],('Declare it as a basis for negotiation','Объявить это основой для переговоров')),
  (['add_war_support = 0.03','YUG = { YGwar_add_cohesion = { VAL = -8 } }','set_country_flag = SVN_sovereignty_declared','add_stability = -0.02'],('Declare it as a final act','Объявить это окончательным решением'))])
e(2,('The Association Treaty','Договор об ассоциации'),('The federation has sent a draft: the republic keeps its own government, army and currency, and shares a market and a foreign-policy council with the union.','Федерация прислала проект: республика сохраняет собственное правительство, армию и валюту и делит с союзом рынок и совет по внешней политике.'),
 [(['set_country_flag = SVN_association_signed','add_stability = 0.04','YUG = { YGwar_add_cohesion = { VAL = 8 } }'],('Sign the treaty','Подписать договор')),
  (['add_political_power = -30','set_country_flag = SVN_association_signed','add_stability = 0.02','YUG = { YGwar_add_cohesion = { VAL = 4 } }'],('Sign, with a clause allowing review in five years','Подписать, с пунктом о пересмотре через пять лет'))])
e(3,('Federal Facilities on the Republic\'s Soil','Федеральные объекты на территории республики'),('Customs posts and depots are staffed by people who still take orders from Belgrade. A transfer has to be arranged, one way or another.','Таможенные посты и склады укомплектованы людьми, которые всё ещё подчиняются приказам из Белграда. Передачу нужно организовать так или иначе.'),
 [(['add_stability = -0.02','add_political_power = -20','YUG = { YGwar_add_cohesion = { VAL = -3 } }'],('Negotiate a handover','Договориться о передаче')),
  (['add_war_support = 0.05','add_stability = -0.04','YUG = { YGwar_add_cohesion = { VAL = -8 } YGwar_add_loyalty = { VAL = -5 } }','set_country_flag = SVN_facilities_seized'],('Take them by force of numbers','Взять их числом'))])
e(4,('Recognition Campaign','Кампания за признание'),('Delegations travel abroad with maps, treaties and economic offers. What they say depends on what the republic wants to be.','Делегации ездят за границу с картами, договорами и экономическими предложениями. Что они говорят, зависит от того, чем хочет быть республика.'),
 [(['SVN_add_recognition = { VAL = 15 }','add_political_power = -30','add_ideas = SVN_neutral_course'],('Present the republic as a peaceful, neutral partner','Представить республику мирным нейтральным партнёром')),
  (['SVN_add_recognition = { VAL = 8 }','add_war_support = 0.03','add_political_power = 20'],('Present the republic as a state that has already taken its place','Представить республику государством, которое уже заняло своё место'))])
e(5,('A New Currency','Новая валюта'),('The treasury asks how the new money should relate to the old and to foreign currencies.','Казначейство спрашивает, как новые деньги должны соотноситься со старыми и с иностранными валютами.'),
 [(['add_ideas = SVN_hard_money','add_stability = 0.02'],('Peg it to a hard anchor','Привязать к твёрдому якорю')),
  (['add_ideas = SVN_float_policy','add_political_power = 25'],('Let it float','Пустить в свободное плавание'))])
e(6,('Mobilization Orders','Приказы о мобилизации'),('Reports say federal units are moving towards the border. The staff asks how much of the republic should be put on a war footing.','Сообщают, что федеральные части движутся к границе. Штаб спрашивает, какая часть республики должна быть переведена на военное положение.'),
 [(['add_war_support = 0.05','add_stability = -0.04','YGwar_build_mil = yes','YGwar_build_mil = yes'],('General mobilization','Всеобщая мобилизация')),
  (['add_war_support = 0.02','add_stability = -0.01','YGwar_build_mil = yes'],('Limited call-up of the territorial units','Ограниченный призыв территориальных частей'))])
o='# YGwar - Slovenia events (GENERATED by tools/build_svn.py)\nadd_namespace = YGwar_SVN\n\n'
for n,t_,d_,opts in EV:
    o+=f'country_event = {{\n\tid = YGwar_SVN.{n}\n\ttitle = YGwar_SVN.{n}.t\n\tdesc = YGwar_SVN.{n}.d\n\tpicture = GFX_report_event_unrest_in_city\n\tis_triggered_only = yes\n'
    for i,(eff,name) in enumerate(opts):
        o+=f'\toption = {{\n\t\tname = YGwar_SVN.{n}.{"ab"[i]}\n'+''.join(f'\t\t{x}\n' for x in eff)+'\t}\n'
        rows.append((f'YGwar_SVN.{n}.{"ab"[i]}',name[0],name[1]))
    o+='}\n\n'; rows+=[(f'YGwar_SVN.{n}.t',t_[0],t_[1]),(f'YGwar_SVN.{n}.d',d_[0],d_[1])]
W('events/YGwar_SVN_events.txt',o)
# decisions
DEC=[('SVN_secure_transport_corridors','decision_generic_military_pressure','visible = { tag = SVN }\n\t\tavailable = { check_variable = { SVN_corridor_count < 4 } }',40,120,'YGwar_build_infra = yes add_to_variable = { SVN_corridor_count = 1 }','Secure the Transport Corridors','Охрана транспортных коридоров','Station guards and repair crews on the main routes. Limited number of uses.','Разместить охрану и ремонтные бригады на главных путях. Число применений ограничено.'),
('SVN_cooperate_with_neighbours','decision_generic_construct_civilian','visible = { tag = SVN }\n\t\tavailable = { check_variable = { SVN_cooperation_count < 3 } OR = { has_country_flag = SVN_sovereignty_declared has_country_flag = SVN_association_signed } }',50,150,'YGwar_build_civ = yes add_stability = 0.01 add_to_variable = { SVN_cooperation_count = 1 }','Cooperate with Neighbouring Republics','Сотрудничество с соседними республиками','Joint projects with the republics next door. Limited number of uses.','Совместные проекты с соседними республиками. Число применений ограничено.'),
('SVN_press_for_recognition','decision_generic_political_pressure','visible = { tag = SVN }\n\t\tavailable = { check_variable = { SVN_recognition < 100 } has_country_flag = SVN_sovereignty_declared }',60,90,'SVN_add_recognition = { VAL = 5 }','Press for Recognition','Добиваться признания','Raise international recognition. Needs a declaration of sovereignty.','Повысить международное признание. Требует декларации суверенитета.')]
o='# YGwar - Slovenia decisions (GENERATED by tools/build_svn.py)\nYGwar_republic_category = {\n'
for k,ic,cond,cost,re_,eff,en,ru,de,dr in DEC:
    o+=f'\n\t{k} = {{\n\t\ticon = {ic}\n\t\tpriority = 20\n\t\tallowed = {{ tag = SVN }}\n\t\t{cond}\n\t\tcost = {cost}\n\t\tdays_re_enable = {re_}\n\t\tcomplete_effect = {{ {eff} }}\n\t\tai_will_do = {{ factor = 1 }}\n\t}}\n'
    rows+=[(k,en,ru),(k+'_desc',de,dr)]
W('common/decisions/YGwar_SVN_decisions.txt',o+'}\n')
# loc
seen=set()
for k,_,_ in rows: assert k not in seen,k; seen.add(k)
q=lambda s:s.replace('\\','\\\\').replace('"','\\"')
for lang,i,fn in (('english',1,'YGwar_svn_l_english.yml'),('russian',2,'YGwar_svn_l_russian.yml')):
    W(f'localisation/{lang}/{fn}','\ufeffl_%s:\n'%lang+''.join(' %s:0 "%s"\n'%(r[0],q(r[i])) for r in rows))
print('SVN focuses',len(F),'events',len(EV),'loc keys',len(rows))
