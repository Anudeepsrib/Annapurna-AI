# Annapurna-AI Product Reframe

Annapurna-AI is framed as a local-first, culturally aware planning app for
Andhra Telugu home cooking. The product value is not "AI recipes"; it is private
weekly planning that combines family roles, pantry stock, Telugu household rules,
and grocery optimization.

## Privacy-by-design family model

The family profile intentionally avoids high-risk personal data.

| Field | Product purpose | Privacy design |
| --- | --- | --- |
| Role label | Distinguish household needs | Use "Adult cook", "Senior", or "Child" instead of legal names |
| Age group | Tune appetite and spice assumptions | Use broad bands, not exact age or date of birth |
| Appetite | Adjust meal planning language | Use light, regular, or hearty instead of weight or calorie targets |
| Dietary tags | Capture cooking needs | Use simple tags such as mild spice or prefers curd rice |
| Privacy scope | Explain handling | Default is local device only |

Do not collect exact ages, weights, diagnoses, prescriptions, or medical history
for meal generation. If a user mentions a medical condition, the backend returns
general wellness guardrails and recommends qualified professional review.

## Pantry inventory and grocery optimization

Users can enter pantry items with optional quantity and expiry context:

```text
rice - 5 kg
moong dal - 1 kg
spinach - 1 bunch - use within 2 days
tamarind - small box
```

The backend classifies generated grocery items into:

- `Use From Pantry First`: recipe ingredients already present in the pantry.
- `Buy / Replenish`: ingredients used by the plan that are not in the pantry.
- `Pantry Items To Use Soon`: pantry items expiring soon but not used by the plan.

The optimizer preserves recipe units instead of inventing exact purchase
quantities. It explains repeat usage and priority so the grocery list is useful
without pretending to know household consumption precisely.

## Telugu and Andhra dietary constraints

The app treats cultural food rules as validated planning constraints:

- vegetarian
- no egg
- Andhra Telugu style
- rice-based lunch
- daily pappu or dal anchor
- fermented breakfasts allowed
- mild spice for children
- festival no onion/garlic

Generated plans are schema-validated and rule-validated before saving. If a model
returns malformed JSON or violates these rules, Annapurna falls back to a
deterministic local Andhra-style plan.

## Local vs cloud model switching

Local mode is the default:

```env
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434
ENABLE_EXTERNAL_NETWORK=false
```

External mode is allowed only after an explicit opt-in:

```env
LLM_PROVIDER=custom
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=...
ENABLE_EXTERNAL_NETWORK=true
```

When the model endpoint is non-local, family roles, pantry inventory, allergies,
and dietary text may leave the machine as prompt data. The backend enforces this
boundary by rejecting a non-local `LLM_BASE_URL` unless
`ENABLE_EXTERNAL_NETWORK=true`.

## Wellness, not medical advice

Annapurna-AI provides general wellness meal-planning ideas only. It is not a
medical device, clinical nutrition system, diagnosis tool, or treatment planner.
Nutrition estimates are approximate. Users should consult a qualified clinician
or registered dietitian for medical conditions, pregnancy, pediatric diets,
eating disorders, allergies, medication interactions, or therapeutic nutrition.

## Short case study: private personalization

A household wants a vegetarian Andhra week plan for three people: an adult cook,
a senior, and a child. They enter role labels rather than names, choose broad
age groups, mark the child as mild spice, and add pantry items such as rice,
moong dal, spinach, and tamarind. They enable rice-based lunch and daily pappu
or dal.

Annapurna creates a weekly plan using those local signals, marks rice and moong
dal as pantry-first items, flags spinach to use soon, and lists only missing
ingredients for shopping. No account, analytics identifier, exact age, weight,
diagnosis, or cloud model call is required by default. Personalization comes
from minimized local context, not broad personal data collection.
