#!/usr/bin/env python3
"""Generates localisation/english/YGwar_yug_l_english.yml and localisation/russian/YGwar_yug_l_russian.yml
from tools/_yug_focus_loc.json, tools/_events_loc.json and the tables below."""
import os, json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T=os.path.join(ROOT,'tools')
rows=[]  # (key, en, ru)
for x in json.load(open(os.path.join(T,'_yug_focus_loc.json'),encoding='utf-8')):
    rows.append((x['id'],x['en'][0],x['ru'][0])); rows.append((x['id']+'_desc',x['en'][1],x['ru'][1]))
for k,en,ru in json.load(open(os.path.join(T,'_events_loc.json'),encoding='utf-8')): rows.append((k,en,ru))
rows += [('YGwar.1.t','Security Forces Unrest','Волнения в силовых структурах'),
 ('YGwar.1.d','Reports reach the Presidency of disorder in local militia units: unpaid wages, contested orders and unauthorised movements.','В Президиум поступают сообщения о беспорядках в местных частях ополчения: невыплаченное жалованье, оспариваемые приказы и несанкционированные перемещения.'),
 ('YGwar.1.a','Pay arrears and reassure the units','Выплатить задолженность и успокоить части'),
 ('YGwar.1.b','Order the units back to barracks','Приказать частям вернуться в казармы')]
