-- =============================================================================
-- FULL MODEL CATALOG — February 2026
-- Prices: USD per 1M tokens (input / output)
-- Providers: OpenAI, Anthropic, Google AI, Groq, Mistral, DeepSeek,
--            xAI, Perplexity, Amazon Bedrock, Ollama (local)
-- NOTE: "Groq" (inference platform) ≠ "Grok" (xAI chatbot)
-- =============================================================================
BEGIN;

-- ─────────────────────────────────────────────────────────────────────────────
-- 0. COMPANIES
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO company (name, website) SELECT 'OpenAI',         'https://openai.com'         WHERE NOT EXISTS (SELECT 1 FROM company WHERE name='OpenAI');
INSERT INTO company (name, website) SELECT 'Anthropic',      'https://anthropic.com'      WHERE NOT EXISTS (SELECT 1 FROM company WHERE name='Anthropic');
INSERT INTO company (name, website) SELECT 'Google',         'https://google.com'         WHERE NOT EXISTS (SELECT 1 FROM company WHERE name='Google');
INSERT INTO company (name, website) SELECT 'Meta',           'https://meta.ai'            WHERE NOT EXISTS (SELECT 1 FROM company WHERE name='Meta');
INSERT INTO company (name, website) SELECT 'Mistral AI',     'https://mistral.ai'         WHERE NOT EXISTS (SELECT 1 FROM company WHERE name='Mistral AI');
INSERT INTO company (name, website) SELECT 'DeepSeek',       'https://deepseek.com'       WHERE NOT EXISTS (SELECT 1 FROM company WHERE name='DeepSeek');
INSERT INTO company (name, website) SELECT 'xAI',            'https://x.ai'               WHERE NOT EXISTS (SELECT 1 FROM company WHERE name='xAI');
INSERT INTO company (name, website) SELECT 'Perplexity',     'https://perplexity.ai'      WHERE NOT EXISTS (SELECT 1 FROM company WHERE name='Perplexity');
INSERT INTO company (name, website) SELECT 'Groq',           'https://groq.com'           WHERE NOT EXISTS (SELECT 1 FROM company WHERE name='Groq');
INSERT INTO company (name, website) SELECT 'Alibaba',        'https://qwen.aliyun.com'    WHERE NOT EXISTS (SELECT 1 FROM company WHERE name='Alibaba');
INSERT INTO company (name, website) SELECT 'Amazon',         'https://aws.amazon.com'     WHERE NOT EXISTS (SELECT 1 FROM company WHERE name='Amazon');
INSERT INTO company (name, website) SELECT 'Cohere',         'https://cohere.com'         WHERE NOT EXISTS (SELECT 1 FROM company WHERE name='Cohere');
INSERT INTO company (name, website) SELECT 'Microsoft',      'https://microsoft.com'      WHERE NOT EXISTS (SELECT 1 FROM company WHERE name='Microsoft');
INSERT INTO company (name, website) SELECT 'Ollama (Local)', 'https://ollama.com'         WHERE NOT EXISTS (SELECT 1 FROM company WHERE name='Ollama (Local)');

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. PROVIDERS
-- ─────────────────────────────────────────────────────────────────────────────
INSERT INTO provider (name, website) SELECT 'OpenAI',          'https://api.openai.com'           WHERE NOT EXISTS (SELECT 1 FROM provider WHERE name='OpenAI');
INSERT INTO provider (name, website) SELECT 'Anthropic',       'https://api.anthropic.com'        WHERE NOT EXISTS (SELECT 1 FROM provider WHERE name='Anthropic');
INSERT INTO provider (name, website) SELECT 'Google AI',       'https://ai.google.dev'            WHERE NOT EXISTS (SELECT 1 FROM provider WHERE name='Google AI');
INSERT INTO provider (name, website) SELECT 'Groq',            'https://console.groq.com'         WHERE NOT EXISTS (SELECT 1 FROM provider WHERE name='Groq');
INSERT INTO provider (name, website) SELECT 'Mistral',         'https://console.mistral.ai'       WHERE NOT EXISTS (SELECT 1 FROM provider WHERE name='Mistral');
INSERT INTO provider (name, website) SELECT 'DeepSeek',        'https://platform.deepseek.com'    WHERE NOT EXISTS (SELECT 1 FROM provider WHERE name='DeepSeek');
INSERT INTO provider (name, website) SELECT 'xAI',             'https://x.ai/api'                 WHERE NOT EXISTS (SELECT 1 FROM provider WHERE name='xAI');
INSERT INTO provider (name, website) SELECT 'Perplexity',      'https://docs.perplexity.ai'       WHERE NOT EXISTS (SELECT 1 FROM provider WHERE name='Perplexity');
INSERT INTO provider (name, website) SELECT 'Amazon Bedrock',  'https://aws.amazon.com/bedrock'   WHERE NOT EXISTS (SELECT 1 FROM provider WHERE name='Amazon Bedrock');
INSERT INTO provider (name, website) SELECT 'Ollama',          'https://ollama.com'               WHERE NOT EXISTS (SELECT 1 FROM provider WHERE name='Ollama');

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. MODELS
-- ─────────────────────────────────────────────────────────────────────────────

