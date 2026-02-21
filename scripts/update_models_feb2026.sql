BEGIN;

-- ============================================================
-- STEP 1: DELETE old models (mappings first, then models)
-- ============================================================

-- OpenAI: delete gpt-4o, gpt-4o-mini, gpt-4.5-preview, gpt-5, o1-preview
DELETE FROM modelprovidermapping WHERE model_id IN (
    SELECT id FROM model WHERE slug IN ('gpt-4o','gpt-4o-mini','gpt-4.5-preview','gpt-5','o1-preview')
);
DELETE FROM model WHERE slug IN ('gpt-4o','gpt-4o-mini','gpt-4.5-preview','gpt-5','o1-preview');

-- Anthropic: delete claude-3.5, claude-3-opus, claude-3.7, claude-4.5-sonnet, claude-4.5-opus
DELETE FROM modelprovidermapping WHERE model_id IN (
    SELECT id FROM model WHERE slug IN (
        'claude-3-5-sonnet-20240620','claude-3-opus-20240229',
        'claude-3-7-sonnet','claude-4-5-sonnet','claude-4-5-opus'
    )
);
DELETE FROM model WHERE slug IN (
    'claude-3-5-sonnet-20240620','claude-3-opus-20240229',
    'claude-3-7-sonnet','claude-4-5-sonnet','claude-4-5-opus'
);

-- Google: delete gemini-1.5-pro, gemini-1.5-flash, gemini-2.5-pro
DELETE FROM modelprovidermapping WHERE model_id IN (
    SELECT id FROM model WHERE slug IN ('gemini-1.5-pro','gemini-1.5-flash','gemini-2.5-pro')
);
DELETE FROM model WHERE slug IN ('gemini-1.5-pro','gemini-1.5-flash','gemini-2.5-pro');

-- Groq: delete llama3-70b, llama3-8b, mixtral-8x7b
DELETE FROM modelprovidermapping WHERE model_id IN (
    SELECT id FROM model WHERE slug IN ('llama3-70b-8192','llama3-8b-8192','mixtral-8x7b-32768')
);
DELETE FROM model WHERE slug IN ('llama3-70b-8192','llama3-8b-8192','mixtral-8x7b-32768');

-- Mistral: delete mistral-large-2 and codestral
DELETE FROM modelprovidermapping WHERE model_id IN (
    SELECT id FROM model WHERE slug IN ('mistral-large-latest','codestral-latest')
);
DELETE FROM model WHERE slug IN ('mistral-large-latest','codestral-latest');

-- xAI: delete grok-3
DELETE FROM modelprovidermapping WHERE model_id IN (SELECT id FROM model WHERE slug = 'grok-3');
DELETE FROM model WHERE slug = 'grok-3';

-- Perplexity: delete old sonar
DELETE FROM modelprovidermapping WHERE model_id IN (SELECT id FROM model WHERE slug = 'llama-3-sonar-large-32k-online');
DELETE FROM model WHERE slug = 'llama-3-sonar-large-32k-online';

-- ============================================================
-- STEP 2: ADD new companies and providers (Meta, DeepSeek)
-- ============================================================
INSERT INTO company (name, website) VALUES ('Meta', 'https://meta.ai') ON CONFLICT DO NOTHING;
INSERT INTO company (name, website) VALUES ('DeepSeek', 'https://deepseek.com') ON CONFLICT DO NOTHING;
INSERT INTO provider (name, website) VALUES ('Meta', 'https://meta.ai') ON CONFLICT DO NOTHING;
INSERT INTO provider (name, website) VALUES ('DeepSeek', 'https://deepseek.com') ON CONFLICT DO NOTHING;

-- ============================================================
-- STEP 3: ADD new models
-- ============================================================

-- OpenAI
INSERT INTO model (name, slug, company_id) VALUES
    ('GPT-5.3 Codex', 'gpt-5.3-codex', (SELECT id FROM company WHERE name='OpenAI')),
    ('o4 Mini', 'o4-mini', (SELECT id FROM company WHERE name='OpenAI'));