ideas=[
('YUG_federal_bureaucracy','Federal Bureaucracy','Федеральная бюрократия','Overlapping federal departments slow every decision.','Дублирующие федеральные ведомства замедляют любое решение.'),
('YUG_streamlined_administration','Streamlined Administration','Упорядоченная администрация','Clear lines of responsibility have replaced the old overlap.','Чёткие линии ответственности заменили прежнее дублирование.'),
('YUG_economic_instability','Economic Instability','Экономическая нестабильность','Inflation and debt weigh on factories and households.','Инфляция и долги давят на заводы и домохозяйства.'),
('YUG_stabilization_programme','Stabilization Programme','Программа стабилизации','Hard budget limits have steadied prices, at a cost in output.','Жёсткие бюджетные лимиты стабилизировали цены ценой выпуска.'),
('YUG_republican_particularism','Republican Particularism','Республиканский партикуляризм','Each republic reads federal policy through its own interests.','Каждая республика читает федеральную политику через свои интересы.'),
('YUG_military_leadership_influence','Military Leadership Influence','Влияние военного руководства','The army is strong and has opinions about politics.','Армия сильна и имеет мнение о политике.'),
('YUG_transport_network','Transport Network','Транспортная сеть','Roads, rails and ports connect the republics better than politics does.','Дороги, железные дороги и порты связывают республики лучше, чем политика.'),
('YUG_industrial_potential','Industrial Potential','Промышленный потенциал','A broad base of machine building, steel and vehicles.','Широкая база машиностроения, металлургии и автомобилестроения.'),
('YUG_federal_trust_crisis','Crisis of Federal Trust','Кризис федерального доверия','Republics doubt that federal bodies are fair. Rebuild trust or reform the federation to lift it.','Республики сомневаются в беспристрастности федеральных органов. Восстановите доверие или реформируйте федерацию, чтобы его снять.'),
('YUG_emergency_rule','Emergency Rule','Чрезвычайное управление','Decisions are made fast and by few. The republics notice.','Решения принимаются быстро и немногими. Республики это замечают.'),
('YUG_rail_road_programme','Rail and Road Programme','Программа железных и автомобильных дорог','New links make goods and troops move faster.','Новые связи ускоряют перевозку грузов и войск.'),
('YUG_modern_agriculture','Modern Agriculture','Современное сельское хозяйство','Cooperatives and storage steady food supply.','Кооперативы и хранилища стабилизируют снабжение продовольствием.'),
('YUG_export_orientation','Export Orientation','Экспортная ориентация','Factories work for foreign markets, with the risks that brings.','Заводы работают на внешние рынки, со всеми вытекающими рисками.'),
('YUG_common_market','Common Market','Общий рынок','Shared supply chains bind republican economies together.','Общие цепочки поставок связывают республиканские экономики.'),
('YUG_democratic_institutions','Democratic Institutions','Демократические институты','Open politics bring stability and slow decisions.','Открытая политика приносит стабильность и замедляет решения.'),
('YUG_joint_defence','Joint Defence','Совместная оборона','Republican and federal forces share one defence plan.','Республиканские и федеральные силы делят один оборонный план.'),
('YUG_central_defence_planning','Central Defence Planning','Централизованное оборонное планирование','One general staff controls plans, depots and call-ups.','Один генеральный штаб управляет планами, складами и призывом.'),
('YUG_workers_councils','Workers\' Councils','Рабочие советы','Elected councils have a real say in enterprise decisions.','Выборные советы имеют реальный голос в решениях предприятий.'),
('YUG_trained_reserves','Trained Reserves','Подготовленные резервы','Regular refresher courses keep the mobilization pool ready.','Регулярная переподготовка держит мобилизационный резерв в готовности.'),
('YUG_territorial_defence_network','Territorial Defence Network','Сеть территориальной обороны','Local stores and plans strengthen defence, and also local loyalties.','Местные склады и планы усиливают оборону, а вместе с ней и местные лояльности.'),
('YUG_confederal_bargaining','Confederal Bargaining','Конфедеративный торг','Every decision is negotiated between sovereign members.','Каждое решение согласуется между суверенными членами.'),
('YUG_reformed_federation','Reformed Federation','Реформированная федерация','A constitution all republics helped write.','Конституция, к написанию которой приложили руку все республики.'),
('YUG_centralized_state','Centralized State','Централизованное государство','A strong centre, a strong army and little patience for dissent.','Сильный центр, сильная армия и мало терпения к несогласию.')]
for k,en,ru,de,dr in ideas: rows += [(k,en,ru),(k+'_desc',de,dr)]
dec=[
('YGwar_militia_category','Security Forces','Силовые структуры','',''),
('YGwar_federal_category','Federal Government','Федеральное правительство','Routine tools of the federal government.','Повседневные инструменты федерального правительства.'),
('YGwar_crisis_category','Federation in Crisis','Федерация в кризисе','Tools for managing the crisis. Available once cohesion has started to fall.','Инструменты управления кризисом. Доступны, когда согласованность начала падать.'),
('YGwar_republic_category','Republican Government','Республиканское правительство','Routine tools for republican and regional governments.','Повседневные инструменты республиканских и региональных правительств.'),
('YUG_discipline_militia','Discipline the Militia','Дисциплинировать ополчение','Raise militia loyalty. It may cause some unrest.','Повысить лояльность ополчения. Это может вызвать недовольство.'),
('YUG_hold_republic_talks','Hold Talks with the Republics','Провести переговоры с республиками','Raise federation cohesion.','Повысить согласованность федерации.'),
('YUG_federal_economic_programme','Federal Economic Programme','Федеральная экономическая программа','Fund civilian industry while the economy is unstable.','Финансировать гражданскую промышленность, пока экономика нестабильна.'),
('YUG_constitutional_commission','Constitutional Reform Commission','Комиссия по конституционной реформе','Set up a commission, once. Raises cohesion.','Создать комиссию, один раз. Повышает согласованность.'),
('YUG_review_budget_agreements','Review Budget Agreements','Пересмотреть бюджетные договорённости','Raise cohesion at some cost to the security forces.','Повысить согласованность за счёт недовольства силовых структур.'),
('YUG_army_development_programme','Army Development Programme','Программа развития армии','Build arms factories and raise security-force loyalty.','Построить оружейные заводы и повысить лояльность силовых структур.'),
('YUG_defuse_tensions','Defuse Tensions','Снизить напряжённость','Raise cohesion.','Повысить согласованность.'),
('YUG_summon_emergency_talks','Summon Emergency Talks','Созвать чрезвычайные переговоры','Raise cohesion substantially. Needs a serious crisis.','Заметно повысить согласованность. Требует серьёзного кризиса.'),
('YUG_rebuild_trust','Rebuild Trust','Восстановить доверие','Raise loyalty and cohesion while the trust crisis lasts.','Повысить лояльность и согласованность, пока длится кризис доверия.'),
('YUG_prepare_transitional_administration','Prepare Transitional Administration','Подготовить переходное управление','Prepare for an orderly end, once. Makes dissolution cheaper and safer.','Подготовиться к упорядоченному концу, один раз. Делает роспуск дешевле и безопаснее.'),
('YGwar_consolidate_institutions','Consolidate Institutions','Укрепить институты','Raise stability. Limited number of uses.','Повысить стабильность. Число применений ограничено.'),
('YGwar_regional_investment','Regional Investment','Региональные инвестиции','Build civilian industry. Limited number of uses.','Построить гражданскую промышленность. Число применений ограничено.'),
('YGwar_territorial_defence_drive','Territorial Defence Drive','Кампания территориальной обороны','Raise war support at some cost to stability. Limited number of uses.','Повысить поддержку войны ценой некоторой стабильности. Число применений ограничено.')]
for k,en,ru,de,dr in dec:
    rows.append((k,en,ru))
    if de: rows.append((k+'_desc',de,dr))