-- ── OPENAI ───────────────────────────────────────────────────────────────────
INSERT INTO model (name, slug, company_id) SELECT 'GPT-5.2',         'gpt-5.2',         id FROM company WHERE name='OpenAI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'GPT-5.2 Pro',     'gpt-5.2-pro',     id FROM company WHERE name='OpenAI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'GPT-5.1',         'gpt-5.1',         id FROM company WHERE name='OpenAI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'GPT-5 Mini',      'gpt-5-mini',      id FROM company WHERE name='OpenAI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'GPT-5 Nano',      'gpt-5-nano',      id FROM company WHERE name='OpenAI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'GPT-5.3 Codex',   'gpt-5.3-codex',   id FROM company WHERE name='OpenAI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'GPT-5.2 Codex',   'gpt-5.2-codex',   id FROM company WHERE name='OpenAI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'GPT-5.1 Codex',   'gpt-5.1-codex',   id FROM company WHERE name='OpenAI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'o3',              'o3',              id FROM company WHERE name='OpenAI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'o3 Pro',          'o3-pro',          id FROM company WHERE name='OpenAI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'o3 Mini',         'o3-mini',         id FROM company WHERE name='OpenAI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'o4 Mini',         'o4-mini',         id FROM company WHERE name='OpenAI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'GPT-4.1',         'gpt-4.1',         id FROM company WHERE name='OpenAI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'GPT-4.1 Mini',    'gpt-4.1-mini',    id FROM company WHERE name='OpenAI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'GPT-4.1 Nano',    'gpt-4.1-nano',    id FROM company WHERE name='OpenAI' ON CONFLICT (slug) DO NOTHING;

-- ── ANTHROPIC ────────────────────────────────────────────────────────────────
INSERT INTO model (name, slug, company_id) SELECT 'Claude 4.6 Opus',   'claude-4-6-opus',   id FROM company WHERE name='Anthropic' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Claude 4.6 Sonnet', 'claude-4-6-sonnet', id FROM company WHERE name='Anthropic' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Claude Haiku 4.5',  'claude-haiku-4.5',  id FROM company WHERE name='Anthropic' ON CONFLICT (slug) DO NOTHING;

-- ── GOOGLE — Gemini 2.5 (stable) + Gemini 3 (preview) ───────────────────────
-- Gemini 3 is still in preview as of Feb 2026
INSERT INTO model (name, slug, company_id) SELECT 'Gemini 3 Pro (Preview)',   'gemini-3-pro-preview',   id FROM company WHERE name='Google' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Gemini 3 Flash (Preview)', 'gemini-3-flash-preview', id FROM company WHERE name='Google' ON CONFLICT (slug) DO NOTHING;
-- Gemini 2.5 (stable, GA)
INSERT INTO model (name, slug, company_id) SELECT 'Gemini 2.5 Pro',         'gemini-2.5-pro',         id FROM company WHERE name='Google' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Gemini 2.5 Flash',       'gemini-2.5-flash',       id FROM company WHERE name='Google' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Gemini 2.5 Flash-Lite',  'gemini-2.5-flash-lite',  id FROM company WHERE name='Google' ON CONFLICT (slug) DO NOTHING;
-- Remove incorrect old slugs
DELETE FROM modelprovidermapping WHERE model_id IN (SELECT id FROM model WHERE slug IN ('gemini-3-pro','gemini-3-flash'));
DELETE FROM model WHERE slug IN ('gemini-3-pro','gemini-3-flash');

