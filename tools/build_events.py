#!/usr/bin/env python3
"""Generates events/YGwar_crisis_events.txt + event loc json. Re-runnable."""
import os, json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIC='GFX_report_event_unrest_in_city'
E=[]  # (num, trigger_extra, immediate, options[(effects, en, ru)], en_title,en_desc,ru_title,ru_desc, hidden)
def ev(n,title,desc,opts,trigger='',immediate=''):
    E.append(dict(n=n,title=title,desc=desc,opts=opts,trigger=trigger,immediate=immediate))
coh=lambda n:f'YGwar_add_cohesion = {{ VAL = {n} }}'
loy=lambda n:f'YGwar_add_loyalty = {{ VAL = {n} }}'
ev(10,('Cracks in the Federation','Трещины в федерации'),
 ('Republican delegations vote against federal proposals more often, and the press has started to count the votes by republic. Nothing is broken yet, but everyone is watching how the Presidency reacts.',
  'Республиканские делегации всё чаще голосуют против федеральных предложений, а пресса начала считать голоса по республикам. Пока ничего не сломано, но все следят за реакцией Президиума.'),
 [(['add_political_power = -30',coh(4)],('Call the republican leaders together','Собрать лидеров республик'),None),
  ([coh(-3),'add_stability = 0.01'],('Treat it as routine politics','Считать это обычной политикой'),None)])
ev(11,('Crisis of Federal Trust','Кризис федерального доверия'),
 ('Republics no longer accept federal figures at face value. Budget allocations, army postings and even census numbers are contested.',
  'Республики больше не принимают федеральные данные на веру. Бюджетные распределения, назначения в армии и даже цифры переписи оспариваются.'),
 [(['add_ideas = YUG_federal_trust_crisis','add_political_power = -50',coh(4),'set_country_flag = YGwar_talks_opened'],('Open emergency negotiations','Начать чрезвычайные переговоры'),None),
  (['add_ideas = YUG_federal_trust_crisis',loy(5),coh(-6),'add_stability = -0.04'],('Assert federal authority','Подтвердить власть федерального центра'),None)],
 immediate='')
ev(12,('Emergency Federal Conference','Чрезвычайная федеральная конференция'),
 ('The cohesion of the federation has fallen below the point where decisions can be taken by consent. The Presidency calls a conference. Three roads are open, and none of them is cheap.',
  'Согласованность федерации упала ниже уровня, при котором решения принимаются по согласию. Президиум созывает конференцию. Открыты три дороги, и ни одна не дешёвая.'),
 [(['add_political_power = -40',coh(10),'set_country_flag = YUG_confederation_track'],('Seek a confederal compromise','Искать конфедеративный компромисс'),None),
  (['add_ideas = YUG_emergency_rule',loy(10),coh(-10),'add_stability = -0.05','set_country_flag = YGwar_emergency_rule'],('Declare emergency rule','Ввести чрезвычайное управление'),None),
  (['set_country_flag = YGwar_dissolution_planned','if = { limit = { has_country_flag = YGwar_transition_prepared } add_stability = 0.05 }','add_political_power = 25'],('Prepare for an orderly dissolution','Готовиться к упорядоченному роспуску'),None)])
ev(14,('The Republics Agree on a Confederal Model','Республики согласились на конфедеративную модель'),
 ('The republics accept a confederal draft: sovereign members, a small common centre, one market and a joint defence council. It is less than some wanted and more than others expected.',
  'Республики принимают проект конфедерации: суверенные члены, небольшой общий центр, единый рынок и совместный совет обороны. Это меньше, чем хотели одни, и больше, чем ожидали другие.'),
 [(['add_ideas = YUG_confederal_bargaining',coh(8),'add_political_power = -25'],('Sign the draft','Подписать проект'),None),
  ([coh(3),loy(4)],('Sign, with a guaranteed army budget','Подписать, с гарантированным армейским бюджетом'),None)],
 trigger='NOT = { has_country_flag = YGwar_confed_draft_seen }',
 immediate='set_country_flag = YGwar_confed_draft_seen')
ev(15,('The Security Forces Close Ranks','Силовые структуры смыкают ряды'),
 ('Commanders of several garrisons have started to take orders only from officers of their own republic. Staff reports describe it as an administrative matter.',
  'Командиры нескольких гарнизонов стали принимать приказы только от офицеров своей республики. В штабных докладах это называют административным вопросом.'),
 [([coh(-3),loy(8),'add_political_power = -30'],('Give them guarantees on pay and rank','Дать гарантии по жалованью и званиям'),None),
  ([loy(5),'add_stability = -0.05','add_political_power = -20'],('Rotate the commanders','Провести ротацию командиров'),None)],
 immediate='set_country_flag = { flag = YGwar_loyalty_cooldown days = 120 }')
