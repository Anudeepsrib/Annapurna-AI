# Sample Meal Plans

These examples show how Annapurna-AI should behave for local-first Andhra Telugu
planning. They are general wellness examples, not medical diets.

## Sample 1: Pantry-first family week

Family profile:

- Adult cook: regular appetite, prefers rice lunch.
- Senior: light appetite, prefers softer dinner.
- Child: light appetite, mild spice.

Pantry:

- rice - 5 kg
- moong dal - 1 kg
- spinach - 1 bunch - use within 2 days
- tamarind - small box

Constraints:

- vegetarian
- no egg
- Andhra Telugu style
- rice-based lunch
- daily pappu or dal
- mild for children

| Day | Breakfast | Lunch | Dinner | Pantry optimization |
| --- | --- | --- | --- | --- |
| Monday | Pesarattu with ginger chutney | Tomato pappu with rice | Phulka with bendakaya fry | Use rice and moong dal first |
| Tuesday | Idli with sambar | Gutti vankaya with rice | Vegetable pulao | Buy brinjal and mixed vegetables |
| Wednesday | Vegetable upma | Dosakaya pappu with rice | Tomato rice with curd | Use tamarind in pappu |
| Thursday | Dosa with coconut chutney | Sambar rice | Cabbage poriyal with rotis | Buy cabbage and coconut |
| Friday | Pongal | Palakura pappu with rice | Lemon rice with sundal | Use spinach within 2 days |
| Saturday | Uttapam | Vegetable kurma with rice | Millet khichdi | Buy millet if not in pantry |
| Sunday | Ragi dosa | Mamidikaya pappu with rice | Curd rice with tempered vegetables | Buy ragi flour and raw mango |

## Sample 2: Festival week, no onion or garlic

Family profile:

- Adult cook: regular appetite.
- Child: light appetite, mild spice.

Pantry:

- sona masoori rice - 3 kg
- toor dal - 750 g
- curry leaves - small bunch - use within 3 days
- jaggery - small packet

Constraints:

- vegetarian
- no egg
- Andhra Telugu style
- rice-based lunch
- daily pappu or dal
- festival no onion/garlic

| Day | Breakfast | Lunch | Dinner | Rule note |
| --- | --- | --- | --- | --- |
| Monday | Idli with coconut chutney | Tomato pappu rice | Lemon rice with chana sundal | No onion/garlic |
| Tuesday | Pesarattu with ginger chutney | Mamidikaya pappu rice | Curd rice with carrot tempering | No onion/garlic |
| Wednesday | Ven pongal | Sambar rice | Ragi dosa with chutney | No onion/garlic |
| Thursday | Dosa with peanut-free chutney | Palakura pappu rice | Vegetable khichdi | No onion/garlic |
| Friday | Upma with curry leaves | Dosakaya pappu rice | Tamarind rice with curd | No onion/garlic |
| Saturday | Uttapam without onion | Bendakaya pappu rice | Millet pongal | No onion/garlic |
| Sunday | Ragi dosa | Plain dal rice with vegetable fry | Curd rice | No onion/garlic |

The backend rule tests reject generated plans that include egg, meat, onion, or
garlic when those constraints are active.