-- ── META via GROQ (inference platform) ───────────────────────────────────────
INSERT INTO model (name, slug, company_id) SELECT 'Llama 4 Maverick', 'llama-4-maverick-instruct', id FROM company WHERE name='Meta' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Llama 4 Scout',    'llama-4-scout-instruct',    id FROM company WHERE name='Meta' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Llama 3.3 70B',    'llama-3.3-70b-versatile',   id FROM company WHERE name='Meta' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Llama 3.1 8B',     'llama-3.1-8b-instant',      id FROM company WHERE name='Meta' ON CONFLICT (slug) DO NOTHING;

-- ── ALIBABA QWEN via GROQ ─────────────────────────────────────────────────────
INSERT INTO model (name, slug, company_id) SELECT 'Qwen3 32B', 'qwen3-32b', id FROM company WHERE name='Alibaba' ON CONFLICT (slug) DO NOTHING;

-- ── DEEPSEEK ─────────────────────────────────────────────────────────────────
INSERT INTO model (name, slug, company_id) SELECT 'DeepSeek V4',   'deepseek-v4',   id FROM company WHERE name='DeepSeek' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'DeepSeek V3.2', 'deepseek-v3.2', id FROM company WHERE name='DeepSeek' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'DeepSeek R1',   'deepseek-r1',   id FROM company WHERE name='DeepSeek' ON CONFLICT (slug) DO NOTHING;

-- ── MISTRAL AI ───────────────────────────────────────────────────────────────
INSERT INTO model (name, slug, company_id) SELECT 'Mistral Large 3',   'mistral-large-3',   id FROM company WHERE name='Mistral AI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Mistral Medium 3',  'mistral-medium-3',  id FROM company WHERE name='Mistral AI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Mistral Small 3.2', 'mistral-small-3.2', id FROM company WHERE name='Mistral AI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Mistral Nemo',      'mistral-nemo',      id FROM company WHERE name='Mistral AI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Codestral 2',       'codestral-2',       id FROM company WHERE name='Mistral AI' ON CONFLICT (slug) DO NOTHING;

-- ── xAI (Grok) ───────────────────────────────────────────────────────────────
INSERT INTO model (name, slug, company_id) SELECT 'Grok 3',           'grok-3',           id FROM company WHERE name='xAI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Grok 3 Mini',      'grok-3-mini',      id FROM company WHERE name='xAI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Grok 4',           'grok-4',           id FROM company WHERE name='xAI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Grok 4.1',         'grok-4.1',         id FROM company WHERE name='xAI' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Grok Code Fast 1', 'grok-code-fast-1', id FROM company WHERE name='xAI' ON CONFLICT (slug) DO NOTHING;

-- ── PERPLEXITY ───────────────────────────────────────────────────────────────
INSERT INTO model (name, slug, company_id) SELECT 'Sonar',               'sonar',               id FROM company WHERE name='Perplexity' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Sonar Pro',           'sonar-pro',           id FROM company WHERE name='Perplexity' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Sonar Reasoning',     'sonar-reasoning',     id FROM company WHERE name='Perplexity' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Sonar Reasoning Pro', 'sonar-reasoning-pro', id FROM company WHERE name='Perplexity' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Sonar Deep Research', 'sonar-deep-research', id FROM company WHERE name='Perplexity' ON CONFLICT (slug) DO NOTHING;