ev(16,('Military Command Defies the Government','Военное командование игнорирует правительство'),
 ('The General Staff declines to carry out a cabinet order, citing the state of the units. For the first time in decades the army speaks as a political actor.',
  'Генштаб отказывается выполнить распоряжение кабинета, ссылаясь на состояние частей. Впервые за десятилетия армия выступает как политический субъект.'),
 [([loy(15),'add_political_power = -50','add_stability = -0.02'],('Negotiate with the generals','Договориться с генералами'),None),
  (['add_ideas = YUG_emergency_rule',loy(20),coh(-12),'add_stability = -0.05','set_country_flag = YGwar_emergency_rule',
    'recruit_character = YUG_petar_lazic','if = { limit = { NOT = { has_country_flag = YGwar_regime_set } } set_country_flag = YGwar_regime_set set_country_flag = YGwar_regime_military set_politics = { ruling_party = neutrality } promote_character = YUG_petar_lazic }'],
   ('Give the army emergency powers','Передать армии чрезвычайные полномочия'),None)],
 immediate='set_country_flag = YGwar_command_defiance_done')
# --- dissolution
ev(20,('Agreement on Orderly Dissolution','Соглашение об упорядоченном роспуске'),
 ('Slovenia, Croatia and Macedonia are recognised as independent states in a written settlement. Debts, army property and border crossings are divided on paper.',
  'Словения, Хорватия и Македония признаются независимыми государствами по письменному соглашению. Долги, армейское имущество и пограничные переходы разделены на бумаге.'),
 [(['YGwar_orderly_dissolution_phase1 = yes','set_country_flag = YGwar_outcome_peaceful_dissolution','country_event = { id = YGwar.21 days = 30 }','add_stability = 0.03'],('Sign the settlement','Подписать соглашение'),None)])
ev(21,('Bosnia and Herzegovina Votes','Босния и Герцеговина голосует'),
 ('Bosnia and Herzegovina must now decide. Its three communities disagree on whether to stay in what is left of the federation or to leave it.',
  'Боснии и Герцеговине теперь предстоит выбор. Три общины расходятся во мнениях, оставаться ли в том, что осталось от федерации, или выйти из неё.'),
 [(['YGwar_secede_BOS_all = yes','set_country_flag = YGwar_BOS_left','country_event = { id = YGwar.22 days = 30 }'],('Allow a negotiated exit of all Bosnia and Herzegovina','Допустить согласованный выход всей Боснии и Герцеговины'),None),
  (['if = { limit = { has_country_flag = YGwar_transition_prepared } YGwar_secede_BOS_all = yes set_country_flag = YGwar_BOS_left } else = { YGwar_secede_BOS_core = yes YGwar_secede_RSB_all = yes YGwar_secede_HRZ_all = yes set_country_flag = YGwar_BOS_left set_country_flag = YGwar_BOS_partitioned }','country_event = { id = YGwar.22 days = 30 }'],('Insist on guarantees for each community','Требовать гарантий для каждой общины'),None)],
 trigger='NOT = { has_country_flag = YGwar_BOS_left }')
ev(22,('The Rump Federation Reorganizes','Остаточная федерация реорганизуется'),
 ('What remains of the federation is Serbia with its provinces, and Montenegro. Both governments must decide how to organize their union, and what to do with the provinces.',
  'От федерации остались Сербия с краями и Черногория. Обоим правительствам предстоит решить, как устроить их союз и что делать с краями.'),
 [(['set_country_flag = YGwar_dissolution_started',coh(50),'set_country_flag = YGwar_outcome_rump_union','add_stability = 0.05'],('Keep the union of Serbia and Montenegro with the provinces','Сохранить союз Сербии и Черногории с краями'),None),
  (['YGwar_secede_VOJ_all = yes','YGwar_secede_KOS_all = yes','set_country_flag = YGwar_outcome_rump_union'],('Let Vojvodina and Kosovo go their own way','Позволить Воеводине и Косову идти своим путём'),None),
  (['YGwar_secede_MNT_all = yes','set_country_flag = YGwar_outcome_rump_union'],('Let Montenegro leave the union','Позволить Черногории выйти из союза'),None)])