-- Anthropic
INSERT INTO model (name, slug, company_id) VALUES
    ('Claude 4.6 Sonnet', 'claude-4-6-sonnet', (SELECT id FROM company WHERE name='Anthropic')),
    ('Claude Haiku 4.5', 'claude-haiku-4.5', (SELECT id FROM company WHERE name='Anthropic'));

-- Google
INSERT INTO model (name, slug, company_id) VALUES
    ('Gemini 3 Flash', 'gemini-3-flash', (SELECT id FROM company WHERE name='Google'));

-- Meta (Llama 4, served via Groq)
INSERT INTO model (name, slug, company_id) VALUES
    ('Llama 4 Maverick', 'llama-4-maverick-instruct', (SELECT id FROM company WHERE name='Meta')),
    ('Llama 4 Scout', 'llama-4-scout-instruct', (SELECT id FROM company WHERE name='Meta'));

-- DeepSeek
INSERT INTO model (name, slug, company_id) VALUES
    ('DeepSeek V4', 'deepseek-v4', (SELECT id FROM company WHERE name='DeepSeek'));

-- xAI
INSERT INTO model (name, slug, company_id) VALUES
    ('Grok 4.1', 'grok-4.1', (SELECT id FROM company WHERE name='xAI'));

-- Perplexity
INSERT INTO model (name, slug, company_id) VALUES
    ('Sonar Deep Research', 'sonar-deep-research', (SELECT id FROM company WHERE name='Perplexity'));

-- ============================================================
-- STEP 4: ADD provider mappings for new models
-- ============================================================

-- GPT-5.3 Codex
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost) VALUES
    ((SELECT id FROM model WHERE slug='gpt-5.3-codex'), (SELECT id FROM provider WHERE name='OpenAI'), 3.0, 15.0);

-- o4-mini
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost) VALUES
    ((SELECT id FROM model WHERE slug='o4-mini'), (SELECT id FROM provider WHERE name='OpenAI'), 1.1, 4.4);

-- Claude 4.6 Sonnet
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost) VALUES
    ((SELECT id FROM model WHERE slug='claude-4-6-sonnet'), (SELECT id FROM provider WHERE name='Anthropic'), 3.0, 15.0);

-- Claude Haiku 4.5
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost) VALUES
    ((SELECT id FROM model WHERE slug='claude-haiku-4.5'), (SELECT id FROM provider WHERE name='Anthropic'), 0.8, 4.0);

-- Gemini 3 Flash
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost) VALUES
    ((SELECT id FROM model WHERE slug='gemini-3-flash'), (SELECT id FROM provider WHERE name='Google AI'), 0.1, 0.4);

-- Llama 4 Maverick (via Groq)
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost) VALUES
    ((SELECT id FROM model WHERE slug='llama-4-maverick-instruct'), (SELECT id FROM provider WHERE name='Groq'), 0.5, 0.77);

-- Llama 4 Scout (via Groq)
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost) VALUES
    ((SELECT id FROM model WHERE slug='llama-4-scout-instruct'), (SELECT id FROM provider WHERE name='Groq'), 0.11, 0.34);

-- DeepSeek V4
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost) VALUES
    ((SELECT id FROM model WHERE slug='deepseek-v4'), (SELECT id FROM provider WHERE name='DeepSeek'), 0.27, 1.1);

-- Grok 4.1
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost) VALUES
    ((SELECT id FROM model WHERE slug='grok-4.1'), (SELECT id FROM provider WHERE name='xAI'), 3.0, 15.0);

-- Sonar Deep Research
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost) VALUES
    ((SELECT id FROM model WHERE slug='sonar-deep-research'), (SELECT id FROM provider WHERE name='Perplexity'), 5.0, 25.0);

COMMIT;
