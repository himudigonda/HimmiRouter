BEGIN;

-- ============================================================
-- PRICING CORRECTIONS (verified Feb 2026)
-- ============================================================

-- GPT-5.3 Codex: search shows $1.75/$14.00 (same base as 5.2), not $3/$15
UPDATE modelprovidermapping
SET input_token_cost = 1.75, output_token_cost = 14.00
WHERE model_id = (SELECT id FROM model WHERE slug = 'gpt-5.3-codex');

-- Gemini 3 Flash: actual is $0.50/$3.00, not $0.10/$0.40
UPDATE modelprovidermapping
SET input_token_cost = 0.50, output_token_cost = 3.00
WHERE model_id = (SELECT id FROM model WHERE slug = 'gemini-3-flash');

-- Grok 4.1 Fast: actual is $0.20/$0.50, not $3/$15
UPDATE modelprovidermapping
SET input_token_cost = 0.20, output_token_cost = 0.50
WHERE model_id = (SELECT id FROM model WHERE slug = 'grok-4.1');

-- Sonar Deep Research: actual is $2/$8, not $5/$25
UPDATE modelprovidermapping
SET input_token_cost = 2.00, output_token_cost = 8.00
WHERE model_id = (SELECT id FROM model WHERE slug = 'sonar-deep-research');

-- ============================================================
-- ADD Ollama as a company and provider (local, $0 cost)
-- ============================================================
INSERT INTO company (name, website) VALUES ('Ollama (Local)', 'https://ollama.com') ON CONFLICT DO NOTHING;
INSERT INTO provider (name, website) VALUES ('Ollama', 'https://ollama.com') ON CONFLICT DO NOTHING;

-- ============================================================
-- ADD Ollama models (local = $0.00 cost)
-- Slugs use the ollama/ prefix that LiteLLM expects
-- ============================================================
INSERT INTO model (name, slug, company_id) VALUES
    ('Llama 4 8B (Local)',         'ollama/llama4:8b',              (SELECT id FROM company WHERE name='Ollama (Local)')),
    ('Llama 4 Scout (Local)',      'ollama/llama4-scout',           (SELECT id FROM company WHERE name='Ollama (Local)')),
    ('DeepSeek V3.2 (Local)',      'ollama/deepseek-v3.2',          (SELECT id FROM company WHERE name='Ollama (Local)')),
    ('DeepSeek R1 70B (Local)',    'ollama/deepseek-r1:70b',        (SELECT id FROM company WHERE name='Ollama (Local)')),
    ('Qwen3 30B (Local)',          'ollama/qwen3:30b',              (SELECT id FROM company WHERE name='Ollama (Local)')),
    ('Qwen3 Coder 30B (Local)',    'ollama/qwen3-coder:30b',        (SELECT id FROM company WHERE name='Ollama (Local)')),
    ('Mistral Large 3 (Local)',    'ollama/mistral-large3',         (SELECT id FROM company WHERE name='Ollama (Local)')),
    ('Gemma 3 27B (Local)',        'ollama/gemma3:27b',             (SELECT id FROM company WHERE name='Ollama (Local)'));

-- ============================================================
-- ADD provider mappings for Ollama models ($0.00 — local compute)
-- ============================================================
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost) VALUES
    ((SELECT id FROM model WHERE slug='ollama/llama4:8b'),           (SELECT id FROM provider WHERE name='Ollama'), 0.00, 0.00),
    ((SELECT id FROM model WHERE slug='ollama/llama4-scout'),        (SELECT id FROM provider WHERE name='Ollama'), 0.00, 0.00),
    ((SELECT id FROM model WHERE slug='ollama/deepseek-v3.2'),       (SELECT id FROM provider WHERE name='Ollama'), 0.00, 0.00),
    ((SELECT id FROM model WHERE slug='ollama/deepseek-r1:70b'),     (SELECT id FROM provider WHERE name='Ollama'), 0.00, 0.00),
    ((SELECT id FROM model WHERE slug='ollama/qwen3:30b'),           (SELECT id FROM provider WHERE name='Ollama'), 0.00, 0.00),
    ((SELECT id FROM model WHERE slug='ollama/qwen3-coder:30b'),     (SELECT id FROM provider WHERE name='Ollama'), 0.00, 0.00),
    ((SELECT id FROM model WHERE slug='ollama/mistral-large3'),      (SELECT id FROM provider WHERE name='Ollama'), 0.00, 0.00),
    ((SELECT id FROM model WHERE slug='ollama/gemma3:27b'),          (SELECT id FROM provider WHERE name='Ollama'), 0.00, 0.00);

COMMIT;