ev(30,('The End of the Federation','Конец федерации'),
 ('The republics no longer agree on anything but the date of the last session. The Presidency must decide how the state ends.',
  'Республики больше не согласны ни в чём, кроме даты последнего заседания. Президиум должен решить, как закончится государство.'),
 [(['country_event = { id = YGwar.20 }'],('An orderly dissolution by agreement','Упорядоченный роспуск по соглашению'),None),
  (['YGwar_contested_dissolution_phase1 = yes','set_country_flag = YGwar_outcome_contested_dissolution','country_event = { id = YGwar.31 days = 30 }'],('Dissolution without agreement','Роспуск без соглашения'),None),
  ([coh(6),loy(-6),'add_political_power = -60'],('Hold the federation together a little longer','Удержать федерацию ещё ненадолго'),None)],
 trigger='NOT = { has_country_flag = YGwar_dissolution_started }')
ev(31,('Bosnia and Herzegovina Divided','Босния и Герцеговина расколота'),
 ('With Croatia at war and its Serb districts in revolt, Bosnia and Herzegovina is pulled apart. The three communities form their own administrations.',
  'Когда Хорватия воюет, а её сербские районы восстали, Боснию и Герцеговину растаскивают в разные стороны. Три общины создают собственные администрации.'),
 [(['YGwar_secede_BOS_core = yes','YGwar_secede_RSB_all = yes','YGwar_secede_HRZ_all = yes','set_country_flag = YGwar_BOS_left','set_country_flag = YGwar_BOS_partitioned'],('The three communities part ways','Три общины расходятся'),None)],
 trigger='NOT = { has_country_flag = YGwar_BOS_left }')
ev(40,('The Final Settlement','Окончательное урегулирование'),
 ('Federal forces, commissioners and the unity campaign move at the same time. The outcome depends on whether the security forces follow orders.',
  'Федеральные силы, комиссары и кампания за единство действуют одновременно. Исход зависит от того, выполнят ли приказы силовые структуры.'),
 [(['if = { limit = { check_variable = { militia_loyalty > 59 } } set_country_flag = YGwar_outcome_centralized add_ideas = YUG_centralized_state set_country_flag = YGwar_federation_stabilized YGwar_add_cohesion = { VAL = 20 } add_stability = -0.03 } else = { YGwar_add_cohesion = { VAL = -25 } YGwar_add_loyalty = { VAL = -15 } add_stability = -0.10 set_country_flag = YGwar_final_settlement_failed country_event = { id = YGwar.30 days = 7 } }'],('Carry out the settlement','Провести урегулирование'),None)])
# --- outcomes
ev(50,('A Reformed Federation','Реформированная федерация'),
 ('The republics ratify a constitution that all of them helped write. It does not end every dispute, but it gives them a place to settle them.',
  'Республики ратифицируют конституцию, к написанию которой приложили руку все. Она не прекращает все споры, но даёт место, где их можно решить.'),
 [(['set_country_flag = YGwar_outcome_reformed_federation','set_country_flag = YGwar_federation_stabilized',coh(20),'add_ideas = YUG_reformed_federation','if = { limit = { has_idea = YUG_federal_trust_crisis } remove_ideas = YUG_federal_trust_crisis }','if = { limit = { has_idea = YUG_republican_particularism } remove_ideas = YUG_republican_particularism }'],('Close the crisis by agreement','Закрыть кризис по согласию'),None)])
ev(51,('A New Democratic Compact','Новый демократический договор'),
 ('Elected governments sign a compact that gives the federation a smaller but better-defined role.',
  'Избранные правительства подписывают договор, оставляющий федерации меньшую, но лучше определённую роль.'),
 [(['set_country_flag = YGwar_outcome_democratic_federation','set_country_flag = YGwar_federation_stabilized',coh(15),'add_ideas = YUG_democratic_institutions','if = { limit = { has_idea = YUG_federal_trust_crisis } remove_ideas = YUG_federal_trust_crisis }','if = { limit = { has_idea = YUG_republican_particularism } remove_ideas = YUG_republican_particularism }'],('Keep a democratic federation','Сохранить демократическую федерацию'),None),
  (['set_country_flag = YGwar_outcome_democratic_confederation','set_country_flag = YGwar_federation_stabilized',coh(8),'set_country_flag = YUG_confederation_track','add_ideas = YUG_confederal_bargaining','if = { limit = { has_idea = YUG_federal_trust_crisis } remove_ideas = YUG_federal_trust_crisis }'],('Settle on a democratic confederation','Остановиться на демократической конфедерации'),None)])