-- ── AMAZON BEDROCK ───────────────────────────────────────────────────────────
-- Amazon Nova (Amazon's own models)
INSERT INTO model (name, slug, company_id) SELECT 'Nova Pro',   'amazon.nova-pro-v1:0',   id FROM company WHERE name='Amazon' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Nova Lite',  'amazon.nova-lite-v1:0',  id FROM company WHERE name='Amazon' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Nova Micro', 'amazon.nova-micro-v1:0', id FROM company WHERE name='Amazon' ON CONFLICT (slug) DO NOTHING;
-- Anthropic on Bedrock
INSERT INTO model (name, slug, company_id) SELECT 'Claude 4.6 Sonnet (Bedrock)', 'anthropic.claude-sonnet-4-6-20260217-v1:0', id FROM company WHERE name='Anthropic' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Claude 3.7 Sonnet (Bedrock)', 'anthropic.claude-3-7-sonnet-20250219-v1:0', id FROM company WHERE name='Anthropic' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Claude 3.5 Haiku (Bedrock)',  'anthropic.claude-3-5-haiku-20241022-v1:0',  id FROM company WHERE name='Anthropic' ON CONFLICT (slug) DO NOTHING;
-- Meta Llama on Bedrock
INSERT INTO model (name, slug, company_id) SELECT 'Llama 3.3 70B (Bedrock)', 'meta.llama3-3-70b-instruct-v1:0', id FROM company WHERE name='Meta' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Llama 3.2 90B (Bedrock)', 'meta.llama3-2-90b-instruct-v1:0', id FROM company WHERE name='Meta' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Llama 3.1 70B (Bedrock)', 'meta.llama3-1-70b-instruct-v1:0', id FROM company WHERE name='Meta' ON CONFLICT (slug) DO NOTHING;
-- Mistral on Bedrock
INSERT INTO model (name, slug, company_id) SELECT 'Mistral Large 3 (Bedrock)', 'mistral.mistral-large-3-2512-v1:0', id FROM company WHERE name='Mistral AI' ON CONFLICT (slug) DO NOTHING;
-- DeepSeek on Bedrock
INSERT INTO model (name, slug, company_id) SELECT 'DeepSeek V3.2 (Bedrock)', 'deepseek.deepseek-v3-2-20250514-v1:0', id FROM company WHERE name='DeepSeek' ON CONFLICT (slug) DO NOTHING;
-- Cohere on Bedrock
INSERT INTO model (name, slug, company_id) SELECT 'Command R+',  'cohere.command-r-plus-v1:0', id FROM company WHERE name='Cohere' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Command R',   'cohere.command-r-v1:0',      id FROM company WHERE name='Cohere' ON CONFLICT (slug) DO NOTHING;

-- ── OLLAMA (LOCAL) ────────────────────────────────────────────────────────────
INSERT INTO model (name, slug, company_id) SELECT 'Llama 4 8B (Local)',         'ollama/llama4:8b',            id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Llama 4 Scout (Local)',      'ollama/llama4-scout',         id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Llama 3.3 70B (Local)',      'ollama/llama3.3:70b',         id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Llama 3.2 3B (Local)',       'ollama/llama3.2:3b',          id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Llama 3.1 8B (Local)',       'ollama/llama3.1:8b',          id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'DeepSeek V3.2 (Local)',      'ollama/deepseek-v3.2',        id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'DeepSeek R1 70B (Local)',    'ollama/deepseek-r1:70b',      id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'DeepSeek R1 32B (Local)',    'ollama/deepseek-r1:32b',      id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'DeepSeek R1 14B (Local)',    'ollama/deepseek-r1:14b',      id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'DeepSeek R1 8B (Local)',     'ollama/deepseek-r1:8b',       id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Qwen3 235B A22B (Local)',    'ollama/qwen3:235b-a22b',      id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Qwen3 32B (Local)',          'ollama/qwen3:32b',            id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Qwen3 30B (Local)',          'ollama/qwen3:30b',            id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Qwen3 14B (Local)',          'ollama/qwen3:14b',            id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Qwen3 8B (Local)',           'ollama/qwen3:8b',             id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Qwen3 Coder 30B (Local)',    'ollama/qwen3-coder:30b',      id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Qwen2.5 72B (Local)',        'ollama/qwen2.5:72b',          id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Qwen2.5 Coder 32B (Local)', 'ollama/qwen2.5-coder:32b',    id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Mistral Large 3 (Local)',    'ollama/mistral-large3',       id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Mistral Nemo (Local)',       'ollama/mistral-nemo',         id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Gemma 3 27B (Local)',        'ollama/gemma3:27b',           id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Gemma 3 12B (Local)',        'ollama/gemma3:12b',           id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Gemma 3 4B (Local)',         'ollama/gemma3:4b',            id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Phi-4 14B (Local)',          'ollama/phi4:14b',             id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;
INSERT INTO model (name, slug, company_id) SELECT 'Phi-4 Mini (Local)',         'ollama/phi4-mini',            id FROM company WHERE name='Ollama (Local)' ON CONFLICT (slug) DO NOTHING;

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. PROVIDER MAPPINGS
-- ─────────────────────────────────────────────────────────────────────────────

-- ── OpenAI ───────────────────────────────────────────────────────────────────
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost)
SELECT m.id, p.id, v.inp, v.out
FROM (VALUES
  ('gpt-5.2',        1.75::float8,  14.00::float8),
  ('gpt-5.2-pro',   21.00,         168.00),
  ('gpt-5.1',        1.75,          14.00),
  ('gpt-5-mini',     0.25,           2.00),
  ('gpt-5-nano',     0.05,           0.40),
  ('gpt-5.3-codex',  1.75,          14.00),
  ('gpt-5.2-codex',  1.75,          14.00),
  ('gpt-5.1-codex',  1.75,          14.00),
  ('o3',             2.00,           8.00),
  ('o3-pro',        20.00,          80.00),
  ('o3-mini',        1.10,           4.40),
  ('o4-mini',        1.10,           4.40),
  ('gpt-4.1',        3.00,          12.00),
  ('gpt-4.1-mini',   0.80,           3.20),
  ('gpt-4.1-nano',   0.20,           0.80)
) AS v(slug, inp, out)
JOIN model m ON m.slug = v.slug
JOIN provider p ON p.name = 'OpenAI'
WHERE NOT EXISTS (SELECT 1 FROM modelprovidermapping WHERE model_id=m.id AND provider_id=p.id);

