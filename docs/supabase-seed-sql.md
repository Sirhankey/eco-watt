# Seed inicial do EcoWatt no Supabase

Execute a migration estrutural antes deste script. Depois, cole apenas o bloco SQL abaixo no SQL Editor do Supabase.

Este seed e idempotente: pode ser executado novamente sem duplicar registros. Ele carrega os dados oficiais dos quatro JSONs, todos os itens dos presets e um quiz inicial desabilitado. Dados pessoais nao sao criados com UUID ficticio.

```sql
begin;

insert into public.official_appliances (id, name, normalized_name, category, power_watts, default_hours_per_day, default_days_per_month, description, status, source) values
  ('shower', 'Chuveiro Elétrico', 'chuveiro eletrico', 'Banheiro', 5500, 0.5, 30, 'Um dos aparelhos com maior potência na residência. Poucos minutos fazem grande diferença.', 'published', 'migration'),
  ('air_conditioner', 'Ar-Condicionado 9.000 BTU', 'ar condicionado 9 000 btu', 'Climatização', 900, 8.0, 30, 'Uso prolongado ao longo da noite tem impacto relevante na fatura mensal.', 'published', 'migration'),
  ('fridge', 'Geladeira Frost Free', 'geladeira frost free', 'Cozinha', 150, 12.0, 30, 'Fica ligada 24 horas, mas o compressor opera intermitentemente (cerca de 10-12h diárias equivalentes).', 'published', 'migration'),
  ('led_tv', 'Smart TV 50''''', 'smart tv 50', 'Sala', 100, 5.0, 30, 'Consumo moderado, que varia conforme o brilho e volume.', 'published', 'migration'),
  ('microwave', 'Forno Micro-ondas', 'forno micro ondas', 'Cozinha', 1200, 0.3, 30, 'Alta potência, porém utilizado por poucos minutos durante o dia.', 'published', 'migration'),
  ('washing_machine', 'Máquina de Lavar Roupas', 'maquina de lavar roupas', 'Lavanderia', 500, 1.5, 12, 'Uso pontual em determinados dias da semana.', 'published', 'migration'),
  ('fan', 'Ventilador de Mesa', 'ventilador de mesa', 'Climatização', 80, 8.0, 30, 'Excelente alternativa econômica para ventilar o ambiente em dias quentes.', 'published', 'migration'),
  ('led_bulb_pack', 'Iluminação LED (Conjunto de 5 lâmpadas)', 'iluminacao led conjunto de 5 lampadas', 'Iluminação', 45, 5.0, 30, 'Lâmpadas LED são até 80% mais econômicas que as antigas incandescentes.', 'published', 'migration'),
  ('iron', 'Ferro de Passar Roupas', 'ferro de passar roupas', 'Lavanderia', 1500, 1.0, 8, 'Aquecimento resistivo de alta potência; passar roupas em lote economiza energia.', 'published', 'migration'),
  ('air_fryer', 'Fritadeira Sem Óleo (Air Fryer)', 'fritadeira sem oleo air fryer', 'Cozinha', 1500, 0.5, 20, 'Prática e rápida, consome bastante potência enquanto a resistência estiver acionada.', 'published', 'migration')
on conflict (id) do update set
  name = excluded.name,
  normalized_name = excluded.normalized_name,
  category = excluded.category,
  power_watts = excluded.power_watts,
  default_hours_per_day = excluded.default_hours_per_day,
  default_days_per_month = excluded.default_days_per_month,
  description = excluded.description,
  status = excluded.status,
  source = excluded.source;

insert into public.official_pc_components (id, name, normalized_name, category, tdp_watts, idle_watts, typical_load_watts, gaming_load_watts, description, status, source) values
  ('cpu_basic', 'Processador Básico / Entrada (ex: Core i3 / Ryzen 3)', 'processador basico entrada ex core i3 ryzen 3', 'CPU', 65, 15, 45, 55, null, 'published', 'migration'),
  ('cpu_mid', 'Processador Intermediário (ex: Ryzen 5 5600 / Core i5 13400)', 'processador intermediario ex ryzen 5 5600 core i5 13400', 'CPU', 65, 20, 55, 70, null, 'published', 'migration'),
  ('cpu_high', 'Processador Avançado / Entusiasta (ex: Ryzen 7 7800X3D / Core i7 14700K)', 'processador avancado entusiasta ex ryzen 7 7800x3d core i7 14700k', 'CPU', 125, 30, 90, 140, null, 'published', 'migration'),
  ('gpu_integrated', 'Vídeo Integrado (iGPU)', 'video integrado igpu', 'GPU', 0, 2, 10, 25, null, 'published', 'migration'),
  ('gpu_entry', 'GPU Dedicada de Entrada (ex: GTX 1650 / RX 6400)', 'gpu dedicada de entrada ex gtx 1650 rx 6400', 'GPU', 75, 8, 30, 70, null, 'published', 'migration'),
  ('gpu_mid', 'GPU Intermediária Gamer (ex: RTX 4060 / RX 6700)', 'gpu intermediaria gamer ex rtx 4060 rx 6700', 'GPU', 160, 12, 45, 140, null, 'published', 'migration'),
  ('gpu_high', 'GPU Alta Performance (ex: RTX 4080 / RX 7900 XTX)', 'gpu alta performance ex rtx 4080 rx 7900 xtx', 'GPU', 320, 20, 70, 290, null, 'published', 'migration'),
  ('mb_standard', 'Placa-Mãe Padrão mATX / ATX', 'placa mae padrao matx atx', 'Motherboard', 40, 25, 35, 45, null, 'published', 'migration'),
  ('ram_16gb', '16 GB DDR4/DDR5 (2 módulos)', '16 gb ddr4 ddr5 2 modulos', 'RAM', 10, 4, 7, 9, null, 'published', 'migration'),
  ('ram_32gb', '32 GB DDR4/DDR5 (2 módulos)', '32 gb ddr4 ddr5 2 modulos', 'RAM', 15, 6, 10, 14, null, 'published', 'migration'),
  ('ssd_nvme', 'SSD NVMe M.2 1TB', 'ssd nvme m 2 1tb', 'Storage', 7, 1, 4, 6, null, 'published', 'migration'),
  ('hdd_sata', 'Disco Rígido HDD 2TB', 'disco rigido hdd 2tb', 'Storage', 10, 4, 7, 8, null, 'published', 'migration'),
  ('mon_24_fhd', 'Monitor LED 24'''' Full HD', 'monitor led 24 full hd', 'Monitor', 25, 1, 20, 24, null, 'published', 'migration'),
  ('mon_27_qhd', 'Monitor Gamer 27'''' QHD 144Hz', 'monitor gamer 27 qhd 144hz', 'Monitor', 45, 1, 35, 42, null, 'published', 'migration'),
  ('periph_standard', 'Teclado, Mouse e Fans RGB', 'teclado mouse e fans rgb', 'Peripherals', 20, 8, 15, 20, null, 'published', 'migration')
on conflict (id) do update set
  name = excluded.name,
  normalized_name = excluded.normalized_name,
  category = excluded.category,
  tdp_watts = excluded.tdp_watts,
  idle_watts = excluded.idle_watts,
  typical_load_watts = excluded.typical_load_watts,
  gaming_load_watts = excluded.gaming_load_watts,
  description = excluded.description,
  status = excluded.status,
  source = excluded.source;

insert into public.official_facts (id, title, normalized_title, body, status, source) values
  ('fact_1', 'Potência x Consumo de Energia', 'potencia x consumo de energia', 'Potência é medida em Watts (W) e indica a demanda instantânea do aparelho. Já a energia consumida é medida em kWh (quilowatt-hora), que é a potência multiplicada pelo tempo de uso.', 'published', 'migration'),
  ('fact_2', 'O Chuveiro Elétrico e a Potência', 'o chuveiro eletrico e a potencia', 'Um chuveiro elétrico pode ter potência entre 4.500 W e 7.500 W. Reduzir o tempo no banho em apenas 5 minutos diários pode poupar dezenas de reais na conta de luz ao final do mês.', 'published', 'migration'),
  ('fact_3', 'Consumo Fantasma (Stand-by)', 'consumo fantasma stand by', 'Aparelhos mantidos em modo stand-by (com a luzinha vermelha acesa) continuam consumindo entre 1 W e 15 W cada um. Em uma casa média, o stand-by pode representar até 12% da conta!', 'published', 'migration'),
  ('fact_4', 'A Revolução do LED', 'a revolucao do led', 'Uma lâmpada LED consome cerca de 9 W a 10 W para iluminar o mesmo que uma antiga lâmpada incandescente de 60 W. Isso representa uma economia direta de mais de 80% na iluminação.', 'published', 'migration'),
  ('fact_5', 'Geladeiras e Troca de Calor', 'geladeiras e troca de calor', 'Evitar guardar alimentos ainda quentes na geladeira e manter as borrachas de vedação limpas reduz o esforço do compressor, economizando energia e prolongando a vida útil do motor.', 'published', 'migration'),
  ('fact_6', 'PC Gamer e Carga de Trabalho', 'pc gamer e carga de trabalho', 'Um computador não consome a potência máxima da fonte o tempo todo. Navegando na web ou estudando, o consumo costuma ficar abaixo de 60 W. Em jogos pesados, a GPU e a CPU exigem muito mais energia.', 'published', 'migration')
on conflict (id) do update set
  title = excluded.title,
  normalized_title = excluded.normalized_title,
  body = excluded.body,
  status = excluded.status,
  source = excluded.source;

insert into public.official_presets (id, name, normalized_name, description, status, source) values
  ('casa_tipica', 'Casa Típica Brasileira (Família de 3 a 4 pessoas)', 'casa tipica brasileira familia de 3 a 4 pessoas', 'Simulação com uso equilibrado de chuveiro elétrico, geladeira contínua, TV e máquina de lavar.', 'published', 'migration'),
  ('casa_sustentavel', 'Casa Eficiente e Sustentável', 'casa eficiente e sustentavel', 'Foco em banhos curtos, iluminação LED de alta eficiência, ventilador em vez de AC e eletrodomésticos inverter.', 'published', 'migration'),
  ('quarto_gamer', 'Quarto Conectado & Gamer', 'quarto conectado gamer', 'Foco em tecnologia com PC gamer potente de muitas horas, monitor gamer e ar-condicionado.', 'published', 'migration')
on conflict (id) do update set
  name = excluded.name,
  normalized_name = excluded.normalized_name,
  description = excluded.description,
  status = excluded.status,
  source = excluded.source;

insert into public.official_preset_items (id, preset_id, name, category, power_watts, hours_per_day, days_per_month, snapshot) values
  ('shower_preset', 'casa_tipica', 'Chuveiro Elétrico (Família)', 'Banheiro', 5500, 0.8, 30, '{"id": "shower_preset", "name": "Chuveiro Elétrico (Família)", "category": "Banheiro", "power_watts": 5500, "hours_per_day": 0.8, "days_per_month": 30}'::jsonb),
  ('fridge_preset', 'casa_tipica', 'Geladeira Frost Free', 'Cozinha', 150, 12.0, 30, '{"id": "fridge_preset", "name": "Geladeira Frost Free", "category": "Cozinha", "power_watts": 150, "hours_per_day": 12.0, "days_per_month": 30}'::jsonb),
  ('tv_preset', 'casa_tipica', 'Smart TV Sala', 'Sala', 100, 5.0, 30, '{"id": "tv_preset", "name": "Smart TV Sala", "category": "Sala", "power_watts": 100, "hours_per_day": 5.0, "days_per_month": 30}'::jsonb),
  ('led_preset', 'casa_tipica', 'Iluminação LED Geral', 'Iluminação', 60, 6.0, 30, '{"id": "led_preset", "name": "Iluminação LED Geral", "category": "Iluminação", "power_watts": 60, "hours_per_day": 6.0, "days_per_month": 30}'::jsonb),
  ('washer_preset', 'casa_tipica', 'Máquina de Lavar', 'Lavanderia', 500, 1.5, 12, '{"id": "washer_preset", "name": "Máquina de Lavar", "category": "Lavanderia", "power_watts": 500, "hours_per_day": 1.5, "days_per_month": 12}'::jsonb),
  ('fan_preset', 'casa_tipica', 'Ventilador', 'Climatização', 80, 6.0, 25, '{"id": "fan_preset", "name": "Ventilador", "category": "Climatização", "power_watts": 80, "hours_per_day": 6.0, "days_per_month": 25}'::jsonb),
  ('shower_eco', 'casa_sustentavel', 'Chuveiro Elétrico (Banhos curtos 5min)', 'Banheiro', 4500, 0.35, 30, '{"id": "shower_eco", "name": "Chuveiro Elétrico (Banhos curtos 5min)", "category": "Banheiro", "power_watts": 4500, "hours_per_day": 0.35, "days_per_month": 30}'::jsonb),
  ('fridge_eco', 'casa_sustentavel', 'Geladeira Inverter Classe A+++', 'Cozinha', 100, 10.0, 30, '{"id": "fridge_eco", "name": "Geladeira Inverter Classe A+++", "category": "Cozinha", "power_watts": 100, "hours_per_day": 10.0, "days_per_month": 30}'::jsonb),
  ('led_eco', 'casa_sustentavel', 'Lâmpadas LED Eficientes', 'Iluminação', 35, 4.0, 30, '{"id": "led_eco", "name": "Lâmpadas LED Eficientes", "category": "Iluminação", "power_watts": 35, "hours_per_day": 4.0, "days_per_month": 30}'::jsonb),
  ('tv_eco', 'casa_sustentavel', 'Smart TV LED', 'Sala', 75, 3.0, 30, '{"id": "tv_eco", "name": "Smart TV LED", "category": "Sala", "power_watts": 75, "hours_per_day": 3.0, "days_per_month": 30}'::jsonb),
  ('fan_eco', 'casa_sustentavel', 'Ventilador Eficiente', 'Climatização', 60, 4.0, 20, '{"id": "fan_eco", "name": "Ventilador Eficiente", "category": "Climatização", "power_watts": 60, "hours_per_day": 4.0, "days_per_month": 20}'::jsonb),
  ('pc_gamer_preset', 'quarto_gamer', 'Computador Desktop Gamer Completo', 'Tecnologia', 380, 6.0, 30, '{"id": "pc_gamer_preset", "name": "Computador Desktop Gamer Completo", "category": "Tecnologia", "power_watts": 380, "hours_per_day": 6.0, "days_per_month": 30}'::jsonb),
  ('ac_quarto', 'quarto_gamer', 'Ar-Condicionado Quarto', 'Climatização', 900, 7.0, 25, '{"id": "ac_quarto", "name": "Ar-Condicionado Quarto", "category": "Climatização", "power_watts": 900, "hours_per_day": 7.0, "days_per_month": 25}'::jsonb),
  ('mon_preset', 'quarto_gamer', 'Monitor Gamer 144Hz', 'Tecnologia', 40, 6.0, 30, '{"id": "mon_preset", "name": "Monitor Gamer 144Hz", "category": "Tecnologia", "power_watts": 40, "hours_per_day": 6.0, "days_per_month": 30}'::jsonb),
  ('led_rgb', 'quarto_gamer', 'Iluminação Ambiente / Fitas LED', 'Iluminação', 30, 8.0, 30, '{"id": "led_rgb", "name": "Iluminação Ambiente / Fitas LED", "category": "Iluminação", "power_watts": 30, "hours_per_day": 8.0, "days_per_month": 30}'::jsonb)
on conflict (id) do update set
  preset_id = excluded.preset_id,
  name = excluded.name,
  category = excluded.category,
  power_watts = excluded.power_watts,
  hours_per_day = excluded.hours_per_day,
  days_per_month = excluded.days_per_month,
  snapshot = excluded.snapshot;

insert into public.event_quizzes (id, event_key, title, enabled, reward_enabled) values
  ('11111111-1111-4111-8111-111111111111', 'ecowatt-quiz-basics-2026', 'Desafio EcoWatt: fundamentos de energia', false, false)
on conflict (id) do update set
  event_key = excluded.event_key,
  title = excluded.title,
  enabled = excluded.enabled,
  reward_enabled = excluded.reward_enabled;

insert into public.quiz_questions (id, quiz_id, prompt, explanation, options, correct_option, status) values
  ('22222222-2222-4222-8222-222222222221', '11111111-1111-4111-8111-111111111111', 'O que o kWh mede?', 'kWh combina potencia e tempo para representar energia consumida.', '["Energia consumida", "Potencia instantanea", "Tensao"]'::jsonb, 0, 'published'),
  ('22222222-2222-4222-8222-222222222222', '11111111-1111-4111-8111-111111111111', 'Qual unidade mede potencia?', 'Watt mede a potencia instantanea de um aparelho.', '["Watt (W)", "Quilowatt-hora (kWh)", "Litro"]'::jsonb, 0, 'published'),
  ('22222222-2222-4222-8222-222222222223', '11111111-1111-4111-8111-111111111111', 'O que ajuda a reduzir consumo em stand-by?', 'Retirar aparelhos da tomada evita consumo quando nao estao em uso.', '["Desligar da tomada", "Aumentar o brilho", "Deixar a luz acesa"]'::jsonb, 0, 'published')
on conflict (id) do update set
  quiz_id = excluded.quiz_id,
  prompt = excluded.prompt,
  explanation = excluded.explanation,
  options = excluded.options,
  correct_option = excluded.correct_option,
  status = excluded.status;

commit;
```

## Verificacao

```sql
select 'official_appliances' as table_name, count(*) as rows from public.official_appliances
union all select 'official_pc_components', count(*) from public.official_pc_components
union all select 'official_facts', count(*) from public.official_facts
union all select 'official_presets', count(*) from public.official_presets
union all select 'official_preset_items', count(*) from public.official_preset_items
union all select 'event_quizzes', count(*) from public.event_quizzes
union all select 'quiz_questions', count(*) from public.quiz_questions
order by table_name;
```