ev(52,('The Economic and Defence Union','Экономический и оборонный союз'),
 ('Sovereign republics sign a union treaty. One market, one defence council, and a standing right to review membership.',
  'Суверенные республики подписывают договор о союзе. Единый рынок, единый оборонный совет и постоянное право пересматривать членство.'),
 [(['set_country_flag = YGwar_outcome_confederation','set_country_flag = YGwar_federation_stabilized',coh(20),'add_ideas = YUG_confederal_bargaining','add_ideas = YUG_joint_defence'],('Ratify the union','Ратифицировать союз'),None)])
ev(53,('Compact between Workers and State','Соглашение рабочих и государства'),
 ('Workers\' organizations, enterprises and the state sign a long-term compact on wages, investment and self-management.',
  'Рабочие организации, предприятия и государство подписывают долгосрочное соглашение о зарплатах, инвестициях и самоуправлении.'),
 [(['set_country_flag = YGwar_outcome_socialist_renewal','set_country_flag = YGwar_federation_stabilized',coh(15),'add_ideas = YUG_workers_councils','add_stability = 0.05','if = { limit = { has_idea = YUG_federal_trust_crisis } remove_ideas = YUG_federal_trust_crisis }'],('Sign the compact','Подписать соглашение'),None)])
ev(54,('Results of the Elections','Результаты выборов'),
 ('The first competitive elections are over. A reformist list and a conservative-compromise coalition both claim the right to form the government.',
  'Первые конкурентные выборы позади. Реформистский список и консервативно-компромиссная коалиция оба претендуют на право сформировать правительство.'),
 [(['recruit_character = YUG_ana_kovac','if = { limit = { NOT = { has_country_flag = YGwar_regime_set } } set_country_flag = YGwar_regime_set set_country_flag = YGwar_regime_liberal set_politics = { ruling_party = democratic } promote_character = YUG_ana_kovac }','add_popularity = { ideology = democratic popularity = 0.1 }',coh(4)],('The reformist list forms the government','Реформистский список формирует правительство'),None),
  (['recruit_character = YUG_jelena_ilic','if = { limit = { NOT = { has_country_flag = YGwar_regime_set } } set_country_flag = YGwar_regime_set set_country_flag = YGwar_regime_coalition set_politics = { ruling_party = democratic } promote_character = YUG_jelena_ilic }',coh(6),'add_political_power = -25'],('A coalition of compromise forms the government','Формируется компромиссная коалиция'),None)])
# ---------- render
out=['# YGwar - federation crisis events (GENERATED by tools/build_events.py). Namespace YGwar is declared in events/YGwar_events.txt.','']
loc=[]
for e in E:
    n=e['n']; out.append('country_event = {'); out.append(f'\tid = YGwar.{n}'); out.append(f'\ttitle = YGwar.{n}.t'); out.append(f'\tdesc = YGwar.{n}.d'); out.append(f'\tpicture = {PIC}')
    out.append('\tis_triggered_only = yes')
    out.append('\ttrigger = {\n\t\ttag = YUG\n'+(f'\t\t{e["trigger"]}\n' if e['trigger'] else '')+'\t}')
    if e['immediate']: out.append('\timmediate = {\n\t\t'+e['immediate']+'\n\t}')
    for i,(eff,en,ru) in enumerate(e['opts']):
        k='abc'[i]; out.append('\toption = {'); out.append(f'\t\tname = YGwar.{n}.{k}')
        for x in eff: out.append('\t\t'+x)
        out.append('\t}')
    out.append('}\n')
    loc.append((f'YGwar.{n}.t',e['title'][0],e['title'][1])); loc.append((f'YGwar.{n}.d',e['desc'][0],e['desc'][1]))
    for i,(eff,en,ru) in enumerate(e['opts']): loc.append((f'YGwar.{n}.{"abc"[i]}',en[0],en[1]))
open(os.path.join(ROOT,'events','YGwar_crisis_events.txt'),'w',encoding='utf-8').write('\n'.join(out))
json.dump(loc,open(os.path.join(ROOT,'tools','_events_loc.json'),'w',encoding='utf-8'),ensure_ascii=False)
print('events',len(E),'options',sum(len(e['opts']) for e in E))