-- ── Anthropic (direct) ───────────────────────────────────────────────────────
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost)
SELECT m.id, p.id, v.inp, v.out
FROM (VALUES
  ('claude-4-6-opus',   5.00::float8, 25.00::float8),
  ('claude-4-6-sonnet', 3.00,         15.00),
  ('claude-haiku-4.5',  0.80,          4.00)
) AS v(slug, inp, out)
JOIN model m ON m.slug = v.slug
JOIN provider p ON p.name = 'Anthropic'
WHERE NOT EXISTS (SELECT 1 FROM modelprovidermapping WHERE model_id=m.id AND provider_id=p.id);

-- ── Google AI ────────────────────────────────────────────────────────────────
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost)
SELECT m.id, p.id, v.inp, v.out
FROM (VALUES
  ('gemini-3-pro-preview',   2.00::float8, 12.00::float8),
  ('gemini-3-flash-preview', 0.50,          3.00),
  ('gemini-2.5-pro',         1.25,         10.00),
  ('gemini-2.5-flash',       0.30,          2.50),
  ('gemini-2.5-flash-lite',  0.10,          0.40)
) AS v(slug, inp, out)
JOIN model m ON m.slug = v.slug
JOIN provider p ON p.name = 'Google AI'
WHERE NOT EXISTS (SELECT 1 FROM modelprovidermapping WHERE model_id=m.id AND provider_id=p.id);

-- ── Groq (inference platform) — Meta Llama + Qwen ────────────────────────────
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost)
SELECT m.id, p.id, v.inp, v.out
FROM (VALUES
  ('llama-4-maverick-instruct', 0.50::float8, 0.77::float8),
  ('llama-4-scout-instruct',    0.11,          0.34),
  ('llama-3.3-70b-versatile',   0.59,          0.79),
  ('llama-3.1-8b-instant',      0.05,          0.08),
  ('qwen3-32b',                 0.29,          0.59)
) AS v(slug, inp, out)
JOIN model m ON m.slug = v.slug
JOIN provider p ON p.name = 'Groq'
WHERE NOT EXISTS (SELECT 1 FROM modelprovidermapping WHERE model_id=m.id AND provider_id=p.id);

-- ── DeepSeek ─────────────────────────────────────────────────────────────────
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost)
SELECT m.id, p.id, v.inp, v.out
FROM (VALUES
  ('deepseek-v4',   0.27::float8, 1.10::float8),
  ('deepseek-v3.2', 0.27,         1.10),
  ('deepseek-r1',   0.55,         2.19)
) AS v(slug, inp, out)
JOIN model m ON m.slug = v.slug
JOIN provider p ON p.name = 'DeepSeek'
WHERE NOT EXISTS (SELECT 1 FROM modelprovidermapping WHERE model_id=m.id AND provider_id=p.id);

-- ── Mistral ───────────────────────────────────────────────────────────────────
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost)
SELECT m.id, p.id, v.inp, v.out
FROM (VALUES
  ('mistral-large-3',   0.50::float8, 1.50::float8),
  ('mistral-medium-3',  0.40,         2.00),
  ('mistral-small-3.2', 0.10,         0.30),
  ('mistral-nemo',      0.30,         0.30),
  ('codestral-2',       0.30,         0.90)
) AS v(slug, inp, out)
JOIN model m ON m.slug = v.slug
JOIN provider p ON p.name = 'Mistral'
WHERE NOT EXISTS (SELECT 1 FROM modelprovidermapping WHERE model_id=m.id AND provider_id=p.id);

