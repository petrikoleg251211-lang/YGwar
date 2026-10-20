YGwar v6 — виправлення за error.log (2026-10-19)
=================================================

ЯК ВСТАНОВИТИ
1. Закрий гру. Розпакуй архів поверх папки моду
   Documents/Paradox Interactive/Hearts of Iron IV/mod/my_own_mod/  (з заміною файлів).
   Файл descriptor.mod у Documents/.../mod/ (my_own_mod.mod) не чіпай.
2. КРОК 2 — ТЕХНОЛОГІЇ (потрібен один раз, робить 90% решти помилок):
   Відкрий PowerShell у папці моду і запусти (шлях до гри підстав свій):

   python tools/sanitize_vanilla_techs.py --game "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV"

   Скрипт читає ванільні infantry.txt / support.txt / naval.txt, прибирає звернення до неіснуючих
   тегів (GER, SOV, ITA ...) і кладе виправлені копії в common/technologies/ мода.
   Ванільні файли в папці гри НЕ змінюються. Звіт: tools/sanitize_report.txt.
3. Запусти гру, зайди в нову кампанію, і скинь свіжий error.log.

ЩО ВИПРАВЛЕНО В АРХІВІ
- sabotaged_resources: додано (common/dynamic_modifiers/YGwar_dynamic_modifiers.txt), без ефектів.
- autonomy_dominion: прибрано з common/collections/collections.txt.
- Лідери: невалідні experience_gain_factor / skill_factor у common/unit_leader/00_traits.txt.
- Локалізація: YGwar_tech_share (+_desc); назви всіх 100 стейтів і міст перемоги (ru + en).
- Прапори RSK і RSB (усі ідеології, 3 розміри).
- map/buildings.txt рядок 3043: доки зсунуто вглиб суші.

НАЗВИ СТЕЙТІВ
Назви підібрані автоматично за координатами міста перемоги кожного стейта (карта у масштабі реальної
Югославії). Список: tools/state_names.csv. Якщо назва неправильна: поправ у CSV і запусти
   python tools/build_state_names.py
Рядки з відстанню > 0.15 у останній колонці варто перевірити першими. Сараєво, Подгориця
і Нові-Сад окремих стейтів з власним VP не мають (їх міста входять до сусідніх стейтів).
Файли лежать у localisation/replace/. Якщо в грі лишилися старі назви (Вюртемберг) — перемісти обидва
.yml з localisation/replace/ у localisation/russian/ і localisation/english/ відповідно.

НЕ ВИПРАВЛЯВ СВІДОМО
- sp:sp_* та Unknown modifier sp_*: ванільні технології посилаються на спецпроєкти, а
  common/special_projects/projects у моді замінений порожнім. Нешкідливо. Якщо хочеш прибрати —
  видали replace_path="common/special_projects/projects" з descriptor.mod і перевір лог.
- "X is not in the tag list": шум від ванільних файлів, зникне після кроку 2.
- Could not find music named maintheme; occupation law warning; ugc_*.mod supported_version.
- Помилки "Failed to create 2D texture (height=0)": перевір після нових прапорів, можливо зникнуть.