chars=[('dragan_vukic','Dragan Vukić','Драган Вукич'),('stevan_jovanov','Stevan Jovanov','Стеван Йованов'),('milos_radic','Miloš Radić','Милош Радич'),
('ana_kovac','Ana Kovač','Ана Ковач'),('petar_lazic','Petar Lazić','Петар Лазич'),('mirko_stankovic','Mirko Stanković','Мирко Станкович'),('jelena_ilic','Jelena Ilić','Елена Илич')]
for c,en,ru in chars: rows.append(('YUG_'+c,en,ru))
# interim leaders created earlier (history files recruit them): neutral titled placeholders, not real persons
for tg,en,ru in [('YUG','Yugoslavia','Югославия')]+[(k,v[0],v[1]) for k,v in {'SVN':('Slovenia','Словения'),'CRO':('Croatia','Хорватия'),'BOS':('Bosnia and Herzegovina','Босния и Герцеговина'),'SER':('Serbia','Сербия'),'MNT':('Montenegro','Черногория'),'MAC':('Macedonia','Македония'),'VOJ':('Vojvodina','Воеводина'),'KOS':('Kosovo','Косово'),'RSB':('Republika Srpska','Республика Сербская'),'RSK':('Republika Srpska Krajina','Республика Сербская Краина'),'HRZ':('Herceg-Bosna','Герцег-Босна')}.items()]:
    rows.append((tg+'_YGwar_leader','Interim Leader of '+en,'Временный лидер: '+ru))
# republic stub focuses (existing 33 ids): neutral placeholder names until their full trees are built
tags=['SVN','CRO','BOS','SER','MNT','MAC','VOJ','KOS','RSB','RSK','HRZ']
names={'SVN':('Slovenia','Словения'),'CRO':('Croatia','Хорватия'),'BOS':('Bosnia and Herzegovina','Босния и Герцеговина'),'SER':('Serbia','Сербия'),'MNT':('Montenegro','Черногория'),'MAC':('Macedonia','Македония'),'VOJ':('Vojvodina','Воеводина'),'KOS':('Kosovo','Косово'),'RSB':('Republika Srpska','Республика Сербская'),'RSK':('Republika Srpska Krajina','Республика Сербская Краина'),'HRZ':('Herceg-Bosna','Герцег-Босна')}
for t in tags:
    n=names[t]
    rows += [(f'{t}_consolidate_statehood','Consolidate Statehood','Укрепление государственности'),(f'{t}_consolidate_statehood_desc',f'Set up the working institutions of {n[0]}.',f'Создать работающие институты: {n[1]}.'),
             (f'{t}_build_defence_forces','Build Defence Forces','Создание сил обороны'),(f'{t}_build_defence_forces_desc',f'Organize the defence of {n[0]}.',f'Организовать оборону: {n[1]}.'),
             (f'{t}_seek_recognition','Seek Recognition','Поиск признания'),(f'{t}_seek_recognition_desc',f'Win acceptance for {n[0]} among its neighbours.',f'Добиться признания: {n[1]} среди соседей.')]
seen=set()
for k,en,ru in rows:
    assert k not in seen,('dup key',k); seen.add(k)
def q(s): return s.replace('\\','\\\\').replace('"','\\"')
for lang,idx,fn in (('english',1,'YGwar_yug_l_english.yml'),('russian',2,'YGwar_yug_l_russian.yml')):
    out='\ufeffl_%s:\n'%lang+''.join(' %s:0 "%s"\n'%(r[0],q(r[idx])) for r in rows)
    open(os.path.join(ROOT,'localisation',lang,fn),'w',encoding='utf-8').write(out)
print('keys',len(rows))