-- ── xAI (Grok) ───────────────────────────────────────────────────────────────
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost)
SELECT m.id, p.id, v.inp, v.out
FROM (VALUES
  ('grok-3',           3.00::float8, 15.00::float8),
  ('grok-3-mini',      0.30,          0.50),
  ('grok-4',           3.00,         15.00),
  ('grok-4.1',         0.20,          0.50),
  ('grok-code-fast-1', 0.20,          1.50)
) AS v(slug, inp, out)
JOIN model m ON m.slug = v.slug
JOIN provider p ON p.name = 'xAI'
WHERE NOT EXISTS (SELECT 1 FROM modelprovidermapping WHERE model_id=m.id AND provider_id=p.id);

-- ── Perplexity ────────────────────────────────────────────────────────────────
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost)
SELECT m.id, p.id, v.inp, v.out
FROM (VALUES
  ('sonar',               1.00::float8,  1.00::float8),
  ('sonar-pro',           3.00,         15.00),
  ('sonar-reasoning',     1.00,          5.00),
  ('sonar-reasoning-pro', 2.00,          8.00),
  ('sonar-deep-research', 2.00,          8.00)
) AS v(slug, inp, out)
JOIN model m ON m.slug = v.slug
JOIN provider p ON p.name = 'Perplexity'
WHERE NOT EXISTS (SELECT 1 FROM modelprovidermapping WHERE model_id=m.id AND provider_id=p.id);

-- ── Amazon Bedrock ────────────────────────────────────────────────────────────
-- Pricing: Bedrock on-demand rates (us-east-1), per 1M tokens
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost)
SELECT m.id, p.id, v.inp, v.out
FROM (VALUES
  ('amazon.nova-pro-v1:0',                         0.80::float8,  3.20::float8),
  ('amazon.nova-lite-v1:0',                        0.06,          0.24),
  ('amazon.nova-micro-v1:0',                       0.035,         0.14),
  ('anthropic.claude-sonnet-4-6-20260217-v1:0',    3.00,         15.00),
  ('anthropic.claude-3-7-sonnet-20250219-v1:0',    3.00,         15.00),
  ('anthropic.claude-3-5-haiku-20241022-v1:0',     0.80,          4.00),
  ('meta.llama3-3-70b-instruct-v1:0',              0.72,          0.72),
  ('meta.llama3-2-90b-instruct-v1:0',              0.72,          0.72),
  ('meta.llama3-1-70b-instruct-v1:0',              0.72,          0.72),
  ('mistral.mistral-large-3-2512-v1:0',            2.00,          6.00),
  ('deepseek.deepseek-v3-2-20250514-v1:0',         0.62,          1.85),
  ('cohere.command-r-plus-v1:0',                   3.00,         15.00),
  ('cohere.command-r-v1:0',                        0.50,          1.50)
) AS v(slug, inp, out)
JOIN model m ON m.slug = v.slug
JOIN provider p ON p.name = 'Amazon Bedrock'
WHERE NOT EXISTS (SELECT 1 FROM modelprovidermapping WHERE model_id=m.id AND provider_id=p.id);

-- ── Ollama (local, $0) ────────────────────────────────────────────────────────
INSERT INTO modelprovidermapping (model_id, provider_id, input_token_cost, output_token_cost)
SELECT m.id, p.id, 0.00, 0.00
FROM model m
JOIN provider p ON p.name = 'Ollama'
WHERE m.slug LIKE 'ollama/%'
  AND NOT EXISTS (SELECT 1 FROM modelprovidermapping WHERE model_id=m.id AND provider_id=p.id);

COMMIT;

-- ─────────────────────────────────────────────────────────────────────────────
-- VERIFICATION
-- ─────────────────────────────────────────────────────────────────────────────
SELECT c.name AS company, COUNT(*) AS models
FROM model m JOIN company c ON m.company_id = c.id
GROUP BY c.name ORDER BY c.name;

SELECT COUNT(*) AS total_models FROM model;
SELECT COUNT(*) AS total_mappings FROM modelprovidermapping;
