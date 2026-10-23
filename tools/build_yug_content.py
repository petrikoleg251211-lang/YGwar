#!/usr/bin/env python3
"""Generates the Yugoslavia content pass (focus tree, localisation). Re-runnable.
Writes: common/national_focus/YUG_focus.txt, localisation/*/YGwar_yug_l_*.yml"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def coh(n): return f'YGwar_add_cohesion = {{ VAL = {n} }}'
def loy(n): return f'YGwar_add_loyalty = {{ VAL = {n} }}'
def pp(n): return f'add_political_power = {n}'
def stab(n): return f'add_stability = {n}'
def war(n): return f'add_war_support = {n}'
def idea(i): return f'add_ideas = {i}'
def swap(a,b): return f'swap_ideas = {{ remove_idea = {a} add_idea = {b} }}'
def flag(f): return f'set_country_flag = {f}'
def ev(i): return f'country_event = {{ id = YGwar.{i} }}'
CIV='YGwar_build_civ = yes'; MIL='YGwar_build_mil = yes'; INF='YGwar_build_infra = yes'
def leader(ch, party, fl):
    return (f'recruit_character = {ch}\n'
            f'if = {{ limit = {{ NOT = {{ has_country_flag = YGwar_regime_set }} }}\n'
            f'  set_country_flag = YGwar_regime_set\n  set_country_flag = {fl}\n'
            f'  set_politics = {{ ruling_party = {party} }}\n  promote_character = {ch} }}')
I1,I2,I3,I4,I5,I6,I7='national_unity','political_pressure','construct_civilian','army_doctrines','construct_military','major_war','demand_territory'
F=[]  # dicts
def f(id,x,y,cost,icon,pre=(),orp=(),mx=(),av='',rw=(),en=('',''),ru=('',''),ai=None):
    F.append(dict(id='YUG_'+id,x=x,y=y,cost=cost,icon='GFX_goal_generic_'+icon,pre=['YUG_'+p for p in pre],orp=['YUG_'+p for p in orp],mx=['YUG_'+p for p in mx],av=av,rw=list(rw),en=en,ru=ru,ai=ai))
FIN=['constitutional_settlement','democratic_social_compact','economic_defence_union','final_settlement_attempt','workers_state_compact']
def fin(me): return [x for x in FIN if x!=me]
# ---------------- TRUNK ----------------
f('organize_the_federation',0,0,5,I1,rw=[stab(0.05),'add_ideas = YUG_reform_impulse_start' if False else pp(30)],
  en=('Organize the Federal Government','Settle the working order of the federal cabinet, the Presidency and the republican delegations before the crisis forces the issue.'),
  ru=('Организация работы федерального правительства','Выстроить рабочий порядок федерального кабинета, Президиума и республиканских делегаций, пока кризис не вынудил к спешке.'))
f('strengthen_federal_institutions',-2,1,5,I2,pre=['organize_the_federation'],rw=[pp(50),coh(3)],
  en=('Strengthen Federal Institutions','Give federal bodies the staff and the budget to carry out their decisions.'),
  ru=('Укрепление федеральных институтов','Дать федеральным органам кадры и бюджет, чтобы их решения исполнялись.'))
f('modernize_the_economy',2,1,5,I3,pre=['organize_the_federation'],rw=[pp(25),stab(0.03),CIV],
  en=('Modernize the Economy','Open the debate on ownership, enterprise management and the role of the market.'),
  ru=('Модернизация экономики','Открыть дискуссию о собственности, управлении предприятиями и роли рынка.'))
f('reform_the_army',-2,2,5,I4,pre=['strengthen_federal_institutions'],rw=[war(0.05),loy(5)],
  en=('Reform the Army','Review the structure of the Yugoslav People\'s Army and its relation to the republics.'),
  ru=('Реформа армии','Пересмотреть структуру Югославской народной армии и её отношения с республиками.'))
f('defend_the_adriatic',2,2,5,I5,pre=['modernize_the_economy'],rw=[war(0.05),MIL],
  en=('Defend the Adriatic','Secure the coast, the ports and the coastal roads that bind the federation together.'),
  ru=('Оборона Адриатики','Обеспечить побережье, порты и прибрежные дороги, связывающие федерацию.'))
f('yugoslav_future',0,3,5,I6,pre=['reform_the_army','defend_the_adriatic'],rw=[pp(100),stab(0.05),coh(2)],
  en=('The Yugoslav Future','The groundwork is laid. The question now is which Yugoslavia the republics will accept.'),
  ru=('Будущее Югославии','Основа заложена. Теперь вопрос в том, какую Югославию примут республики.'))
f('rising_nationalism',0,4,7,I7,pre=['yugoslav_future'],rw=[coh(-15),stab(-0.05),flag('YUG_nationalism_rising')],
  en=('Rising Nationalism','National movements gain ground in every republic and the common language of politics begins to fail.'),
  ru=('Рост национализма','Национальные движения набирают силу во всех республиках, и общий язык политики перестаёт работать.'))
f('crisis_of_federal_trust',0,5,7,I2,pre=['rising_nationalism'],rw=[coh(-8),idea('YUG_federal_trust_crisis'),flag('YGwar_trust_crisis_acknowledged')],
  en=('Crisis of Federal Trust','Republics stop believing that federal bodies speak for them. Every decision is read as a favour to someone else.'),
  ru=('Кризис федерального доверия','Республики перестают верить, что федеральные органы говорят от их имени. Любое решение читают как услугу кому-то другому.'))
f('emergency_republic_talks',0,6,7,I1,pre=['crisis_of_federal_trust'],rw=[coh(5),pp(-25),flag('YGwar_talks_opened')],
  en=('Emergency Talks with the Republics','Call the republican leaders to a closed session. Nothing is agreed, but everyone is in the room.'),
  ru=('Чрезвычайные переговоры с республиками','Созвать республиканских лидеров на закрытое заседание. Ничего не решено, но все сидят в одной комнате.'))
f('crackdown_on_separatism',-2,7,10,I2,pre=['emergency_republic_talks'],mx=['allow_self_determination','constitutional_compromise_attempt'],
  rw=[war(0.10),stab(-0.05),loy(-10),coh(-6),flag('YUG_chose_crackdown')],ai=3,
  en=('Crackdown on Separatism','Treat separatist organisations as a threat to the constitutional order and act accordingly.'),
  ru=('Подавление сепаратизма','Рассматривать сепаратистские организации как угрозу конституционному порядку и действовать соответственно.'))
f('constitutional_compromise_attempt',0,7,10,I1,pre=['emergency_republic_talks'],mx=['crackdown_on_separatism','allow_self_determination'],
  av='check_variable = { federation_cohesion > 29 }',
  rw=[coh(12),pp(-50),flag('YUG_chose_compromise'),leader('YUG_mirko_stankovic','democratic','YGwar_regime_compromise')],ai=6,
  en=('Constitutional Compromise Attempt','Put a package on the table: wider republican powers, a guaranteed federal core, and a timetable for both.'),
  ru=('Попытка конституционного компромисса','Выложить на стол пакет: расширенные права республик, гарантированное федеральное ядро и график для обоих.'))
f('allow_self_determination',2,7,10,I1,pre=['emergency_republic_talks'],mx=['crackdown_on_separatism','constitutional_compromise_attempt'],
  rw=[stab(0.05),coh(-12),flag('YUG_chose_self_determination')],ai=1,
  en=('Allow Self-Determination','Accept in principle that each republic may decide its own future, and manage what follows.'),
  ru=('Признать самоопределение','Принять в принципе, что каждая республика вправе решать свою судьбу, и управлять тем, что последует.'))
f('federal_collapse',0,10,10,I6,orp=['crackdown_on_separatism','allow_self_determination','constitutional_compromise_attempt'],
  av='check_variable = { federation_cohesion < 41 }',rw=[flag('YGwar_collapse_reached'),ev(30)],ai=0.2,
  en=('Federal Collapse','The federation can no longer hold its republics together by consent. What remains is to decide how it ends.'),
  ru=('Крах федерации','Федерация больше не может удерживать республики вместе по согласию. Остаётся решить, как всё закончится.'))
# ---------------- A: federal system ----------------
f('republic_leaders_council',-4,2,5,I1,pre=['strengthen_federal_institutions'],rw=[pp(40),coh(5),flag('YGwar_leaders_council')],
  en=('Permanent Council of Republican Leaders','A standing body where presidents of the republics meet monthly, with minutes.'),
  ru=('Постоянный совет лидеров республик','Постоянный орган, где президенты республик встречаются ежемесячно, с протоколами.'))
f('administrative_reform',-4,3,5,I2,pre=['republic_leaders_council'],rw=[swap('YUG_federal_bureaucracy','YUG_streamlined_administration'),stab(0.03)],
  en=('Administrative Reform','Cut overlapping federal departments and make civil service careers depend on results.'),
  ru=('Административная реформа','Сократить дублирующие федеральные ведомства и поставить карьеру чиновников в зависимость от результата.'))
f('review_competences',-6,3,5,I2,pre=['republic_leaders_council'],rw=[coh(4),pp(-20),flag('YGwar_competences_reviewed')],
  en=('Review the Division of Powers','Go through every federal competence and ask whether the republics could carry it better.'),
  ru=('Пересмотр разграничения полномочий','Пройти по каждому федеральному полномочию и спросить, не справятся ли республики лучше.'))
f('provinces_settlement',-6,4,6,I1,pre=['review_competences'],rw=[coh(5),flag('YGwar_provinces_settled')],
  en=('Settlement with the Autonomous Provinces','Clarify the position of Vojvodina and Kosovo inside the federation and within Serbia.'),
  ru=('Урегулирование с автономными краями','Уточнить положение Воеводины и Косова в федерации и в составе Сербии.'))
f('new_federal_treaty',-5,5,8,I1,pre=['administrative_reform','provinces_settlement'],av='check_variable = { federation_cohesion > 44 }',
  rw=[coh(10),pp(75),flag('YGwar_federal_treaty')],
  en=('A New Federal Treaty','Replace the patchwork of amendments with one treaty all republics sign.'),
  ru=('Новый федеральный договор','Заменить лоскутное одеяло поправок единым договором, который подпишут все республики.'))
f('constitutional_settlement',-5,6,10,I1,pre=['new_federal_treaty'],mx=fin('constitutional_settlement'),
  av='check_variable = { federation_cohesion > 49 }',rw=[ev(50)],ai=10,
  en=('Constitutional Settlement','Ratify the reformed constitution and close the crisis by agreement.'),
  ru=('Конституционное урегулирование','Ратифицировать реформированную конституцию и закрыть кризис по согласию.'))
# ---------------- B: economy ----------------
f('currency_stabilization',4,2,5,I3,pre=['modernize_the_economy'],rw=[stab(0.03),pp(25)],
  en=('Stabilize the Currency','Peg the dinar to a hard anchor and defend it with reserves.'),
  ru=('Стабилизация валюты','Привязать динар к твёрдому якорю и защищать его резервами.'))
f('fight_inflation',4,3,6,I3,pre=['currency_stabilization'],rw=[swap('YUG_economic_instability','YUG_stabilization_programme'),stab(0.03)],
  en=('Fight Inflation','Wage restraint, a hard budget limit and a price watch. Unpopular, and it works.'),
  ru=('Борьба с инфляцией','Сдерживание зарплат, жёсткий бюджетный лимит и контроль цен. Непопулярно, но работает.'))
f('banking_reform',6,3,6,I3,pre=['currency_stabilization'],rw=[pp(40),leader('YUG_dragan_vukic','democratic','YGwar_regime_reformist')],
  en=('Banking System Reform','Separate commercial banks from republican patronage and set common reserve rules.'),
  ru=('Реформа банковской системы','Отделить коммерческие банки от республиканского патронажа и ввести общие правила резервирования.'))
f('industrial_stimulus',3,4,6,I3,pre=['fight_inflation'],rw=[CIV,CIV,'add_ideas = YUG_industrial_potential' if False else stab(0.01)],
  en=('Industrial Stimulus','Credit lines for machine building, steel and vehicles in the main industrial districts.'),
  ru=('Стимулирование промышленности','Кредитные линии для машиностроения, металлургии и автомобилестроения в главных промышленных районах.'))
f('energy_modernization',5,4,6,I3,pre=['fight_inflation','banking_reform'],rw=[CIV,INF],
  en=('Energy Modernization','Rebuild the power grid and link republican systems into one network.'),
  ru=('Модернизация энергетики','Перестроить энергосеть и объединить республиканские системы в одну.'))
f('transport_programme',7,4,6,I3,pre=['banking_reform'],rw=[INF,INF,'add_ideas = YUG_rail_road_programme'],
  en=('Rail and Road Programme','Finish the motorway and modernize the main railway lines between republics.'),
  ru=('Программа железных и автомобильных дорог','Достроить автомагистраль и модернизировать главные железные дороги между республиками.'))
f('agriculture_modernization',5,5,5,I3,pre=['energy_modernization'],rw=[CIV,stab(0.02),'add_ideas = YUG_modern_agriculture'],
  en=('Modernize Agriculture','Cooperatives, machinery and storage so the harvest stops depending on the weather alone.'),
  ru=('Модернизация сельского хозяйства','Кооперативы, техника и хранилища, чтобы урожай не зависел только от погоды.'))
f('adriatic_tourism',7,5,5,I3,pre=['transport_programme'],rw=[CIV,pp(30),stab(0.02)],
  en=('Adriatic Tourism','Hotels, harbours and a unified marketing board for the coast.'),
  ru=('Туризм на Адриатике','Отели, гавани и единое туристическое ведомство для побережья.'))
f('economic_equalization',4,6,8,I1,pre=['industrial_stimulus','agriculture_modernization'],rw=[coh(7),pp(-40),CIV,flag('YGwar_equalization')],
  en=('Economic Equalization Programme','A federal fund for the poorer republics. The richer ones notice the bill.'),
  ru=('Программа экономического выравнивания','Федеральный фонд для бедных республик. Богатые замечают счёт.'))
f('export_led_strategy',4,7,7,I3,pre=['economic_equalization'],mx=['internal_market_strategy'],rw=[CIV,'add_ideas = YUG_export_orientation',flag('YGwar_strategy_export')],
  en=('Export-Led Strategy','Bet on foreign markets: faster growth, more exposure to outside shocks.'),
  ru=('Экспортная стратегия','Ставка на внешние рынки: рост быстрее, зависимость от внешних потрясений сильнее.'))
f('internal_market_strategy',6,7,7,I3,pre=['economic_equalization'],mx=['export_led_strategy'],rw=[coh(4),'add_ideas = YUG_common_market',flag('YGwar_strategy_internal')],
  en=('Internal Market Strategy','Bind republican economies together through a common market and shared supply chains.'),
  ru=('Стратегия внутреннего рынка','Связать республиканские экономики общим рынком и общими цепочками поставок.'))
# ---------------- C: democratization ----------------
f('reform_the_constitution',8,1,5,I1,pre=['organize_the_federation'],rw=[pp(30)],
  en=('Open the Constitutional Question','Admit that the 1974 constitution needs rewriting and set up the process.'),
  ru=('Открыть конституционный вопрос','Признать, что конституцию 1974 года нужно переписывать, и запустить процесс.'))
f('political_liberalization',9,2,6,I2,pre=['reform_the_constitution'],rw=[stab(0.02),pp(40)],
  en=('Political Liberalization','Loosen censorship, allow independent associations and open parliamentary debate.'),
  ru=('Политическая либерализация','Ослабить цензуру, разрешить независимые объединения и открыть парламентские дебаты.'))
f('electoral_law_review',11,2,6,I2,pre=['reform_the_constitution'],rw=[pp(40),flag('YGwar_electoral_law')],
  en=('Review the Electoral Law','Draft rules for competitive elections that every republic can accept.'),
  ru=('Пересмотр избирательного закона','Подготовить правила конкурентных выборов, приемлемые для каждой республики.'))
f('judicial_reform',9,3,6,I2,pre=['political_liberalization'],rw=[stab(0.03),coh(3)],
  en=('Judicial Reform','Courts that are protected from party instructions and republican pressure.'),
  ru=('Судебная реформа','Суды, защищённые от партийных указаний и республиканского давления.'))
f('civil_liberties',11,3,6,I2,pre=['electoral_law_review'],rw=[stab(0.03),'add_ideas = YUG_democratic_institutions'],
  en=('Protect Civil Liberties','Freedom of assembly, press and association written into federal law.'),
  ru=('Защита гражданских свобод','Свобода собраний, печати и объединений, закреплённая в федеральном законе.'))
f('competitive_elections',10,4,8,I1,pre=['judicial_reform','civil_liberties'],rw=[flag('YGwar_elections_held'),ev(54)],
  en=('Competitive Elections','Hold multi-party elections for federal and republican assemblies.'),
  ru=('Конкурентные выборы','Провести многопартийные выборы в федеральные и республиканские собрания.'))
f('civilian_control_of_army',12,4,6,I4,pre=['civil_liberties'],rw=[loy(-6),coh(4),stab(0.03)],
  en=('Civilian Control of the Army','Put the army under parliamentary budget oversight. The officer corps takes note.'),
  ru=('Гражданский контроль над армией','Поставить армию под парламентский бюджетный контроль. Офицерский корпус принимает это к сведению.'))
f('democratic_social_compact',10,5,10,I1,pre=['competitive_elections'],mx=fin('democratic_social_compact'),
  av='check_variable = { federation_cohesion > 39 }\nhas_country_flag = YGwar_elections_held',rw=[ev(51)],ai=3,
  en=('A New Democratic Compact','A treaty between elected governments in place of a treaty between party leaderships.'),
  ru=('Новый демократический договор','Договор между избранными правительствами вместо договора между партийными руководствами.'))
# ---------------- D: federalization ----------------
f('division_of_powers',2,8,6,I2,pre=['allow_self_determination'],rw=[coh(3),pp(-30),flag('YGwar_powers_divided')],
  en=('Divide Powers','A written list of what belongs to the federation and what to the republics.'),
  ru=('Разделение полномочий','Письменный перечень того, что принадлежит федерации, а что республикам.'))
f('budget_autonomy_talks',4,8,6,I3,pre=['allow_self_determination'],rw=[coh(3),pp(-30)],
  en=('Budget Autonomy Talks','Negotiate how much of each republic\'s revenue stays at home.'),
  ru=('Переговоры о бюджетной самостоятельности','Договориться, какая часть доходов каждой республики остаётся дома.'))
f('joint_defence_treaty',2,9,7,I5,pre=['division_of_powers'],rw=[war(0.03),'add_ideas = YUG_joint_defence'],
  en=('Joint Defence Treaty','Republican forces and the federal army commit to a common defence plan.'),
  ru=('Договор о совместной обороне','Республиканские силы и федеральная армия принимают общий оборонный план.'))
f('confederal_model',4,9,8,I1,pre=['division_of_powers','budget_autonomy_talks'],rw=[flag('YGwar_confederation_track'),ev(14),pp(-40)],
  en=('Move to a Confederal Model','Sovereign republics delegate chosen powers to a common centre.'),
  ru=('Переход к конфедеративной модели','Суверенные республики делегируют общему центру отдельные полномочия.'))
f('peaceful_exit_terms',2,10,7,I2,pre=['joint_defence_treaty'],rw=[flag('YGwar_exit_terms_agreed'),pp(60),flag('YGwar_transition_prepared')],
  en=('Terms of Peaceful Exit','Write down how a republic may leave: referendum, debts, army property, citizenship.'),
  ru=('Условия мирного выхода','Записать, как республика может выйти: референдум, долги, имущество армии, гражданство.'))
f('economic_defence_union',4,11,10,I3,pre=['confederal_model','peaceful_exit_terms'],mx=fin('economic_defence_union'),
  av='has_country_flag = YGwar_confederation_track\ncheck_variable = { federation_cohesion > 24 }',rw=[ev(52)],ai=3,
  en=('Economic and Defence Union','Keep one market and one defence even if the republics are sovereign.'),
  ru=('Экономический и оборонный союз','Сохранить единый рынок и единую оборону, даже если республики суверенны.'))
# ---------------- E: centralization ----------------
f('security_forces_reform',-4,8,6,I4,pre=['crackdown_on_separatism'],rw=[loy(8),pp(-30)],
  en=('Reform the Security Forces','Merge overlapping federal police and security services under one command.'),
  ru=('Реформа силовых структур','Свести пересекающиеся федеральные полицейские и спецслужбы под единое командование.'))
f('disarm_illegal_formations',-2,8,6,I4,pre=['crackdown_on_separatism'],rw=[loy(4),coh(-4),stab(-0.03),war(0.03)],
  en=('Disarm Illegal Formations','Seize weapons from unauthorized local armed groups before they organize.'),
  ru=('Разоружение незаконных формирований','Изъять оружие у неразрешённых местных вооружённых групп, пока они не организовались.'))
f('centralize_defence_planning',-6,9,7,I5,pre=['security_forces_reform'],rw=[war(0.05),loy(4),'add_ideas = YUG_central_defence_planning'],
  en=('Centralize Defence Planning','All defence plans, depots and call-up lists answer to one general staff.'),
  ru=('Централизация оборонного планирования','Все оборонные планы, склады и списки призыва подчиняются одному генеральному штабу.'))
f('federal_administrative_control',-4,9,7,I2,pre=['security_forces_reform','disarm_illegal_formations'],
  rw=[pp(75),coh(-5),leader('YUG_stevan_jovanov','neutrality','YGwar_regime_centralist')],
  en=('Federal Administrative Control','Appoint federal commissioners to supervise republican administrations.'),
  ru=('Федеральный административный контроль','Назначить федеральных комиссаров для надзора за республиканскими администрациями.'))
f('unity_campaign',-2,9,6,I1,pre=['disarm_illegal_formations'],av='check_variable = { federation_cohesion < 70 }',rw=[coh(6),stab(0.02),pp(-30)],
  en=('Campaign for Unity','A political campaign for the common state, from schools to factory floors.'),
  ru=('Кампания за единство','Политическая кампания за общее государство: от школ до заводских цехов.'))
f('federal_army_rearmament',-6,10,8,I5,pre=['centralize_defence_planning'],rw=[MIL,MIL,loy(6),stab(-0.02)],
  en=('Rearm the Federal Army','New equipment for the units the federation trusts most.'),
  ru=('Перевооружение федеральной армии','Новая техника для частей, которым федерация доверяет больше всего.'))
f('final_settlement_attempt',-4,11,10,I6,pre=['federal_administrative_control','unity_campaign'],mx=fin('final_settlement_attempt'),
  av='check_variable = { militia_loyalty > 29 }',rw=[ev(40)],ai=2,
  en=('Attempt a Final Settlement','Use every federal lever at once to end the crisis on the centre\'s terms.'),
  ru=('Попытка окончательного урегулирования','Задействовать все федеральные рычаги сразу, чтобы закончить кризис на условиях центра.'))
# ---------------- F: socialist ----------------
f('reform_socialist_institutions',14,2,6,I1,pre=['modernize_the_economy'],rw=[pp(40),leader('YUG_milos_radic','communism','YGwar_regime_socialist')],
  en=('Reform Socialist Institutions','Renew party and state bodies and return them to the programme of self-management.'),
  ru=('Реформа социалистических институтов','Обновить партийные и государственные органы и вернуть их к программе самоуправления.'))
f('workers_organizations',14,3,6,I1,pre=['reform_socialist_institutions'],rw=[stab(0.03),'add_ideas = YUG_workers_councils'],
  en=('Rebuild Workers\' Organizations','Elected works councils with a real say in wages and investment.'),
  ru=('Восстановление рабочих организаций','Выборные рабочие советы с реальным голосом в вопросах зарплат и инвестиций.'))
f('state_enterprise_modernization',16,3,6,I3,pre=['reform_socialist_institutions'],rw=[CIV,MIL],
  en=('Modernize State Enterprises','Replace worn-out plant in the state sector before closing it down.'),
  ru=('Модернизация госпредприятий','Заменить изношенное оборудование в государственном секторе, прежде чем его закрывать.'))
f('social_security',14,4,6,I1,pre=['workers_organizations'],rw=[stab(0.04),pp(-30)],
  en=('Renew Social Security','Pensions, health and housing funded from one federal formula.'),
  ru=('Обновление социального обеспечения','Пенсии, здравоохранение и жильё, финансируемые по единой федеральной формуле.'))
f('employment_programme',16,4,6,I3,pre=['state_enterprise_modernization'],rw=[CIV,stab(0.02)],
  en=('Employment Programme','Public works and retraining for regions that lose factories.'),
  ru=('Программа занятости','Общественные работы и переобучение для регионов, теряющих заводы.'))
f('workers_state_compact',15,5,10,I1,pre=['social_security','employment_programme'],mx=fin('workers_state_compact'),
  av='check_variable = { federation_cohesion > 34 }',rw=[ev(53)],ai=2,
  en=('Compact between Workers and State','A new settlement between workers\' organizations, enterprises and the state.'),
  ru=('Соглашение рабочих и государства','Новое соглашение между рабочими организациями, предприятиями и государством.'))
# ---------------- G: army ----------------
f('modernize_ground_forces',-10,3,6,I4,pre=['reform_the_army'],rw=[war(0.03),'add_ideas = YUG_army_modernization' if False else loy(3)],
  en=('Modernize Ground Forces','A modernization plan for the infantry core of the army.'),
  ru=('Модернизация сухопутных войск','План модернизации пехотного ядра армии.'))
f('armoured_units',-12,4,6,I4,pre=['modernize_ground_forces'],rw=[MIL],
  en=('Develop Armoured Units','Concentrate tanks in a few well-supplied formations.'),
  ru=('Развитие бронетанковых частей','Сосредоточить танки в нескольких хорошо снабжаемых соединениях.'))
f('artillery_modernization',-10,4,6,I4,pre=['modernize_ground_forces'],rw=[MIL],
  en=('Modernize Artillery','Fire-control, towing and stocks of shells.'),
  ru=('Модернизация артиллерии','Управление огнём, тяга и запасы снарядов.'))
f('reservist_training',-8,4,6,I4,pre=['modernize_ground_forces'],rw=[war(0.03),'add_ideas = YUG_trained_reserves'],
  en=('Train the Reservists','Regular refresher courses for the mobilization pool.'),
  ru=('Подготовка резервистов','Регулярные курсы переподготовки для мобилизационного резерва.'))
f('territorial_defence_coordination',-8,5,7,I5,pre=['reservist_training'],rw=[loy(-3),coh(-2),'add_ideas = YUG_territorial_defence_network'],
  en=('Coordinate Territorial Defence','Agree how republican territorial defence fits the federal plan. Each republic keeps its own stores.'),
  ru=('Координация территориальной обороны','Договориться, как республиканская территориальная оборона вписывается в федеральный план. Каждая республика держит свои склады.'))
f('military_industry_programme',-11,5,8,I5,pre=['armoured_units','artillery_modernization'],rw=[MIL,MIL,CIV],
  en=('Military Industry Programme','Expand the arsenal districts and secure the supply of components.'),
  ru=('Программа военной промышленности','Расширить арсенальные районы и обеспечить поставки комплектующих.'))
f('civilian_oversight_of_army',-8,6,6,I2,pre=['territorial_defence_coordination'],rw=[coh(3),loy(-5),stab(0.03)],
  en=('Civilian Oversight of the Army','Establish a defence committee of delegates with budget powers.'),
  ru=('Гражданский надзор над армией','Создать оборонный комитет делегатов с бюджетными полномочиями.'))
f('crisis_contingency_planning',-10,6,7,I6,pre=['military_industry_programme','territorial_defence_coordination'],rw=[loy(4),flag('YGwar_contingency_planned')],
  en=('Contingency Planning for State Crisis','Plans for each scenario of the crisis, kept in the general staff safe.'),
  ru=('Планирование на случай кризиса государства','Планы для каждого сценария кризиса, хранящиеся в сейфе генерального штаба.'))
# ---------------------------------------------------
ids={x['id'] for x in F}
assert len(ids)==len(F),'dup id'
pos=set()
for x in F:
    assert (x['x'],x['y']) not in pos, ('pos clash',x['id'],x['x'],x['y']); pos.add((x['x'],x['y']))
    for p in x['pre']+x['orp']+x['mx']: assert p in ids,(x['id'],p)
byid={x['id']:x for x in F}
for x in F:
    for p in x['pre']+x['orp']: assert byid[p]['y']<x['y'] or p==x['id'], ('order',x['id'],p)
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
    L.append('\t\t}'); L.append('\t}'); return '\n'.join(L)
tree='# YGwar - Yugoslavia focus tree. GENERATED by tools/build_yug_content.py (edit the script, then re-run).\nfocus_tree = {\n\tid = YUG_focus_tree\n\tcountry = {\n\t\tfactor = 0\n\t\tmodifier = { add = 100 tag = YUG }\n\t}\n\n'+'\n\n'.join(block(x) for x in F)+'\n}\n'
open(os.path.join(ROOT,'common','national_focus','YUG_focus.txt'),'w',encoding='utf-8').write(tree)
import json
json.dump([dict(id=x['id'],en=x['en'],ru=x['ru']) for x in F],open(os.path.join(ROOT,'tools','_yug_focus_loc.json'),'w',encoding='utf-8'),ensure_ascii=False)
print('focuses:',len(F))
